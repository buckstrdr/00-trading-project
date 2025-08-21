"""
Database connection and session management for PDH/PDL strategy.
"""

import os
import logging
from typing import Generator, Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

from .models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection and session manager."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize database manager with connection URL."""
        self.database_url = database_url or self._get_database_url()
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        
    def _get_database_url(self) -> str:
        """Get database URL from environment or use SQLite for testing."""
        # Check for PostgreSQL environment variables
        pg_url = os.getenv('DATABASE_URL')
        if pg_url:
            return pg_url
        
        # Build PostgreSQL URL from individual components
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '5432')
        database = os.getenv('DB_NAME', 'pdh_pdl_strategy')
        username = os.getenv('DB_USER', 'postgres')
        password = os.getenv('DB_PASSWORD', 'password')
        
        if all([host, port, database, username, password]):
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"
        
        # Fallback to SQLite for development/testing
        sqlite_path = os.path.join(os.getcwd(), 'data', 'strategy.db')
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
        logger.warning(f"Using SQLite database at: {sqlite_path}")
        return f"sqlite:///{sqlite_path}"
    
    def initialize(self) -> bool:
        """Initialize database engine and session factory."""
        try:
            # Create engine with connection pooling
            if self.database_url.startswith('postgresql'):
                self.engine = create_engine(
                    self.database_url,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
                    echo=False
                )
            else:  # SQLite
                self.engine = create_engine(
                    self.database_url,
                    echo=False,
                    connect_args={"check_same_thread": False}
                )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False
            )
            
            # Test connection
            with self.engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("SELECT 1"))
            
            logger.info(f"Database initialized successfully: {self.database_url.split('@')[0]}@***")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize database: {e}")
            return False
    
    def create_tables(self) -> bool:
        """Create all tables if they don't exist."""
        try:
            if self.engine is None:
                raise RuntimeError("Database engine not initialized")
            
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to create tables: {e}")
            return False
    
    def drop_tables(self) -> bool:
        """Drop all tables (use with caution)."""
        try:
            if self.engine is None:
                raise RuntimeError("Database engine not initialized")
            
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to drop tables: {e}")
            return False
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup."""
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized")
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def health_check(self) -> bool:
        """Check database connection health."""
        try:
            with self.get_session() as session:
                from sqlalchemy import text
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")


# Global database manager instance
db_manager = DatabaseManager()


def get_db_session() -> Generator[Session, None, None]:
    """Dependency for getting database session."""
    with db_manager.get_session() as session:
        yield session


def init_database() -> bool:
    """Initialize database for the application."""
    # Reinitialize db_manager to pick up environment changes
    global db_manager
    db_manager = DatabaseManager()
    
    if not db_manager.initialize():
        return False
    
    if not db_manager.create_tables():
        return False
    
    return True


def close_database():
    """Close database connections."""
    db_manager.close()