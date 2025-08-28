"""
Categorical Encoder - Advanced categorical variable encoding.

This module provides various encoding strategies for categorical variables
with automatic strategy selection and target-aware encoding.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from ...utils.logger import get_logger


class CategoricalEncoder:
    """
    Advanced categorical variable encoder with multiple strategies.
    
    This class provides various encoding techniques for categorical variables
    including OneHot, Ordinal, Target, and Binary encoding.
    """
    
    def __init__(self, strategy: str = 'auto'):
        """
        Initialize the CategoricalEncoder.
        
        Args:
            strategy: Encoding strategy ('auto', 'onehot', 'ordinal', 'target', 'binary')
        """
        self.logger = get_logger(__name__)
        self.strategy = strategy
        self.encoders = {}
        self.encoding_info = {}
    
    def fit_transform(self, X: pd.DataFrame, 
                     y: Optional[pd.Series] = None,
                     categorical_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Fit the encoder and transform the data.
        
        Args:
            X: Input DataFrame
            y: Target variable (required for target encoding)
            categorical_columns: List of categorical columns to encode
            
        Returns:
            Transformed DataFrame
        """
        try:
            # Identify categorical columns if not provided
            if categorical_columns is None:
                categorical_columns = self._identify_categorical_columns(X)
            
            self.logger.info(f"Encoding {len(categorical_columns)} categorical columns")
            
            # Create a copy of the data
            X_encoded = X.copy()
            
            # Encode each categorical column
            for col in categorical_columns:
                if col not in X.columns:
                    self.logger.warning(f"Column '{col}' not found in DataFrame")
                    continue
                
                # Determine encoding strategy for this column
                encoding_strategy = self._determine_strategy(X[col], y, col)
                
                # Apply encoding
                encoded_col = self._apply_encoding(X[col], y, encoding_strategy, col)
                
                # Replace or add encoded columns
                if isinstance(encoded_col, pd.DataFrame):
                    # Multiple columns (e.g., OneHot)
                    X_encoded = X_encoded.drop(columns=[col])
                    X_encoded = pd.concat([X_encoded, encoded_col], axis=1)
                else:
                    # Single column
                    X_encoded[col] = encoded_col
                
                # Store encoding information
                self.encoding_info[col] = {
                    'strategy': encoding_strategy,
                    'original_cardinality': X[col].nunique(),
                    'encoded_columns': encoded_col.columns.tolist() if isinstance(encoded_col, pd.DataFrame) else [col]
                }
            
            self.logger.info("Categorical encoding completed successfully")
            return X_encoded
            
        except Exception as e:
            self.logger.error(f"Error in categorical encoding: {str(e)}")
            raise
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform new data using fitted encoders.
        
        Args:
            X: Input DataFrame to transform
            
        Returns:
            Transformed DataFrame
        """
        if not self.encoders:
            raise ValueError("Encoder not fitted. Call fit_transform first.")
        
        X_encoded = X.copy()
        
        for col, encoder_info in self.encoders.items():
            if col in X.columns:
                strategy = encoder_info['strategy']
                encoder = encoder_info['encoder']
                
                if strategy == 'onehot':
                    encoded_col = self._transform_onehot(X[col], encoder)
                elif strategy == 'ordinal':
                    encoded_col = self._transform_ordinal(X[col], encoder)
                elif strategy == 'target':
                    encoded_col = self._transform_target(X[col], encoder)
                elif strategy == 'binary':
                    encoded_col = self._transform_binary(X[col], encoder)
                else:
                    continue
                
                # Replace columns
                if isinstance(encoded_col, pd.DataFrame):
                    X_encoded = X_encoded.drop(columns=[col])
                    X_encoded = pd.concat([X_encoded, encoded_col], axis=1)
                else:
                    X_encoded[col] = encoded_col
        
        return X_encoded
    
    def _identify_categorical_columns(self, X: pd.DataFrame) -> List[str]:
        """Identify categorical columns in the DataFrame."""
        categorical_columns = []
        
        for col in X.columns:
            if X[col].dtype in ['object', 'category']:
                categorical_columns.append(col)
            elif X[col].dtype in ['int64', 'float64']:
                # Check if it might be categorical (low cardinality)
                unique_ratio = X[col].nunique() / len(X)
                if unique_ratio < 0.05 and X[col].nunique() < 20:
                    categorical_columns.append(col)
        
        return categorical_columns
    
    def _determine_strategy(self, series: pd.Series, 
                          y: Optional[pd.Series], 
                          column_name: str) -> str:
        """
        Determine the best encoding strategy for a categorical column.
        
        Args:
            series: The categorical series
            y: Target variable
            column_name: Name of the column
            
        Returns:
            Encoding strategy name
        """
        if self.strategy != 'auto':
            return self.strategy
        
        cardinality = series.nunique()
        
        # High cardinality (>50 categories) - use target encoding if target available
        if cardinality > 50:
            if y is not None:
                return 'target'
            else:
                return 'binary'
        
        # Medium cardinality (10-50 categories) - use target or ordinal
        elif cardinality > 10:
            if y is not None and self._is_ordinal(series):
                return 'ordinal'
            elif y is not None:
                return 'target'
            else:
                return 'onehot'
        
        # Low cardinality (<10 categories) - use onehot or ordinal
        else:
            if self._is_ordinal(series):
                return 'ordinal'
            else:
                return 'onehot'
    
    def _is_ordinal(self, series: pd.Series) -> bool:
        """
        Heuristic to determine if a categorical variable is ordinal.
        
        Args:
            series: Categorical series
            
        Returns:
            True if likely ordinal, False otherwise
        """
        # Common ordinal patterns
        ordinal_patterns = [
            ['low', 'medium', 'high'],
            ['small', 'medium', 'large'],
            ['poor', 'fair', 'good', 'excellent'],
            ['never', 'rarely', 'sometimes', 'often', 'always'],
            ['strongly disagree', 'disagree', 'neutral', 'agree', 'strongly agree']
        ]
        
        unique_values = [str(val).lower() for val in series.unique() if pd.notna(val)]
        
        # Check if values match any ordinal pattern
        for pattern in ordinal_patterns:
            if set(unique_values).issubset(set(pattern)):
                return True
        
        # Check for numeric-like categories
        try:
            numeric_values = [float(val) for val in unique_values if str(val).replace('.', '').isdigit()]
            if len(numeric_values) == len(unique_values):
                return True
        except:
            pass
        
        return False
    
    def _apply_encoding(self, series: pd.Series, 
                       y: Optional[pd.Series], 
                       strategy: str, 
                       column_name: str) -> Union[pd.Series, pd.DataFrame]:
        """Apply the specified encoding strategy."""
        
        if strategy == 'onehot':
            return self._apply_onehot(series, column_name)
        elif strategy == 'ordinal':
            return self._apply_ordinal(series, column_name)
        elif strategy == 'target':
            if y is None:
                self.logger.warning(f"Target encoding requested for '{column_name}' but no target provided. Using ordinal.")
                return self._apply_ordinal(series, column_name)
            return self._apply_target(series, y, column_name)
        elif strategy == 'binary':
            return self._apply_binary(series, column_name)
        else:
            self.logger.warning(f"Unknown encoding strategy '{strategy}'. Using ordinal.")
            return self._apply_ordinal(series, column_name)
    
    def _apply_onehot(self, series: pd.Series, column_name: str) -> pd.DataFrame:
        """Apply one-hot encoding."""
        # Create one-hot encoded DataFrame
        encoded = pd.get_dummies(series, prefix=column_name, dummy_na=True)
        
        # Store encoder info
        self.encoders[column_name] = {
            'strategy': 'onehot',
            'encoder': {
                'categories': series.unique().tolist(),
                'columns': encoded.columns.tolist()
            }
        }
        
        return encoded
    
    def _apply_ordinal(self, series: pd.Series, column_name: str) -> pd.Series:
        """Apply ordinal encoding."""
        # Create mapping
        unique_values = series.unique()
        unique_values = unique_values[~pd.isna(unique_values)]  # Remove NaN
        
        # Sort values if they appear to be ordinal
        if self._is_ordinal(series):
            # Try to sort intelligently
            try:
                sorted_values = sorted(unique_values, key=lambda x: str(x))
            except:
                sorted_values = list(unique_values)
        else:
            sorted_values = list(unique_values)
        
        # Create mapping
        mapping = {val: idx for idx, val in enumerate(sorted_values)}
        
        # Apply mapping
        encoded = series.map(mapping)
        
        # Store encoder info
        self.encoders[column_name] = {
            'strategy': 'ordinal',
            'encoder': {
                'mapping': mapping,
                'categories': sorted_values
            }
        }
        
        return encoded
    
    def _apply_target(self, series: pd.Series, y: pd.Series, column_name: str) -> pd.Series:
        """Apply target encoding with smoothing."""
        # Calculate global mean
        global_mean = y.mean()
        
        # Calculate category means and counts
        category_stats = pd.DataFrame({
            'target': y,
            'category': series
        }).groupby('category').agg({
            'target': ['mean', 'count']
        }).round(6)
        
        category_stats.columns = ['mean', 'count']
        
        # Apply smoothing (Bayesian average)
        alpha = 1.0  # Smoothing parameter
        category_stats['smoothed_mean'] = (
            (category_stats['count'] * category_stats['mean'] + alpha * global_mean) /
            (category_stats['count'] + alpha)
        )
        
        # Create mapping
        mapping = category_stats['smoothed_mean'].to_dict()
        mapping[np.nan] = global_mean  # Handle NaN values
        
        # Apply mapping
        encoded = series.map(mapping).fillna(global_mean)
        
        # Store encoder info
        self.encoders[column_name] = {
            'strategy': 'target',
            'encoder': {
                'mapping': mapping,
                'global_mean': global_mean
            }
        }
        
        return encoded
    
    def _apply_binary(self, series: pd.Series, column_name: str) -> pd.DataFrame:
        """Apply binary encoding."""
        # Get unique categories
        categories = series.unique()
        categories = categories[~pd.isna(categories)]
        
        # Calculate number of binary columns needed
        n_cols = int(np.ceil(np.log2(len(categories)))) if len(categories) > 0 else 1
        
        # Create mapping to binary
        binary_mapping = {}
        for i, cat in enumerate(categories):
            binary_repr = format(i, f'0{n_cols}b')
            binary_mapping[cat] = [int(bit) for bit in binary_repr]
        
        # Apply mapping
        encoded_data = []
        for val in series:
            if pd.isna(val):
                encoded_data.append([0] * n_cols)  # Handle NaN
            else:
                encoded_data.append(binary_mapping.get(val, [0] * n_cols))
        
        # Create DataFrame
        columns = [f'{column_name}_binary_{i}' for i in range(n_cols)]
        encoded = pd.DataFrame(encoded_data, columns=columns, index=series.index)
        
        # Store encoder info
        self.encoders[column_name] = {
            'strategy': 'binary',
            'encoder': {
                'mapping': binary_mapping,
                'columns': columns,
                'n_cols': n_cols
            }
        }
        
        return encoded
    
    def _transform_onehot(self, series: pd.Series, encoder: Dict) -> pd.DataFrame:
        """Transform using fitted one-hot encoder."""
        encoded = pd.get_dummies(series, prefix=series.name, dummy_na=True)
        
        # Ensure all expected columns are present
        expected_columns = encoder['columns']
        for col in expected_columns:
            if col not in encoded.columns:
                encoded[col] = 0
        
        # Remove any unexpected columns and reorder
        encoded = encoded[expected_columns]
        
        return encoded
    
    def _transform_ordinal(self, series: pd.Series, encoder: Dict) -> pd.Series:
        """Transform using fitted ordinal encoder."""
        mapping = encoder['mapping']
        return series.map(mapping)
    
    def _transform_target(self, series: pd.Series, encoder: Dict) -> pd.Series:
        """Transform using fitted target encoder."""
        mapping = encoder['mapping']
        global_mean = encoder['global_mean']
        return series.map(mapping).fillna(global_mean)
    
    def _transform_binary(self, series: pd.Series, encoder: Dict) -> pd.DataFrame:
        """Transform using fitted binary encoder."""
        mapping = encoder['mapping']
        columns = encoder['columns']
        n_cols = encoder['n_cols']
        
        # Apply mapping
        encoded_data = []
        for val in series:
            if pd.isna(val):
                encoded_data.append([0] * n_cols)
            else:
                encoded_data.append(mapping.get(val, [0] * n_cols))
        
        return pd.DataFrame(encoded_data, columns=columns, index=series.index)
    
    def get_encoding_info(self) -> Dict[str, Any]:
        """Get information about applied encodings."""
        return self.encoding_info.copy()
    
    def get_feature_names(self) -> List[str]:
        """Get names of all encoded features."""
        feature_names = []
        for col_info in self.encoding_info.values():
            feature_names.extend(col_info['encoded_columns'])
        return feature_names
