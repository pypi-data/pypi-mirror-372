"""
Response Handler - Processes and formats agent responses.

This module handles the formatting and presentation of results from
various AutoDS operations.
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ..utils.logger import get_logger


class ResponseHandler:
    """
    Handles processing and formatting of agent responses.
    
    This class takes raw execution results and formats them into
    user-friendly responses with appropriate visualizations and summaries.
    """
    
    def __init__(self):
        """Initialize the ResponseHandler."""
        self.logger = get_logger(__name__)
    
    def format_response(self, result: Any, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the execution result based on the intent.
        
        Args:
            result: Raw execution result
            intent: Intent dictionary from prompt parsing
            
        Returns:
            Formatted response dictionary
        """
        try:
            response = {
                'success': True,
                'intent': intent,
                'result': result,
                'summary': '',
                'visualizations': [],
                'recommendations': [],
                'metadata': {}
            }
            
            # Format based on intent category
            if intent['category'] == 'eda':
                response = self._format_eda_response(result, response)
            elif intent['category'] == 'visualization':
                response = self._format_visualization_response(result, response)
            elif intent['category'] == 'encoding':
                response = self._format_encoding_response(result, response)
            elif intent['category'] == 'modeling':
                response = self._format_modeling_response(result, response)
            elif intent['category'] == 'evaluation':
                response = self._format_evaluation_response(result, response)
            else:
                response = self._format_general_response(result, response)
            
            self.logger.debug(f"Formatted response for intent: {intent['category']}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error formatting response: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'intent': intent,
                'result': None
            }
    
    def _format_eda_response(self, result: Any, response: Dict[str, Any]) -> Dict[str, Any]:
        """Format EDA analysis results."""
        if isinstance(result, dict):
            response['summary'] = self._create_eda_summary(result)
            response['recommendations'] = self._get_eda_recommendations(result)
        else:
            response['summary'] = "EDA analysis completed successfully."
        
        return response
    
    def _format_visualization_response(self, result: Any, response: Dict[str, Any]) -> Dict[str, Any]:
        """Format visualization results."""
        response['summary'] = "Visualization generated successfully."
        
        # If result contains matplotlib figures, store them
        if hasattr(result, 'get_figure'):
            response['visualizations'].append(result.get_figure())
        
        return response
    
    def _format_encoding_response(self, result: Any, response: Dict[str, Any]) -> Dict[str, Any]:
        """Format encoding results."""
        if isinstance(result, dict) and 'encoded_data' in result:
            response['summary'] = f"Categorical encoding completed. " \
                                f"Shape changed from {result.get('original_shape')} " \
                                f"to {result.get('new_shape')}."
            response['metadata']['encoding_info'] = result.get('encoding_info', {})
        else:
            response['summary'] = "Categorical encoding completed successfully."
        
        return response
    
    def _format_modeling_response(self, result: Any, response: Dict[str, Any]) -> Dict[str, Any]:
        """Format modeling results."""
        if isinstance(result, dict):
            model_name = result.get('model_name', 'Unknown')
            score = result.get('score', 'N/A')
            response['summary'] = f"Model training completed. " \
                                f"Best model: {model_name}, Score: {score}"
            response['metadata']['model_info'] = result
        else:
            response['summary'] = "Model training completed successfully."
        
        return response
    
    def _format_evaluation_response(self, result: Any, response: Dict[str, Any]) -> Dict[str, Any]:
        """Format evaluation results."""
        if isinstance(result, dict):
            metrics = result.get('metrics', {})
            response['summary'] = self._create_metrics_summary(metrics)
            response['metadata']['evaluation_metrics'] = metrics
        else:
            response['summary'] = "Model evaluation completed successfully."
        
        return response
    
    def _format_general_response(self, result: Any, response: Dict[str, Any]) -> Dict[str, Any]:
        """Format general responses."""
        response['summary'] = "Operation completed successfully."
        
        if isinstance(result, pd.DataFrame):
            response['summary'] += f" Result contains {result.shape[0]} rows and {result.shape[1]} columns."
        elif isinstance(result, dict):
            response['summary'] += f" Result contains {len(result)} items."
        elif isinstance(result, list):
            response['summary'] += f" Result contains {len(result)} items."
        
        return response
    
    def _create_eda_summary(self, eda_result: Dict[str, Any]) -> str:
        """Create a summary for EDA results."""
        summary_parts = []
        
        if 'data_shape' in eda_result:
            shape = eda_result['data_shape']
            summary_parts.append(f"Dataset contains {shape[0]} rows and {shape[1]} columns.")
        
        if 'missing_values' in eda_result:
            missing = eda_result['missing_values']
            if missing > 0:
                summary_parts.append(f"Found {missing} missing values.")
            else:
                summary_parts.append("No missing values found.")
        
        if 'categorical_columns' in eda_result:
            cat_cols = len(eda_result['categorical_columns'])
            summary_parts.append(f"Identified {cat_cols} categorical columns.")
        
        if 'numerical_columns' in eda_result:
            num_cols = len(eda_result['numerical_columns'])
            summary_parts.append(f"Identified {num_cols} numerical columns.")
        
        return " ".join(summary_parts) if summary_parts else "EDA analysis completed."
    
    def _get_eda_recommendations(self, eda_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on EDA results."""
        recommendations = []
        
        if 'missing_values' in eda_result and eda_result['missing_values'] > 0:
            recommendations.append("Consider handling missing values before modeling.")
        
        if 'high_cardinality_columns' in eda_result:
            high_card = eda_result['high_cardinality_columns']
            if high_card:
                recommendations.append(f"High cardinality columns detected: {', '.join(high_card)}. "
                                     "Consider feature engineering or dimensionality reduction.")
        
        if 'skewed_columns' in eda_result:
            skewed = eda_result['skewed_columns']
            if skewed:
                recommendations.append(f"Skewed distributions detected in: {', '.join(skewed)}. "
                                     "Consider log transformation or normalization.")
        
        return recommendations
    
    def _create_metrics_summary(self, metrics: Dict[str, Any]) -> str:
        """Create a summary for evaluation metrics."""
        summary_parts = []
        
        # Common metrics
        metric_names = {
            'accuracy': 'Accuracy',
            'precision': 'Precision', 
            'recall': 'Recall',
            'f1_score': 'F1 Score',
            'r2_score': 'R² Score',
            'mse': 'MSE',
            'rmse': 'RMSE',
            'mae': 'MAE'
        }
        
        for metric_key, metric_name in metric_names.items():
            if metric_key in metrics:
                value = metrics[metric_key]
                if isinstance(value, float):
                    summary_parts.append(f"{metric_name}: {value:.4f}")
                else:
                    summary_parts.append(f"{metric_name}: {value}")
        
        return ", ".join(summary_parts) if summary_parts else "Evaluation metrics calculated."
