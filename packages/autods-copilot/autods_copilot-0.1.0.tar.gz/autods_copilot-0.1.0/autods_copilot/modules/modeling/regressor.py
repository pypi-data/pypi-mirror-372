"""
Regression Manager - Advanced regression model management.

This module provides comprehensive regression model training,
evaluation, and comparison capabilities.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from ...utils.logger import get_logger


class RegressionManager:
    """
    Manages regression model training and evaluation.
    
    This class provides methods for training multiple regression models,
    comparing their performance, and selecting the best model.
    """
    
    def __init__(self, random_state: int = 42):
        """
        Initialize the RegressionManager.
        
        Args:
            random_state: Random state for reproducibility
        """
        self.logger = get_logger(__name__)
        self.random_state = random_state
        self.models = {}
        self.results = {}
        self.best_model = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
    
    def train_models(self, X: pd.DataFrame, y: pd.Series,
                    test_size: float = 0.2,
                    models_to_train: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Train multiple regression models and compare performance.
        
        Args:
            X: Feature matrix
            y: Target variable
            test_size: Test set size (0.0 to 1.0)
            models_to_train: List of model names to train
            
        Returns:
            Dictionary containing training results
        """
        try:
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import StandardScaler
            from sklearn.linear_model import LinearRegression, Ridge, Lasso
            from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
            from sklearn.svm import SVR
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            
            self.logger.info("Starting regression model training")
            
            # Split the data
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                X, y, test_size=test_size, random_state=self.random_state
            )
            
            # Scale the features for algorithms that need it
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(self.X_train)
            X_test_scaled = scaler.transform(self.X_test)
            
            # Define models to train
            all_models = {
                'linear_regression': LinearRegression(),
                'ridge_regression': Ridge(
                    alpha=1.0, random_state=self.random_state
                ),
                'lasso_regression': Lasso(
                    alpha=1.0, random_state=self.random_state, max_iter=1000
                ),
                'random_forest': RandomForestRegressor(
                    n_estimators=100, random_state=self.random_state
                ),
                'gradient_boosting': GradientBoostingRegressor(
                    n_estimators=100, random_state=self.random_state
                ),
                'svr': SVR(kernel='rbf', C=1.0, gamma='scale')
            }
            
            if models_to_train is None:
                models_to_train = list(all_models.keys())
            
            # Train and evaluate each model
            for model_name in models_to_train:
                if model_name not in all_models:
                    self.logger.warning(f"Unknown model: {model_name}")
                    continue
                
                self.logger.info(f"Training {model_name}")
                
                model = all_models[model_name]
                
                # Use scaled data for SVR and regularized linear models
                if model_name in ['svr', 'ridge_regression', 'lasso_regression']:
                    X_train_model = X_train_scaled
                    X_test_model = X_test_scaled
                else:
                    X_train_model = self.X_train
                    X_test_model = self.X_test
                
                # Train the model
                model.fit(X_train_model, self.y_train)
                
                # Make predictions
                y_pred = model.predict(X_test_model)
                
                # Calculate metrics
                metrics = self._calculate_regression_metrics(self.y_test, y_pred)
                
                # Store results
                self.models[model_name] = model
                self.results[model_name] = {
                    'model': model,
                    'predictions': y_pred,
                    'metrics': metrics,
                    'scaled_data_used': model_name in ['svr', 'ridge_regression', 'lasso_regression']
                }
            
            # Find best model
            self._select_best_model()
            
            self.logger.info("Regression model training completed")
            return self._format_results()
            
        except Exception as e:
            self.logger.error(f"Error in regression training: {str(e)}")
            raise
    
    def _calculate_regression_metrics(self, y_true: np.ndarray, 
                                    y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate regression metrics."""
        try:
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            
            metrics = {
                'mse': mean_squared_error(y_true, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
                'mae': mean_absolute_error(y_true, y_pred),
                'r2_score': r2_score(y_true, y_pred)
            }
            
            # Calculate additional metrics
            metrics['mape'] = self._calculate_mape(y_true, y_pred)
            metrics['explained_variance'] = 1 - np.var(y_true - y_pred) / np.var(y_true)
            
            return metrics
            
        except Exception as e:
            self.logger.warning(f"Error calculating metrics: {str(e)}")
            return {'mse': float('inf'), 'rmse': float('inf'), 'mae': float('inf'), 'r2_score': -float('inf')}
    
    def _calculate_mape(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Mean Absolute Percentage Error."""
        try:
            # Avoid division by zero
            mask = y_true != 0
            if not np.any(mask):
                return float('inf')
            
            mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
            return float(mape)
        except:
            return float('inf')
    
    def _select_best_model(self) -> None:
        """Select the best performing model."""
        if not self.results:
            return
        
        # Use R² score as primary metric (higher is better)
        best_score = -float('inf')
        best_name = None
        
        for model_name, result in self.results.items():
            r2_score = result['metrics'].get('r2_score', -float('inf'))
            if r2_score > best_score:
                best_score = r2_score
                best_name = model_name
        
        if best_name:
            self.best_model = {
                'name': best_name,
                'model': self.results[best_name]['model'],
                'metrics': self.results[best_name]['metrics']
            }
            self.logger.info(f"Best model selected: {best_name} (R²: {best_score:.4f})")
    
    def _format_results(self) -> Dict[str, Any]:
        """Format results for output."""
        formatted_results = {
            'models_trained': list(self.results.keys()),
            'best_model': self.best_model,
            'all_results': {},
            'comparison': self._create_comparison_table()
        }
        
        # Format individual results
        for model_name, result in self.results.items():
            formatted_results['all_results'][model_name] = {
                'metrics': result['metrics'],
                'scaled_data_used': result.get('scaled_data_used', False)
            }
        
        return formatted_results
    
    def _create_comparison_table(self) -> pd.DataFrame:
        """Create a comparison table of all models."""
        if not self.results:
            return pd.DataFrame()
        
        comparison_data = []
        for model_name, result in self.results.items():
            metrics = result['metrics']
            row = {'Model': model_name}
            row.update(metrics)
            comparison_data.append(row)
        
        df = pd.DataFrame(comparison_data)
        
        # Sort by R² score descending
        if 'r2_score' in df.columns:
            df = df.sort_values('r2_score', ascending=False)
        
        return df
    
    def predict(self, X: pd.DataFrame, model_name: Optional[str] = None) -> np.ndarray:
        """
        Make predictions using a trained model.
        
        Args:
            X: Feature matrix
            model_name: Name of model to use (uses best model if None)
            
        Returns:
            Predictions array
        """
        if model_name is None:
            if self.best_model is None:
                raise ValueError("No models trained yet")
            model = self.best_model['model']
            model_name = self.best_model['name']
        else:
            if model_name not in self.models:
                raise ValueError(f"Model '{model_name}' not found")
            model = self.models[model_name]
        
        # Check if scaling is needed
        if self.results[model_name].get('scaled_data_used', False):
            # Need to scale the data (assuming scaler was fitted during training)
            from sklearn.preprocessing import StandardScaler
            scaler = StandardScaler()
            scaler.fit(self.X_train)  # Refit on training data
            X_scaled = scaler.transform(X)
            return model.predict(X_scaled)
        else:
            return model.predict(X)
    
    def get_feature_importance(self, model_name: Optional[str] = None) -> Optional[pd.Series]:
        """
        Get feature importance from a trained model.
        
        Args:
            model_name: Name of model (uses best model if None)
            
        Returns:
            Feature importance series or None if not available
        """
        if model_name is None:
            if self.best_model is None:
                return None
            model = self.best_model['model']
        else:
            if model_name not in self.models:
                return None
            model = self.models[model_name]
        
        # Get feature importance if available
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            feature_names = self.X_train.columns if self.X_train is not None else None
            if feature_names is not None:
                return pd.Series(importance, index=feature_names).sort_values(ascending=False)
            else:
                return pd.Series(importance)
        elif hasattr(model, 'coef_'):
            # For linear models, use coefficient magnitude
            coef = np.abs(model.coef_)
            feature_names = self.X_train.columns if self.X_train is not None else None
            if feature_names is not None:
                return pd.Series(coef, index=feature_names).sort_values(ascending=False)
            else:
                return pd.Series(coef)
        
        return None
    
    def plot_predictions(self, model_name: Optional[str] = None) -> None:
        """
        Plot actual vs predicted values.
        
        Args:
            model_name: Name of model to plot (uses best model if None)
        """
        try:
            import matplotlib.pyplot as plt
            
            if model_name is None:
                if self.best_model is None:
                    raise ValueError("No models trained yet")
                predictions = self.results[self.best_model['name']]['predictions']
                model_name = self.best_model['name']
            else:
                if model_name not in self.results:
                    raise ValueError(f"Model '{model_name}' not found")
                predictions = self.results[model_name]['predictions']
            
            plt.figure(figsize=(8, 6))
            plt.scatter(self.y_test, predictions, alpha=0.6)
            plt.plot([self.y_test.min(), self.y_test.max()], 
                    [self.y_test.min(), self.y_test.max()], 'r--', lw=2)
            plt.xlabel('Actual Values')
            plt.ylabel('Predicted Values')
            plt.title(f'Actual vs Predicted - {model_name}')
            plt.grid(True, alpha=0.3)
            plt.show()
            
        except Exception as e:
            self.logger.error(f"Error plotting predictions: {str(e)}")
    
    def plot_residuals(self, model_name: Optional[str] = None) -> None:
        """
        Plot residuals.
        
        Args:
            model_name: Name of model to plot (uses best model if None)
        """
        try:
            import matplotlib.pyplot as plt
            
            if model_name is None:
                if self.best_model is None:
                    raise ValueError("No models trained yet")
                predictions = self.results[self.best_model['name']]['predictions']
                model_name = self.best_model['name']
            else:
                if model_name not in self.results:
                    raise ValueError(f"Model '{model_name}' not found")
                predictions = self.results[model_name]['predictions']
            
            residuals = self.y_test - predictions
            
            plt.figure(figsize=(12, 4))
            
            # Residuals vs Predicted
            plt.subplot(1, 2, 1)
            plt.scatter(predictions, residuals, alpha=0.6)
            plt.axhline(y=0, color='r', linestyle='--')
            plt.xlabel('Predicted Values')
            plt.ylabel('Residuals')
            plt.title('Residuals vs Predicted')
            plt.grid(True, alpha=0.3)
            
            # Residuals histogram
            plt.subplot(1, 2, 2)
            plt.hist(residuals, bins=20, alpha=0.7, edgecolor='black')
            plt.xlabel('Residuals')
            plt.ylabel('Frequency')
            plt.title('Residuals Distribution')
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            self.logger.error(f"Error plotting residuals: {str(e)}")
