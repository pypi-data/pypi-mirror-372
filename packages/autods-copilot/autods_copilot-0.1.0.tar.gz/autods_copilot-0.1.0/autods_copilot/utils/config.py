"""
Configuration management for AutoDS Copilot.

This module handles loading and managing configuration settings
for the AutoDS Copilot package.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, asdict


@dataclass
class ModelConfig:
    """Configuration for machine learning models."""
    max_features: Optional[int] = None
    random_state: int = 42
    test_size: float = 0.2
    cv_folds: int = 5
    scoring: str = 'auto'  # 'auto', 'accuracy', 'f1', 'roc_auc', 'r2', 'neg_mean_squared_error'
    

@dataclass
class ExecutorConfig:
    """Configuration for code execution."""
    timeout: int = 30
    max_code_length: int = 10000
    max_lines: int = 500
    max_ast_depth: int = 20


@dataclass
class EDAConfig:
    """Configuration for EDA operations."""
    max_categorical_cardinality: int = 50
    correlation_threshold: float = 0.8
    missing_threshold: float = 0.1
    skewness_threshold: float = 2.0


@dataclass
class EncodingConfig:
    """Configuration for categorical encoding."""
    auto_detect_ordinal: bool = True
    onehot_max_categories: int = 20
    target_encoding_smoothing: float = 1.0
    handle_unknown: str = 'error'  # 'error', 'ignore'


class Config:
    """
    Main configuration class for AutoDS Copilot.
    
    This class manages all configuration settings and provides
    methods to load configuration from files or environment variables.
    """
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to configuration file (YAML)
        """
        self.model = ModelConfig()
        self.executor = ExecutorConfig()
        self.eda = EDAConfig()
        self.encoding = EncodingConfig()
        
        # Load configuration from file if provided
        if config_path:
            self.load_from_file(config_path)
        
        # Load configuration from environment variables
        self._load_from_env()
    
    def load_from_file(self, config_path: Union[str, Path]) -> None:
        """
        Load configuration from a YAML file.
        
        Args:
            config_path: Path to the configuration file
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is malformed
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if config_data:
                self._update_from_dict(config_data)
                
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing configuration file: {e}")
    
    def save_to_file(self, config_path: Union[str, Path]) -> None:
        """
        Save current configuration to a YAML file.
        
        Args:
            config_path: Path where to save the configuration
        """
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_dict = self.to_dict()
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            'model': asdict(self.model),
            'executor': asdict(self.executor),
            'eda': asdict(self.eda),
            'encoding': asdict(self.encoding)
        }
    
    def _update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        if 'model' in config_dict:
            self._update_dataclass(self.model, config_dict['model'])
        
        if 'executor' in config_dict:
            self._update_dataclass(self.executor, config_dict['executor'])
        
        if 'eda' in config_dict:
            self._update_dataclass(self.eda, config_dict['eda'])
        
        if 'encoding' in config_dict:
            self._update_dataclass(self.encoding, config_dict['encoding'])
    
    def _update_dataclass(self, dataclass_instance: Any, update_dict: Dict[str, Any]) -> None:
        """Update dataclass instance with values from dictionary."""
        for key, value in update_dict.items():
            if hasattr(dataclass_instance, key):
                setattr(dataclass_instance, key, value)
    
    def _load_from_env(self) -> None:
        """Load configuration values from environment variables."""
        # Model configuration
        if os.getenv('AUTODS_RANDOM_STATE'):
            self.model.random_state = int(os.getenv('AUTODS_RANDOM_STATE'))
        
        if os.getenv('AUTODS_TEST_SIZE'):
            self.model.test_size = float(os.getenv('AUTODS_TEST_SIZE'))
        
        if os.getenv('AUTODS_CV_FOLDS'):
            self.model.cv_folds = int(os.getenv('AUTODS_CV_FOLDS'))
        
        # Executor configuration
        if os.getenv('AUTODS_TIMEOUT'):
            self.executor.timeout = int(os.getenv('AUTODS_TIMEOUT'))
        
        if os.getenv('AUTODS_MAX_CODE_LENGTH'):
            self.executor.max_code_length = int(os.getenv('AUTODS_MAX_CODE_LENGTH'))
        
        # EDA configuration
        if os.getenv('AUTODS_MAX_CARDINALITY'):
            self.eda.max_categorical_cardinality = int(os.getenv('AUTODS_MAX_CARDINALITY'))
        
        if os.getenv('AUTODS_CORRELATION_THRESHOLD'):
            self.eda.correlation_threshold = float(os.getenv('AUTODS_CORRELATION_THRESHOLD'))


def get_default_config() -> Config:
    """
    Get default configuration instance.
    
    Returns:
        Default Config instance
    """
    return Config()


def load_config(config_path: Optional[Union[str, Path]] = None) -> Config:
    """
    Load configuration from file or create default.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Config instance
    """
    if config_path and Path(config_path).exists():
        return Config(config_path)
    else:
        return get_default_config()
