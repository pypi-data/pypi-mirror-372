"""
Classification Manager - Advanced classification model management.

This module provides comprehensive classification model training,
evaluation, and comparison capabilities.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from ...utils.logger import get_logger


class ClassificationManager:
    """
    Manages classification model training and evaluation.
    
    This class provides methods for training multiple classification models,
    comparing their performance, and selecting the best model.
    """
    
    def __init__(self, random_state: int = 42):
        """
        Initialize the ClassificationManager.
        
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
        Train multiple classification models and compare performance.
        
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
            from sklearn.linear_model import LogisticRegression
            from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
            from sklearn.svm import SVC
            from sklearn.naive_bayes import GaussianNB
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            
            self.logger.info("Starting classification model training")
            
            # Split the data
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                X, y, test_size=test_size, random_state=self.random_state, stratify=y
            )
            
            # Scale the features for algorithms that need it
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(self.X_train)
            X_test_scaled = scaler.transform(self.X_test)
            
            # Define models to train
            all_models = {
                'logistic_regression': LogisticRegression(
                    random_state=self.random_state, max_iter=1000
                ),
                'random_forest': RandomForestClassifier(
                    n_estimators=100, random_state=self.random_state
                ),
                'gradient_boosting': GradientBoostingClassifier(
                    n_estimators=100, random_state=self.random_state
                ),
                'svc': SVC(
                    random_state=self.random_state, probability=True
                ),
                'naive_bayes': GaussianNB()
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
                
                # Use scaled data for SVC and Logistic Regression
                if model_name in ['svc', 'logistic_regression']:
                    X_train_model = X_train_scaled
                    X_test_model = X_test_scaled
                else:
                    X_train_model = self.X_train
                    X_test_model = self.X_test
                
                # Train the model
                model.fit(X_train_model, self.y_train)
                
                # Make predictions
                y_pred = model.predict(X_test_model)
                y_pred_proba = None
                
                try:
                    y_pred_proba = model.predict_proba(X_test_model)
                except:
                    pass
                
                # Calculate metrics
                metrics = self._calculate_classification_metrics(
                    self.y_test, y_pred, y_pred_proba
                )
                
                # Store results
                self.models[model_name] = model
                self.results[model_name] = {
                    'model': model,
                    'predictions': y_pred,
                    'probabilities': y_pred_proba,
                    'metrics': metrics,
                    'scaled_data_used': model_name in ['svc', 'logistic_regression']
                }
            
            # Find best model
            self._select_best_model()
            
            self.logger.info("Classification model training completed")
            return self._format_results()
            
        except Exception as e:
            self.logger.error(f"Error in classification training: {str(e)}")
            raise
    
    def _calculate_classification_metrics(self, y_true: np.ndarray, 
                                        y_pred: np.ndarray,
                                        y_pred_proba: Optional[np.ndarray] = None) -> Dict[str, float]:
        """Calculate classification metrics."""
        try:
            from sklearn.metrics import (
                accuracy_score, precision_score, recall_score, f1_score,
                roc_auc_score, classification_report
            )
            
            # Determine average method based on number of classes
            n_classes = len(np.unique(y_true))
            avg_method = 'binary' if n_classes == 2 else 'weighted'
            
            metrics = {
                'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred, average=avg_method, zero_division=0),
                'recall': recall_score(y_true, y_pred, average=avg_method, zero_division=0),
                'f1_score': f1_score(y_true, y_pred, average=avg_method, zero_division=0)
            }
            
            # Add ROC AUC for binary classification or if probabilities available
            if y_pred_proba is not None:
                try:
                    if n_classes == 2:
                        metrics['roc_auc'] = roc_auc_score(y_true, y_pred_proba[:, 1])
                    else:
                        metrics['roc_auc'] = roc_auc_score(y_true, y_pred_proba, multi_class='ovr')
                except:
                    pass
            
            return metrics
            
        except Exception as e:
            self.logger.warning(f"Error calculating metrics: {str(e)}")
            return {'accuracy': 0.0, 'precision': 0.0, 'recall': 0.0, 'f1_score': 0.0}
    
    def _select_best_model(self) -> None:
        """Select the best performing model."""
        if not self.results:
            return
        
        # Use F1 score as primary metric, accuracy as tiebreaker
        best_score = -1
        best_name = None
        
        for model_name, result in self.results.items():
            f1_score = result['metrics'].get('f1_score', 0)
            if f1_score > best_score:
                best_score = f1_score
                best_name = model_name
        
        if best_name:
            self.best_model = {
                'name': best_name,
                'model': self.results[best_name]['model'],
                'metrics': self.results[best_name]['metrics']
            }
            self.logger.info(f"Best model selected: {best_name} (F1: {best_score:.4f})")
    
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
        
        # Sort by F1 score descending
        if 'f1_score' in df.columns:
            df = df.sort_values('f1_score', ascending=False)
        
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
            coef = np.abs(model.coef_[0]) if model.coef_.ndim > 1 else np.abs(model.coef_)
            feature_names = self.X_train.columns if self.X_train is not None else None
            if feature_names is not None:
                return pd.Series(coef, index=feature_names).sort_values(ascending=False)
            else:
                return pd.Series(coef)
        
        return None
