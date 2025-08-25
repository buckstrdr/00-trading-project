#!/usr/bin/env python3
"""
Backtest Scheduler - Phase 4A Implementation
TSX Strategy Bridge ML Optimization Framework

Purpose: Advanced scheduling and orchestration for systematic backtesting
- Time-based backtest scheduling
- Resource management and throttling
- Priority queuing for different backtest types
- Status monitoring and reporting
"""

import os
import sys
import json
import time
import datetime
import threading
import logging
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from queue import PriorityQueue, Queue
from dataclasses import dataclass, field
from enum import Enum
import uuid

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "ml"))


class BacktestPriority(Enum):
    """Priority levels for backtest scheduling"""
    URGENT = 1      # Immediate execution required
    HIGH = 2        # High priority, execute soon  
    NORMAL = 3      # Normal priority, standard queue
    LOW = 4         # Low priority, execute when resources available
    BATCH = 5       # Batch processing, lowest priority


class BacktestStatus(Enum):
    """Status tracking for scheduled backtests"""
    PENDING = "pending"
    QUEUED = "queued" 
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class BacktestJob:
    """Represents a scheduled backtest job"""
    job_id: str
    symbol: str
    strategy: str
    start_date: str
    end_date: str
    parameters: Dict[str, Any]
    priority: BacktestPriority = BacktestPriority.NORMAL
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    scheduled_for: Optional[datetime.datetime] = None
    timeout_seconds: int = 300  # 5 minute default timeout
    retry_count: int = 0
    max_retries: int = 3
    status: BacktestStatus = BacktestStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_start: Optional[datetime.datetime] = None
    execution_end: Optional[datetime.datetime] = None
    
    def __lt__(self, other):
        """Enable priority queue ordering"""
        if not isinstance(other, BacktestJob):
            return NotImplemented
        # Lower priority value = higher priority in queue
        return self.priority.value < other.priority.value
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'job_id': self.job_id,
            'symbol': self.symbol,
            'strategy': self.strategy,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'parameters': self.parameters,
            'priority': self.priority.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'timeout_seconds': self.timeout_seconds,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'status': self.status.value,
            'result': self.result,
            'error_message': self.error_message,
            'execution_start': self.execution_start.isoformat() if self.execution_start else None,
            'execution_end': self.execution_end.isoformat() if self.execution_end else None
        }


class ResourceManager:
    """Manage computational resources for backtest execution"""
    
    def __init__(self, max_concurrent_jobs: int = 4, max_cpu_percent: float = 80.0):
        self.max_concurrent_jobs = max_concurrent_jobs
        self.max_cpu_percent = max_cpu_percent
        self.running_jobs = {}  # job_id -> thread
        self.resource_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
    def can_start_job(self) -> bool:
        """Check if resources are available to start a new job"""
        with self.resource_lock:
            current_jobs = len([j for j in self.running_jobs.values() if j.is_alive()])
            return current_jobs < self.max_concurrent_jobs
            
    def register_job(self, job_id: str, thread: threading.Thread):
        """Register a running job"""
        with self.resource_lock:
            self.running_jobs[job_id] = thread
            
    def unregister_job(self, job_id: str):
        """Unregister a completed job"""
        with self.resource_lock:
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]
                
    def get_resource_status(self) -> Dict[str, Any]:
        """Get current resource utilization"""
        with self.resource_lock:
            active_jobs = [j for j in self.running_jobs.values() if j.is_alive()]
            return {
                'active_jobs': len(active_jobs),
                'max_concurrent_jobs': self.max_concurrent_jobs,
                'resource_utilization': len(active_jobs) / self.max_concurrent_jobs,
                'available_slots': self.max_concurrent_jobs - len(active_jobs)
            }


class BacktestScheduler:
    """Advanced scheduler for systematic backtest execution"""
    
    def __init__(self, max_workers: int = 4, persist_jobs: bool = True):
        self.max_workers = max_workers
        self.persist_jobs = persist_jobs
        self.logger = self._setup_logging()
        
        # Core components
        self.job_queue = PriorityQueue()
        self.completed_jobs = {}  # job_id -> BacktestJob
        self.resource_manager = ResourceManager(max_workers)
        
        # Scheduling state
        self.scheduler_running = False
        self.scheduler_thread = None
        self.job_executor_callback = None
        self.stats = {
            'jobs_scheduled': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'jobs_cancelled': 0,
            'total_execution_time': 0.0
        }
        
        # Persistence
        self.jobs_file = Path(project_root) / "ml" / "scheduled_jobs.json"
        if self.persist_jobs:
            self._load_persisted_jobs()
            
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for scheduler"""
        logger = logging.getLogger('BacktestScheduler')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def set_executor_callback(self, callback: Callable[[BacktestJob], Dict[str, Any]]):
        """Set the callback function for executing backtests"""
        self.job_executor_callback = callback
        
    def schedule_backtest(self, 
                         symbol: str,
                         strategy: str, 
                         start_date: str,
                         end_date: str,
                         parameters: Dict[str, Any],
                         priority: BacktestPriority = BacktestPriority.NORMAL,
                         scheduled_for: Optional[datetime.datetime] = None,
                         timeout_seconds: int = 300) -> str:
        """Schedule a new backtest job"""
        
        job_id = f"bt_{symbol}_{strategy}_{uuid.uuid4().hex[:8]}"
        
        job = BacktestJob(
            job_id=job_id,
            symbol=symbol,
            strategy=strategy,
            start_date=start_date,
            end_date=end_date,
            parameters=parameters,
            priority=priority,
            scheduled_for=scheduled_for,
            timeout_seconds=timeout_seconds
        )
        
        # Add to queue
        self.job_queue.put(job)
        job.status = BacktestStatus.QUEUED
        self.stats['jobs_scheduled'] += 1
        
        self.logger.info(f"Scheduled backtest: {job_id} ({symbol}-{strategy}) Priority: {priority.name}")
        
        if self.persist_jobs:
            self._persist_job(job)
            
        return job_id
        
    def schedule_batch_backtests(self, 
                                jobs: List[Dict[str, Any]], 
                                priority: BacktestPriority = BacktestPriority.BATCH) -> List[str]:
        """Schedule multiple backtests as a batch"""
        
        job_ids = []
        
        for job_config in jobs:
            job_id = self.schedule_backtest(
                symbol=job_config['symbol'],
                strategy=job_config['strategy'],
                start_date=job_config['start_date'],
                end_date=job_config['end_date'],
                parameters=job_config.get('parameters', {}),
                priority=priority,
                timeout_seconds=job_config.get('timeout_seconds', 300)
            )
            job_ids.append(job_id)
            
        self.logger.info(f"Scheduled batch of {len(job_ids)} backtests")
        return job_ids
        
    def start_scheduler(self):
        """Start the background scheduler"""
        if self.scheduler_running:
            self.logger.warning("Scheduler already running")
            return
            
        if not self.job_executor_callback:
            raise ValueError("Job executor callback not set. Use set_executor_callback()")
            
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Backtest scheduler started")
        
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5.0)
        self.logger.info("Backtest scheduler stopped")
        
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.scheduler_running:
            try:
                # Check if we can start new jobs
                if not self.resource_manager.can_start_job():
                    time.sleep(1.0)
                    continue
                    
                # Get next job from queue (blocks briefly)
                try:
                    job = self.job_queue.get(timeout=1.0)
                except:
                    continue  # No jobs available, continue loop
                    
                # Check if job should be executed now
                if job.scheduled_for and datetime.datetime.now() < job.scheduled_for:
                    # Put job back in queue for later
                    self.job_queue.put(job)
                    time.sleep(1.0)
                    continue
                    
                # Execute job in separate thread
                job.status = BacktestStatus.RUNNING
                job.execution_start = datetime.datetime.now()
                
                execution_thread = threading.Thread(
                    target=self._execute_job,
                    args=(job,),
                    daemon=True
                )
                
                self.resource_manager.register_job(job.job_id, execution_thread)
                execution_thread.start()
                
                self.logger.info(f"Started execution: {job.job_id}")
                
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                time.sleep(1.0)
                
    def _execute_job(self, job: BacktestJob):
        """Execute a backtest job"""
        try:
            # Execute the backtest using callback
            result = self.job_executor_callback(job)
            
            # Update job with result
            job.execution_end = datetime.datetime.now()
            
            if result and result.get('success', False):
                job.status = BacktestStatus.COMPLETED
                job.result = result
                self.stats['jobs_completed'] += 1
                
                execution_time = (job.execution_end - job.execution_start).total_seconds()
                self.stats['total_execution_time'] += execution_time
                
                self.logger.info(f"Completed job: {job.job_id} ({execution_time:.2f}s)")
            else:
                job.status = BacktestStatus.FAILED
                job.error_message = result.get('error', 'Unknown error') if result else 'No result returned'
                self.stats['jobs_failed'] += 1
                
                self.logger.error(f"Job failed: {job.job_id} - {job.error_message}")
                
                # Check if we should retry
                if job.retry_count < job.max_retries:
                    job.retry_count += 1
                    job.status = BacktestStatus.QUEUED
                    job.execution_start = None
                    job.execution_end = None
                    
                    # Re-queue with delay
                    time.sleep(2.0)  # Brief delay before retry
                    self.job_queue.put(job)
                    
                    self.logger.info(f"Re-queued job for retry: {job.job_id} (attempt {job.retry_count})")
                    
        except Exception as e:
            job.status = BacktestStatus.FAILED
            job.error_message = str(e)
            job.execution_end = datetime.datetime.now()
            self.stats['jobs_failed'] += 1
            
            self.logger.error(f"Exception in job execution {job.job_id}: {e}")
            
        finally:
            # Always unregister job and store result
            self.resource_manager.unregister_job(job.job_id)
            self.completed_jobs[job.job_id] = job
            
            if self.persist_jobs:
                self._persist_job(job)
                
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job"""
        if job_id in self.completed_jobs:
            return self.completed_jobs[job_id].to_dict()
        return None
        
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue and scheduler status"""
        resource_status = self.resource_manager.get_resource_status()
        
        return {
            'scheduler_running': self.scheduler_running,
            'jobs_in_queue': self.job_queue.qsize(),
            'completed_jobs': len(self.completed_jobs),
            'resource_status': resource_status,
            'statistics': self.stats.copy(),
            'average_execution_time': (
                self.stats['total_execution_time'] / max(1, self.stats['jobs_completed'])
            )
        }
        
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job"""
        # Note: This is a simplified implementation
        # In a full implementation, we'd need to track queued jobs better
        if job_id in self.completed_jobs:
            job = self.completed_jobs[job_id]
            if job.status in [BacktestStatus.PENDING, BacktestStatus.QUEUED]:
                job.status = BacktestStatus.CANCELLED
                self.stats['jobs_cancelled'] += 1
                return True
        return False
        
    def _persist_job(self, job: BacktestJob):
        """Persist job to disk"""
        try:
            # Load existing jobs
            jobs_data = []
            if self.jobs_file.exists():
                with open(self.jobs_file, 'r') as f:
                    jobs_data = json.load(f)
                    
            # Update or add job
            job_dict = job.to_dict()
            updated = False
            
            for i, existing_job in enumerate(jobs_data):
                if existing_job['job_id'] == job.job_id:
                    jobs_data[i] = job_dict
                    updated = True
                    break
                    
            if not updated:
                jobs_data.append(job_dict)
                
            # Save back to file
            self.jobs_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.jobs_file, 'w') as f:
                json.dump(jobs_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to persist job {job.job_id}: {e}")
            
    def _load_persisted_jobs(self):
        """Load persisted jobs from disk"""
        if not self.jobs_file.exists():
            return
            
        try:
            with open(self.jobs_file, 'r') as f:
                jobs_data = json.load(f)
                
            for job_dict in jobs_data:
                if job_dict.get('status') == BacktestStatus.COMPLETED.value:
                    # Reconstruct completed job
                    job = BacktestJob(
                        job_id=job_dict['job_id'],
                        symbol=job_dict['symbol'],
                        strategy=job_dict['strategy'],
                        start_date=job_dict['start_date'],
                        end_date=job_dict['end_date'],
                        parameters=job_dict['parameters']
                    )
                    
                    # Restore state
                    job.status = BacktestStatus(job_dict['status'])
                    job.result = job_dict.get('result')
                    job.error_message = job_dict.get('error_message')
                    
                    if job_dict.get('created_at'):
                        job.created_at = datetime.datetime.fromisoformat(job_dict['created_at'])
                    if job_dict.get('execution_start'):
                        job.execution_start = datetime.datetime.fromisoformat(job_dict['execution_start'])
                    if job_dict.get('execution_end'):
                        job.execution_end = datetime.datetime.fromisoformat(job_dict['execution_end'])
                        
                    self.completed_jobs[job.job_id] = job
                    
            self.logger.info(f"Loaded {len(self.completed_jobs)} persisted jobs")
            
        except Exception as e:
            self.logger.error(f"Failed to load persisted jobs: {e}")


def main():
    """Test the scheduler functionality"""
    print("=== Backtest Scheduler Test ===")
    
    # Create scheduler
    scheduler = BacktestScheduler(max_workers=2)
    
    # Mock executor function for testing
    def mock_executor(job: BacktestJob) -> Dict[str, Any]:
        """Mock backtest executor"""
        print(f"Executing mock backtest: {job.symbol}-{job.strategy}")
        
        # Simulate execution time
        time.sleep(2.0)
        
        # Return mock result
        return {
            'success': True,
            'total_trades': 100,
            'win_rate': 45.0,
            'total_pnl': 150.0
        }
    
    # Set executor
    scheduler.set_executor_callback(mock_executor)
    
    # Schedule some test jobs
    job_ids = []
    for symbol in ['MCL', 'MES']:
        for strategy in ['EMA_CROSS', 'ORB_RUBBER_BAND']:
            job_id = scheduler.schedule_backtest(
                symbol=symbol,
                strategy=strategy,
                start_date='2023-08-01',
                end_date='2023-08-31',
                parameters={'test_param': 123},
                priority=BacktestPriority.NORMAL
            )
            job_ids.append(job_id)
            
    print(f"Scheduled {len(job_ids)} jobs")
    
    # Start scheduler
    scheduler.start_scheduler()
    
    # Monitor progress
    for i in range(20):  # Monitor for 20 seconds max
        status = scheduler.get_queue_status()
        print(f"Queue status: {status['jobs_in_queue']} pending, {status['completed_jobs']} completed")
        
        if status['completed_jobs'] >= len(job_ids):
            break
            
        time.sleep(1.0)
        
    # Stop scheduler
    scheduler.stop_scheduler()
    
    # Show final results
    final_status = scheduler.get_queue_status()
    print(f"\nFinal status: {final_status}")
    
    for job_id in job_ids:
        job_status = scheduler.get_job_status(job_id)
        if job_status:
            print(f"Job {job_id}: {job_status['status']} - {job_status.get('result', {}).get('total_trades', 'N/A')} trades")


if __name__ == "__main__":
    main()