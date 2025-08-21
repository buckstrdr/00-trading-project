"""
Strategy Registry for Managing Pluggable Strategies
"""
import os
import importlib
import inspect
from typing import Dict, Type, List, Optional
from pathlib import Path
from shared.strategy_interface import StrategyInterface, StrategyConfig

class StrategyRegistry:
    """Registry for managing pluggable trading strategies"""
    
    def __init__(self):
        self._strategies: Dict[str, Type[StrategyInterface]] = {}
        self._strategy_configs: Dict[str, dict] = {}
        self.strategies_dir = Path(__file__).parent.parent / "strategies"
        
    def register_strategy(self, strategy_class: Type[StrategyInterface], 
                         config: Optional[dict] = None):
        """Register a strategy class"""
        if not issubclass(strategy_class, StrategyInterface):
            raise ValueError(f"Strategy {strategy_class.__name__} must inherit from StrategyInterface")
        
        strategy_name = strategy_class.__name__
        self._strategies[strategy_name] = strategy_class
        
        if config:
            self._strategy_configs[strategy_name] = config
            
        print(f"Registered strategy: {strategy_name}")
    
    def get_strategy(self, name: str) -> Optional[Type[StrategyInterface]]:
        """Get strategy class by name"""
        return self._strategies.get(name)
    
    def get_strategy_config(self, name: str) -> Optional[dict]:
        """Get strategy configuration by name"""
        return self._strategy_configs.get(name)
    
    def list_strategies(self) -> List[str]:
        """List all registered strategy names"""
        return list(self._strategies.keys())
    
    def create_strategy(self, name: str, config: Optional[StrategyConfig] = None, 
                       **kwargs) -> Optional[StrategyInterface]:
        """Create strategy instance"""
        strategy_class = self.get_strategy(name)
        if not strategy_class:
            raise ValueError(f"Strategy '{name}' not found. Available: {self.list_strategies()}")
        
        # Use default config if none provided
        if config is None:
            default_config = self.get_strategy_config(name) or {}
            config = StrategyConfig(**default_config)
        
        return strategy_class(config=config, **kwargs)
    
    def discover_strategies(self, strategies_path: Optional[Path] = None):
        """Automatically discover and register strategies from directory"""
        if strategies_path is None:
            strategies_path = self.strategies_dir
            
        if not strategies_path.exists():
            print(f"Strategies directory not found: {strategies_path}")
            return
            
        print(f"Discovering strategies in: {strategies_path}")
        
        # Walk through strategies directory
        for strategy_dir in strategies_path.iterdir():
            if strategy_dir.is_dir() and not strategy_dir.name.startswith('_'):
                self._discover_strategy_in_directory(strategy_dir)
    
    def _discover_strategy_in_directory(self, strategy_dir: Path):
        """Discover strategy in specific directory"""
        # Look for Python files that might contain strategies
        for py_file in strategy_dir.glob("*.py"):
            if py_file.name.startswith('_'):
                continue
                
            try:
                # Import the module
                module_name = f"strategies.{strategy_dir.name}.{py_file.stem}"
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find strategy classes in the module
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, StrategyInterface) and 
                            obj != StrategyInterface):
                            
                            # Look for associated config file
                            config_file = strategy_dir / f"{py_file.stem}_config.yaml"
                            config = None
                            if config_file.exists():
                                config = self._load_yaml_config(config_file)
                            
                            self.register_strategy(obj, config)
                            break
                            
            except Exception as e:
                print(f"Failed to import strategy from {py_file}: {e}")
    
    def _load_yaml_config(self, config_file: Path) -> dict:
        """Load YAML configuration file"""
        try:
            import yaml
            with open(config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            print("PyYAML not installed, skipping YAML config loading")
            return {}
        except Exception as e:
            print(f"Failed to load config from {config_file}: {e}")
            return {}

# Global strategy registry instance
strategy_registry = StrategyRegistry()

def register_strategy(strategy_class: Type[StrategyInterface], config: Optional[dict] = None):
    """Decorator for registering strategies"""
    strategy_registry.register_strategy(strategy_class, config)
    return strategy_class