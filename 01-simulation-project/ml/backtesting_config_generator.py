#!/usr/bin/env python3
"""
Backtesting Configuration Generator - Phase 4A Implementation
TSX Strategy Bridge ML Optimization Framework

Purpose: Generate systematic parameter variations for ML training
- Parameter space exploration and optimization
- Smart parameter combination generation
- Configuration validation and testing
- Strategy-specific parameter handling
"""

import os
import sys
import json
import itertools
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import datetime
import random

# Add project paths
project_root = Path(__file__).parent.parent


class ParameterType(Enum):
    """Parameter type classifications for optimization"""
    INTEGER = "integer"      # Discrete integer values
    FLOAT = "float"         # Continuous float values
    BOOLEAN = "boolean"     # Binary true/false
    CATEGORICAL = "categorical"  # Discrete categorical choices
    RANGE = "range"         # Min/max range specification


class OptimizationMethod(Enum):
    """Methods for parameter optimization"""
    GRID_SEARCH = "grid_search"     # Exhaustive grid search
    RANDOM_SEARCH = "random_search" # Random sampling
    LATIN_HYPERCUBE = "latin_hypercube"  # Latin hypercube sampling
    GENETIC = "genetic"             # Genetic algorithm approach
    BAYESIAN = "bayesian"           # Bayesian optimization


@dataclass
class ParameterDefinition:
    """Definition of a strategy parameter for optimization"""
    name: str
    param_type: ParameterType
    default_value: Any
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    step_size: Optional[Union[int, float]] = None
    choices: Optional[List[Any]] = None
    description: str = ""
    is_critical: bool = True  # Whether parameter significantly affects performance
    
    def validate_value(self, value: Any) -> bool:
        """Validate if value is acceptable for this parameter"""
        try:
            if self.param_type == ParameterType.INTEGER:
                if not isinstance(value, (int, np.integer)):
                    return False
                if self.min_value is not None and value < self.min_value:
                    return False
                if self.max_value is not None and value > self.max_value:
                    return False
                    
            elif self.param_type == ParameterType.FLOAT:
                if not isinstance(value, (float, int, np.floating, np.integer)):
                    return False
                if self.min_value is not None and value < self.min_value:
                    return False
                if self.max_value is not None and value > self.max_value:
                    return False
                    
            elif self.param_type == ParameterType.BOOLEAN:
                if not isinstance(value, (bool, np.bool_)):
                    return False
                    
            elif self.param_type == ParameterType.CATEGORICAL:
                if self.choices and value not in self.choices:
                    return False
                    
            return True
            
        except Exception:
            return False
            
    def generate_values(self, count: int = 10, method: str = 'grid') -> List[Any]:
        """Generate parameter values for testing"""
        if method == 'grid':
            return self._generate_grid_values(count)
        elif method == 'random':
            return self._generate_random_values(count)
        else:
            return [self.default_value]
            
    def _generate_grid_values(self, count: int) -> List[Any]:
        """Generate grid-based parameter values"""
        if self.param_type == ParameterType.INTEGER:
            if self.min_value is not None and self.max_value is not None:
                step = max(1, (self.max_value - self.min_value) // count)
                return list(range(int(self.min_value), int(self.max_value) + 1, int(step)))
            else:
                return [self.default_value]
                
        elif self.param_type == ParameterType.FLOAT:
            if self.min_value is not None and self.max_value is not None:
                return list(np.linspace(self.min_value, self.max_value, count))
            else:
                return [self.default_value]
                
        elif self.param_type == ParameterType.BOOLEAN:
            return [True, False]
            
        elif self.param_type == ParameterType.CATEGORICAL:
            return self.choices[:count] if self.choices else [self.default_value]
            
        return [self.default_value]
        
    def _generate_random_values(self, count: int) -> List[Any]:
        """Generate random parameter values"""
        values = []
        
        for _ in range(count):
            if self.param_type == ParameterType.INTEGER:
                if self.min_value is not None and self.max_value is not None:
                    values.append(random.randint(int(self.min_value), int(self.max_value)))
                else:
                    values.append(self.default_value)
                    
            elif self.param_type == ParameterType.FLOAT:
                if self.min_value is not None and self.max_value is not None:
                    values.append(random.uniform(self.min_value, self.max_value))
                else:
                    values.append(self.default_value)
                    
            elif self.param_type == ParameterType.BOOLEAN:
                values.append(random.choice([True, False]))
                
            elif self.param_type == ParameterType.CATEGORICAL:
                if self.choices:
                    values.append(random.choice(self.choices))
                else:
                    values.append(self.default_value)
            else:
                values.append(self.default_value)
                
        return values


@dataclass
class StrategyConfiguration:
    """Complete configuration for a trading strategy"""
    strategy_name: str
    parameters: Dict[str, ParameterDefinition] = field(default_factory=dict)
    base_config: Dict[str, Any] = field(default_factory=dict)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)  # Parameter dependencies
    constraints: List[str] = field(default_factory=list)  # Configuration constraints
    
    def add_parameter(self, param_def: ParameterDefinition):
        """Add parameter definition to strategy"""
        self.parameters[param_def.name] = param_def
        
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a parameter configuration"""
        errors = []
        
        # Check all parameters are valid
        for param_name, param_def in self.parameters.items():
            if param_name in config:
                if not param_def.validate_value(config[param_name]):
                    errors.append(f"Invalid value for {param_name}: {config[param_name]}")
                    
        # Check dependencies
        for param_name, depends_on in self.dependencies.items():
            if param_name in config:
                for dep in depends_on:
                    if dep not in config:
                        errors.append(f"Parameter {param_name} requires {dep} to be set")
                        
        # TODO: Add constraint validation
        
        return len(errors) == 0, errors


class BacktestingConfigGenerator:
    """Generate systematic parameter configurations for backtesting"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.strategy_configs = {}
        self._initialize_strategy_definitions()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger('ConfigGenerator')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def _initialize_strategy_definitions(self):
        """Initialize parameter definitions for all strategies"""
        
        # EMA Cross Strategy Configuration
        ema_config = StrategyConfiguration("EMA_CROSS")
        ema_config.add_parameter(ParameterDefinition(
            name="fast_period",
            param_type=ParameterType.INTEGER,
            default_value=10,
            min_value=3,
            max_value=50,
            step_size=1,
            description="Fast EMA period",
            is_critical=True
        ))
        ema_config.add_parameter(ParameterDefinition(
            name="slow_period", 
            param_type=ParameterType.INTEGER,
            default_value=20,
            min_value=10,
            max_value=200,
            step_size=5,
            description="Slow EMA period",
            is_critical=True
        ))
        ema_config.add_parameter(ParameterDefinition(
            name="risk_per_trade",
            param_type=ParameterType.FLOAT,
            default_value=50.0,
            min_value=10.0,
            max_value=200.0,
            step_size=10.0,
            description="Risk amount per trade",
            is_critical=True
        ))
        ema_config.add_parameter(ParameterDefinition(
            name="stop_loss_pct",
            param_type=ParameterType.FLOAT,
            default_value=2.0,
            min_value=0.5,
            max_value=5.0,
            step_size=0.25,
            description="Stop loss percentage",
            is_critical=False
        ))
        
        # Add dependency: slow_period must be greater than fast_period
        ema_config.dependencies["slow_period"] = ["fast_period"]
        
        self.strategy_configs["EMA_CROSS"] = ema_config
        
        # ORB Rubber Band Strategy Configuration
        orb_config = StrategyConfiguration("ORB_RUBBER_BAND")
        orb_config.add_parameter(ParameterDefinition(
            name="orb_period_minutes",
            param_type=ParameterType.INTEGER,
            default_value=30,
            min_value=15,
            max_value=120,
            step_size=15,
            description="Opening range period in minutes",
            is_critical=True
        ))
        orb_config.add_parameter(ParameterDefinition(
            name="rubber_band_pct",
            param_type=ParameterType.FLOAT,
            default_value=0.5,
            min_value=0.1,
            max_value=2.0,
            step_size=0.1,
            description="Rubber band retracement percentage",
            is_critical=True
        ))
        orb_config.add_parameter(ParameterDefinition(
            name="breakout_confirmation",
            param_type=ParameterType.BOOLEAN,
            default_value=True,
            description="Require breakout confirmation",
            is_critical=False
        ))
        orb_config.add_parameter(ParameterDefinition(
            name="risk_per_trade",
            param_type=ParameterType.FLOAT,
            default_value=50.0,
            min_value=10.0,
            max_value=200.0,
            step_size=10.0,
            description="Risk amount per trade",
            is_critical=True
        ))
        
        self.strategy_configs["ORB_RUBBER_BAND"] = orb_config
        
        # Test Time Strategy Configuration
        test_config = StrategyConfiguration("TEST_TIME_STRATEGY")
        test_config.add_parameter(ParameterDefinition(
            name="interval_minutes",
            param_type=ParameterType.INTEGER,
            default_value=5,
            min_value=1,
            max_value=30,
            choices=[1, 2, 3, 5, 10, 15, 30],
            description="Trading interval in minutes",
            is_critical=True
        ))
        test_config.add_parameter(ParameterDefinition(
            name="hold_minutes",
            param_type=ParameterType.INTEGER,
            default_value=3,
            min_value=1,
            max_value=60,
            step_size=1,
            description="Hold period in minutes",
            is_critical=True
        ))
        test_config.add_parameter(ParameterDefinition(
            name="direction_method",
            param_type=ParameterType.CATEGORICAL,
            default_value="previous_candle",
            choices=["previous_candle", "random", "momentum", "mean_reversion"],
            description="Method to determine trade direction",
            is_critical=True
        ))
        test_config.add_parameter(ParameterDefinition(
            name="risk_per_trade",
            param_type=ParameterType.FLOAT,
            default_value=50.0,
            min_value=10.0,
            max_value=200.0,
            step_size=10.0,
            description="Risk amount per trade",
            is_critical=True
        ))
        
        # Add constraint: hold_minutes should be less than interval_minutes
        test_config.constraints.append("hold_minutes < interval_minutes")
        
        self.strategy_configs["TEST_TIME_STRATEGY"] = test_config
        
        # PDH/PDL Comprehensive Strategy Configuration  
        pdhpdl_config = StrategyConfiguration("PDHPDL_COMPREHENSIVE")
        pdhpdl_config.add_parameter(ParameterDefinition(
            name="lookback_days",
            param_type=ParameterType.INTEGER,
            default_value=1,
            min_value=1,
            max_value=5,
            step_size=1,
            description="Days to look back for PDH/PDL",
            is_critical=True
        ))
        pdhpdl_config.add_parameter(ParameterDefinition(
            name="breakout_threshold_pct",
            param_type=ParameterType.FLOAT,
            default_value=0.1,
            min_value=0.01,
            max_value=1.0,
            step_size=0.01,
            description="Breakout threshold percentage",
            is_critical=True
        ))
        pdhpdl_config.add_parameter(ParameterDefinition(
            name="session_filter",
            param_type=ParameterType.BOOLEAN,
            default_value=True,
            description="Filter trades by session time",
            is_critical=False
        ))
        pdhpdl_config.add_parameter(ParameterDefinition(
            name="risk_per_trade",
            param_type=ParameterType.FLOAT,
            default_value=50.0,
            min_value=10.0,
            max_value=200.0,
            step_size=10.0,
            description="Risk amount per trade",
            is_critical=True
        ))
        
        self.strategy_configs["PDHPDL_COMPREHENSIVE"] = pdhpdl_config
        
        self.logger.info(f"Initialized {len(self.strategy_configs)} strategy configurations")
        
    def get_strategy_config(self, strategy_name: str) -> Optional[StrategyConfiguration]:
        """Get configuration for a specific strategy"""
        return self.strategy_configs.get(strategy_name)
        
    def generate_parameter_combinations(self,
                                      strategy_name: str,
                                      method: OptimizationMethod = OptimizationMethod.GRID_SEARCH,
                                      max_combinations: int = 100,
                                      focus_critical: bool = True) -> List[Dict[str, Any]]:
        """
        Generate parameter combinations for strategy optimization
        
        Args:
            strategy_name: Name of strategy to optimize
            method: Optimization method to use
            max_combinations: Maximum number of combinations to generate
            focus_critical: Whether to focus on critical parameters only
            
        Returns:
            List of parameter dictionaries
        """
        
        strategy_config = self.strategy_configs.get(strategy_name)
        if not strategy_config:
            self.logger.error(f"Strategy {strategy_name} not found")
            return []
            
        if method == OptimizationMethod.GRID_SEARCH:
            return self._generate_grid_combinations(strategy_config, max_combinations, focus_critical)
        elif method == OptimizationMethod.RANDOM_SEARCH:
            return self._generate_random_combinations(strategy_config, max_combinations, focus_critical)
        elif method == OptimizationMethod.LATIN_HYPERCUBE:
            return self._generate_latin_hypercube_combinations(strategy_config, max_combinations, focus_critical)
        else:
            self.logger.warning(f"Method {method} not implemented, using grid search")
            return self._generate_grid_combinations(strategy_config, max_combinations, focus_critical)
            
    def _generate_grid_combinations(self,
                                   strategy_config: StrategyConfiguration,
                                   max_combinations: int,
                                   focus_critical: bool) -> List[Dict[str, Any]]:
        """Generate grid-based parameter combinations"""
        
        # Select parameters to vary
        if focus_critical:
            param_names = [name for name, param_def in strategy_config.parameters.items() 
                          if param_def.is_critical]
        else:
            param_names = list(strategy_config.parameters.keys())
            
        if not param_names:
            return [strategy_config.base_config.copy()]
            
        # Calculate grid size per parameter
        grid_size_per_param = max(2, int(max_combinations ** (1/len(param_names))))
        
        # Generate values for each parameter
        param_value_sets = {}
        for param_name in param_names:
            param_def = strategy_config.parameters[param_name]
            param_value_sets[param_name] = param_def.generate_values(grid_size_per_param, 'grid')
            
        # Generate all combinations
        combinations = []
        param_names_list = list(param_value_sets.keys())
        param_values_list = list(param_value_sets.values())
        
        for combo in itertools.product(*param_values_list):
            config = strategy_config.base_config.copy()
            
            # Add varied parameters
            for i, param_name in enumerate(param_names_list):
                config[param_name] = combo[i]
                
            # Add default values for non-varied parameters
            for param_name, param_def in strategy_config.parameters.items():
                if param_name not in config:
                    config[param_name] = param_def.default_value
                    
            # Validate configuration
            is_valid, errors = strategy_config.validate_config(config)
            
            if is_valid:
                combinations.append(config)
                
            if len(combinations) >= max_combinations:
                break
                
        self.logger.info(f"Generated {len(combinations)} grid combinations for {strategy_config.strategy_name}")
        return combinations[:max_combinations]
        
    def _generate_random_combinations(self,
                                     strategy_config: StrategyConfiguration,
                                     max_combinations: int,
                                     focus_critical: bool) -> List[Dict[str, Any]]:
        """Generate random parameter combinations"""
        
        combinations = []
        
        # Select parameters to vary
        if focus_critical:
            vary_params = [name for name, param_def in strategy_config.parameters.items() 
                          if param_def.is_critical]
        else:
            vary_params = list(strategy_config.parameters.keys())
            
        for _ in range(max_combinations):
            config = strategy_config.base_config.copy()
            
            # Generate random values for selected parameters
            for param_name in vary_params:
                param_def = strategy_config.parameters[param_name]
                random_values = param_def.generate_values(1, 'random')
                config[param_name] = random_values[0]
                
            # Add default values for other parameters
            for param_name, param_def in strategy_config.parameters.items():
                if param_name not in config:
                    config[param_name] = param_def.default_value
                    
            # Validate configuration
            is_valid, errors = strategy_config.validate_config(config)
            
            if is_valid:
                combinations.append(config)
                
        self.logger.info(f"Generated {len(combinations)} random combinations for {strategy_config.strategy_name}")
        return combinations
        
    def _generate_latin_hypercube_combinations(self,
                                              strategy_config: StrategyConfiguration,
                                              max_combinations: int,
                                              focus_critical: bool) -> List[Dict[str, Any]]:
        """Generate Latin Hypercube sampled combinations"""
        # Simplified implementation - in production would use scipy.stats.qmc
        
        # For now, fall back to random sampling with better distribution
        combinations = []
        
        # Select parameters to vary
        if focus_critical:
            vary_params = [name for name, param_def in strategy_config.parameters.items() 
                          if param_def.is_critical]
        else:
            vary_params = list(strategy_config.parameters.keys())
            
        # Generate evenly distributed samples
        for i in range(max_combinations):
            config = strategy_config.base_config.copy()
            
            for param_name in vary_params:
                param_def = strategy_config.parameters[param_name]
                
                # Use more evenly distributed sampling
                if param_def.param_type == ParameterType.INTEGER:
                    if param_def.min_value is not None and param_def.max_value is not None:
                        # Evenly distribute across range
                        ratio = (i + 0.5) / max_combinations
                        value = int(param_def.min_value + ratio * (param_def.max_value - param_def.min_value))
                        config[param_name] = max(param_def.min_value, min(param_def.max_value, value))
                    else:
                        config[param_name] = param_def.default_value
                        
                elif param_def.param_type == ParameterType.FLOAT:
                    if param_def.min_value is not None and param_def.max_value is not None:
                        ratio = (i + 0.5) / max_combinations
                        value = param_def.min_value + ratio * (param_def.max_value - param_def.min_value)
                        config[param_name] = value
                    else:
                        config[param_name] = param_def.default_value
                        
                else:
                    # For categorical/boolean, use random
                    random_values = param_def.generate_values(1, 'random')
                    config[param_name] = random_values[0]
                    
            # Add defaults for other parameters
            for param_name, param_def in strategy_config.parameters.items():
                if param_name not in config:
                    config[param_name] = param_def.default_value
                    
            # Validate and add
            is_valid, errors = strategy_config.validate_config(config)
            if is_valid:
                combinations.append(config)
                
        self.logger.info(f"Generated {len(combinations)} Latin Hypercube combinations for {strategy_config.strategy_name}")
        return combinations
        
    def save_configurations(self, 
                           configurations: List[Dict[str, Any]], 
                           output_path: str = None,
                           strategy_name: str = "unknown") -> str:
        """Save generated configurations to file"""
        
        if not output_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = project_root / "ml" / f"config_{strategy_name}_{timestamp}.json"
            
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            output_data = {
                'strategy_name': strategy_name,
                'total_configurations': len(configurations),
                'generated_at': datetime.datetime.now().isoformat(),
                'configurations': configurations
            }
            
            with open(output_path, 'w') as f:
                json.dump(output_data, f, indent=2)
                
            self.logger.info(f"Saved {len(configurations)} configurations to {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save configurations: {e}")
            return ""
            
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get summary of all available optimization options"""
        
        summary = {
            'total_strategies': len(self.strategy_configs),
            'strategies': {},
            'optimization_methods': [method.value for method in OptimizationMethod]
        }
        
        for strategy_name, config in self.strategy_configs.items():
            param_info = {}
            critical_params = 0
            
            for param_name, param_def in config.parameters.items():
                param_info[param_name] = {
                    'type': param_def.param_type.value,
                    'default': param_def.default_value,
                    'critical': param_def.is_critical,
                    'description': param_def.description
                }
                
                if param_def.is_critical:
                    critical_params += 1
                    
            summary['strategies'][strategy_name] = {
                'total_parameters': len(config.parameters),
                'critical_parameters': critical_params,
                'parameters': param_info,
                'has_dependencies': len(config.dependencies) > 0,
                'has_constraints': len(config.constraints) > 0
            }
            
        return summary


def main():
    """Test the configuration generator"""
    print("=== Backtesting Configuration Generator Test ===")
    
    # Initialize generator
    generator = BacktestingConfigGenerator()
    
    # Show optimization summary
    summary = generator.get_optimization_summary()
    print(f"\nOptimization Summary:")
    print(f"- Total strategies: {summary['total_strategies']}")
    
    for strategy_name, strategy_info in summary['strategies'].items():
        print(f"- {strategy_name}: {strategy_info['total_parameters']} params ({strategy_info['critical_parameters']} critical)")
        
    # Generate configurations for EMA_CROSS strategy
    print(f"\nGenerating configurations for EMA_CROSS strategy...")
    
    ema_configs = generator.generate_parameter_combinations(
        strategy_name="EMA_CROSS",
        method=OptimizationMethod.GRID_SEARCH,
        max_combinations=20,
        focus_critical=True
    )
    
    print(f"Generated {len(ema_configs)} configurations")
    
    # Show sample configurations
    print(f"\nSample configurations:")
    for i, config in enumerate(ema_configs[:3]):
        print(f"  Config {i+1}: {config}")
        
    # Test random generation for TEST_TIME_STRATEGY
    print(f"\nGenerating random configurations for TEST_TIME_STRATEGY...")
    
    test_configs = generator.generate_parameter_combinations(
        strategy_name="TEST_TIME_STRATEGY",
        method=OptimizationMethod.RANDOM_SEARCH,
        max_combinations=10,
        focus_critical=True
    )
    
    print(f"Generated {len(test_configs)} random configurations")
    
    # Save configurations
    output_file = generator.save_configurations(ema_configs, strategy_name="EMA_CROSS")
    print(f"Saved configurations to: {output_file}")
    
    print(f"\nConfiguration generator test completed")


if __name__ == "__main__":
    main()