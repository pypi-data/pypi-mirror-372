"""
Data validators for AutoDS Copilot.

This module provides validation utilities for data inputs,
ensuring data quality and compatibility with AutoDS operations.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from ..utils.logger import get_logger


class ValidationError(Exception):
    """Custom exception for data validation errors."""
    pass


class DataValidator:
    """
    Validates data inputs for AutoDS operations.
    
    This class provides comprehensive validation for DataFrames,
    ensuring they meet the requirements for various data science operations.
    """
    
    def __init__(self):
        """Initialize the DataValidator."""
        self.logger = get_logger(__name__)
    
    def validate_dataframe(self, df: pd.DataFrame, 
                          min_rows: int = 10, 
                          min_cols: int = 2,
                          allow_missing: bool = True,
                          max_missing_ratio: float = 0.8) -> Dict[str, Any]:
        """
        Validate a pandas DataFrame for general data science operations.
        
        Args:
            df: DataFrame to validate
            min_rows: Minimum number of rows required
            min_cols: Minimum number of columns required
            allow_missing: Whether to allow missing values
            max_missing_ratio: Maximum ratio of missing values allowed
            
        Returns:
            Dictionary containing validation results
            
        Raises:
            ValidationError: If validation fails
        """
        results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'info': {}
        }
        
        try:
            # Basic checks
            if not isinstance(df, pd.DataFrame):
                raise ValidationError("Input must be a pandas DataFrame")
            
            if df.empty:
                raise ValidationError("DataFrame is empty")
            
            # Shape validation
            if df.shape[0] < min_rows:
                results['errors'].append(f"Insufficient rows: {df.shape[0]} < {min_rows}")
                results['valid'] = False
            
            if df.shape[1] < min_cols:
                results['errors'].append(f"Insufficient columns: {df.shape[1]} < {min_cols}")
                results['valid'] = False
            
            # Missing values check
            missing_count = df.isnull().sum().sum()
            total_cells = df.shape[0] * df.shape[1]
            missing_ratio = missing_count / total_cells if total_cells > 0 else 0
            
            results['info']['missing_values'] = missing_count
            results['info']['missing_ratio'] = missing_ratio
            
            if missing_count > 0:
                if not allow_missing:
                    results['errors'].append(f"Missing values not allowed: {missing_count} found")
                    results['valid'] = False
                elif missing_ratio > max_missing_ratio:
                    results['errors'].append(f"Too many missing values: {missing_ratio:.2%} > {max_missing_ratio:.2%}")
                    results['valid'] = False
                else:
                    results['warnings'].append(f"Missing values found: {missing_count} ({missing_ratio:.2%})")
            
            # Data type analysis
            dtypes_info = self._analyze_dtypes(df)
            results['info'].update(dtypes_info)
            
            # Memory usage check
            memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
            results['info']['memory_mb'] = memory_mb
            
            if memory_mb > 1000:  # > 1GB
                results['warnings'].append(f"Large dataset: {memory_mb:.1f} MB")
            
            # Column name validation
            column_issues = self._validate_column_names(df.columns)
            if column_issues:
                results['warnings'].extend(column_issues)
            
            self.logger.debug(f"DataFrame validation completed: {results['valid']}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error validating DataFrame: {str(e)}")
            raise ValidationError(f"Validation failed: {str(e)}")
    
    def validate_target_column(self, df: pd.DataFrame, 
                              target_column: str,
                              task_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate target column for machine learning tasks.
        
        Args:
            df: DataFrame containing the target column
            target_column: Name of the target column
            task_type: 'classification' or 'regression' (auto-detected if None)
            
        Returns:
            Dictionary containing validation results
            
        Raises:
            ValidationError: If validation fails
        """
        results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'info': {}
        }
        
        try:
            # Check if column exists
            if target_column not in df.columns:
                raise ValidationError(f"Target column '{target_column}' not found in DataFrame")
            
            target_series = df[target_column]
            
            # Basic target validation
            if target_series.isnull().all():
                raise ValidationError("Target column contains only null values")
            
            # Missing values in target
            missing_count = target_series.isnull().sum()
            if missing_count > 0:
                missing_ratio = missing_count / len(target_series)
                if missing_ratio > 0.1:  # More than 10% missing
                    results['errors'].append(f"Too many missing values in target: {missing_ratio:.2%}")
                    results['valid'] = False
                else:
                    results['warnings'].append(f"Missing values in target: {missing_count}")
            
            # Determine task type if not provided
            detected_task_type = self._detect_task_type(target_series)
            if task_type is None:
                task_type = detected_task_type
            elif task_type != detected_task_type:
                results['warnings'].append(f"Specified task type '{task_type}' differs from detected '{detected_task_type}'")
            
            results['info']['task_type'] = task_type
            results['info']['detected_task_type'] = detected_task_type
            
            # Task-specific validation
            if task_type == 'classification':
                class_info = self._validate_classification_target(target_series)
                results['info'].update(class_info)
                
                if class_info['num_classes'] < 2:
                    results['errors'].append("Classification target must have at least 2 classes")
                    results['valid'] = False
                elif class_info['num_classes'] > 100:
                    results['warnings'].append(f"High number of classes: {class_info['num_classes']}")
                
                # Check class imbalance
                if class_info['imbalance_ratio'] > 10:
                    results['warnings'].append(f"Severe class imbalance: {class_info['imbalance_ratio']:.1f}:1")
            
            elif task_type == 'regression':
                reg_info = self._validate_regression_target(target_series)
                results['info'].update(reg_info)
                
                if reg_info['num_unique'] < 10:
                    results['warnings'].append(f"Low target variance: only {reg_info['num_unique']} unique values")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error validating target column: {str(e)}")
            raise ValidationError(f"Target validation failed: {str(e)}")
    
    def validate_feature_columns(self, df: pd.DataFrame, 
                                feature_columns: List[str],
                                target_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate feature columns for machine learning.
        
        Args:
            df: DataFrame containing the features
            feature_columns: List of feature column names
            target_column: Name of target column (to exclude from features)
            
        Returns:
            Dictionary containing validation results
        """
        results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'info': {}
        }
        
        try:
            # Check if all feature columns exist
            missing_cols = [col for col in feature_columns if col not in df.columns]
            if missing_cols:
                results['errors'].append(f"Feature columns not found: {missing_cols}")
                results['valid'] = False
                return results
            
            # Check if target is included in features
            if target_column and target_column in feature_columns:
                results['errors'].append("Target column should not be included in features")
                results['valid'] = False
            
            feature_df = df[feature_columns]
            
            # Analyze feature types
            categorical_features = []
            numerical_features = []
            high_cardinality_features = []
            
            for col in feature_columns:
                if df[col].dtype in ['object', 'category']:
                    categorical_features.append(col)
                    cardinality = df[col].nunique()
                    if cardinality > 50:
                        high_cardinality_features.append(col)
                else:
                    numerical_features.append(col)
            
            results['info']['categorical_features'] = categorical_features
            results['info']['numerical_features'] = numerical_features
            results['info']['high_cardinality_features'] = high_cardinality_features
            
            # Warnings for high cardinality features
            if high_cardinality_features:
                results['warnings'].append(f"High cardinality categorical features: {high_cardinality_features}")
            
            # Check for constant features
            constant_features = []
            for col in feature_columns:
                if df[col].nunique(dropna=False) <= 1:
                    constant_features.append(col)
            
            if constant_features:
                results['warnings'].append(f"Constant features detected: {constant_features}")
                results['info']['constant_features'] = constant_features
            
            # Check for duplicate features
            duplicate_pairs = self._find_duplicate_features(feature_df)
            if duplicate_pairs:
                results['warnings'].append(f"Potential duplicate features: {duplicate_pairs}")
                results['info']['duplicate_features'] = duplicate_pairs
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error validating feature columns: {str(e)}")
            raise ValidationError(f"Feature validation failed: {str(e)}")
    
    def _analyze_dtypes(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data types in the DataFrame."""
        dtype_counts = df.dtypes.value_counts()
        
        return {
            'dtypes': df.dtypes.to_dict(),
            'dtype_counts': dtype_counts.to_dict(),
            'numerical_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object', 'category']).columns.tolist(),
            'datetime_columns': df.select_dtypes(include=['datetime']).columns.tolist()
        }
    
    def _validate_column_names(self, columns: pd.Index) -> List[str]:
        """Validate column names for potential issues."""
        issues = []
        
        # Check for duplicate column names
        if columns.duplicated().any():
            duplicates = columns[columns.duplicated()].tolist()
            issues.append(f"Duplicate column names: {duplicates}")
        
        # Check for problematic characters
        problematic_chars = [' ', '.', '-', '(', ')', '[', ']']
        for col in columns:
            if any(char in str(col) for char in problematic_chars):
                issues.append(f"Column '{col}' contains problematic characters")
        
        return issues
    
    def _detect_task_type(self, series: pd.Series) -> str:
        """Detect whether a series is suitable for classification or regression."""
        if series.dtype in ['object', 'category', 'bool']:
            return 'classification'
        elif series.dtype in ['int64', 'float64']:
            unique_ratio = series.nunique() / len(series.dropna())
            if unique_ratio < 0.05:  # Less than 5% unique values
                return 'classification'
            else:
                return 'regression'
        else:
            return 'classification'  # Default fallback
    
    def _validate_classification_target(self, series: pd.Series) -> Dict[str, Any]:
        """Validate target for classification tasks."""
        value_counts = series.value_counts()
        
        return {
            'num_classes': len(value_counts),
            'class_distribution': value_counts.to_dict(),
            'imbalance_ratio': value_counts.max() / value_counts.min() if len(value_counts) > 1 else 1.0,
            'minority_class_size': value_counts.min()
        }
    
    def _validate_regression_target(self, series: pd.Series) -> Dict[str, Any]:
        """Validate target for regression tasks."""
        return {
            'num_unique': series.nunique(),
            'mean': float(series.mean()),
            'std': float(series.std()),
            'min': float(series.min()),
            'max': float(series.max()),
            'skewness': float(series.skew()) if len(series.dropna()) > 0 else 0.0
        }
    
    def _find_duplicate_features(self, df: pd.DataFrame) -> List[Tuple[str, str]]:
        """Find potentially duplicate feature columns."""
        duplicates = []
        
        # Only check numerical columns for exact duplicates
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        for i, col1 in enumerate(numerical_cols):
            for col2 in numerical_cols[i+1:]:
                if df[col1].equals(df[col2]):
                    duplicates.append((col1, col2))
        
        return duplicates
