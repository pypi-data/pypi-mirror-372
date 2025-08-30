"""
Configuration management for layered-bias-probe.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager for the package."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file (Optional[str]): Path to custom config file
        """
        self.config_data = {}
        self._load_default_config()
        
        if config_file and os.path.exists(config_file):
            self._load_custom_config(config_file)
    
    def _load_default_config(self):
        """Load default configuration."""
        default_config_path = Path(__file__).parent / "default.yaml"
        
        try:
            with open(default_config_path, 'r') as f:
                self.config_data = yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load default config: {e}")
            self.config_data = self._get_fallback_config()
    
    def _load_custom_config(self, config_file: str):
        """Load custom configuration and merge with defaults."""
        try:
            with open(config_file, 'r') as f:
                custom_config = yaml.safe_load(f)
            
            # Merge custom config with defaults
            self._deep_merge(self.config_data, custom_config)
            
        except Exception as e:
            print(f"Warning: Could not load custom config {config_file}: {e}")
    
    def _deep_merge(self, base: Dict, update: Dict):
        """Deep merge two dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Get fallback configuration if default config fails to load."""
        return {
            "model": {
                "cache_dir": "./cache",
                "device_map": "auto",
                "torch_dtype": "float16",
                "quantization": True
            },
            "bias_analysis": {
                "default_languages": ["en"],
                "default_weat_categories": ["WEAT1", "WEAT2", "WEAT6"],
                "batch_size": 1
            },
            "fine_tuning": {
                "default_epochs": 5,
                "default_batch_size": 4,
                "default_learning_rate": 2e-5,
                "save_strategy": "epoch"
            },
            "output": {
                "results_format": "csv",
                "include_timestamp": True,
                "compression": False
            },
            "weathub": {
                "dataset_id": "iamshnoo/WEATHub",
                "trust_remote_code": True
            },
            "visualization": {
                "default_interactive": True,
                "save_plots": True,
                "plot_dpi": 300,
                "figure_width": 10,
                "figure_height": 6
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key (str): Configuration key (supports dot notation)
            default (Any): Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        keys = key.split('.')
        value = self.config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """
        Set configuration value by key.
        
        Args:
            key (str): Configuration key (supports dot notation)
            value (Any): Value to set
        """
        keys = key.split('.')
        config = self.config_data
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model-specific configuration."""
        return self.get("model", {})
    
    def get_bias_analysis_config(self) -> Dict[str, Any]:
        """Get bias analysis configuration."""
        return self.get("bias_analysis", {})
    
    def get_fine_tuning_config(self) -> Dict[str, Any]:
        """Get fine-tuning configuration."""
        return self.get("fine_tuning", {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration."""
        return self.get("output", {})
    
    def get_weathub_config(self) -> Dict[str, Any]:
        """Get WEATHub configuration."""
        return self.get("weathub", {})
    
    def get_visualization_config(self) -> Dict[str, Any]:
        """Get visualization configuration."""
        return self.get("visualization", {})
    
    def save_config(self, filepath: str):
        """
        Save current configuration to file.
        
        Args:
            filepath (str): Path to save the configuration
        """
        try:
            with open(filepath, 'w') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, indent=2)
            print(f"Configuration saved to: {filepath}")
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def load_config(self, filepath: str):
        """
        Load configuration from file.
        
        Args:
            filepath (str): Path to configuration file
        """
        self._load_custom_config(filepath)
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self._load_default_config()
    
    def update(self, updates: Dict[str, Any]):
        """
        Update configuration with dictionary.
        
        Args:
            updates (Dict[str, Any]): Updates to apply
        """
        self._deep_merge(self.config_data, updates)
    
    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return self.config_data.copy()


# Global configuration instance
_global_config = None


def get_config(config_file: Optional[str] = None) -> Config:
    """
    Get global configuration instance.
    
    Args:
        config_file (Optional[str]): Path to custom config file
        
    Returns:
        Config: Configuration instance
    """
    global _global_config
    
    if _global_config is None or config_file is not None:
        _global_config = Config(config_file)
    
    return _global_config


def load_config_from_file(filepath: str):
    """
    Load configuration from file into global config.
    
    Args:
        filepath (str): Path to configuration file
    """
    config = get_config()
    config.load_config(filepath)


def reset_config():
    """Reset global configuration to defaults."""
    global _global_config
    _global_config = None
