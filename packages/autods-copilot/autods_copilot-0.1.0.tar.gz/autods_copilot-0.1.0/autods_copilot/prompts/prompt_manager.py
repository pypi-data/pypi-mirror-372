"""
Prompt Manager - Manages prompt templates for AutoDS operations.

This module handles the generation and management of prompts for
various data science operations in AutoDS Copilot.
"""

from typing import Dict, Any, Optional, List
import textwrap
from ..utils.logger import get_logger


class PromptManager:
    """
    Manages prompt templates for different AutoDS operations.
    
    This class provides a centralized way to manage and generate
    prompts for various data science tasks.
    """
    
    def __init__(self):
        """Initialize the PromptManager."""
        self.logger = get_logger(__name__)
        self.templates = self._load_templates()
    
    def get_template(self, category: str) -> str:
        """
        Get a prompt template for a specific category.
        
        Args:
            category: Template category ('eda', 'visualization', 'encoding', 'modeling', etc.)
            
        Returns:
            Prompt template string
        """
        return self.templates.get(category, self.templates['general'])
    
    def format_prompt(self, category: str, **kwargs) -> str:
        """
        Format a prompt template with provided variables.
        
        Args:
            category: Template category
            **kwargs: Variables to substitute in the template
            
        Returns:
            Formatted prompt string
        """
        template = self.get_template(category)
        try:
            return template.format(**kwargs)
        except KeyError as e:
            self.logger.warning(f"Missing template variable: {e}")
            return template
    
    def _load_templates(self) -> Dict[str, str]:
        """Load all prompt templates."""
        return {
            'eda': self._get_eda_template(),
            'visualization': self._get_visualization_template(),
            'encoding': self._get_encoding_template(),
            'modeling': self._get_modeling_template(),
            'evaluation': self._get_evaluation_template(),
            'general': self._get_general_template()
        }
    
    def _get_eda_template(self) -> str:
        """Get EDA prompt template."""
        return textwrap.dedent("""
        # Exploratory Data Analysis Task
        
        You are tasked with performing exploratory data analysis on the provided dataset.
        
        ## Dataset Information:
        - Shape: {data_info[shape]}
        - Columns: {data_info[columns]}
        - Data types: {data_info[dtypes]}
        
        ## User Request:
        {prompt}
        
        ## Instructions:
        1. Analyze the dataset structure and data quality
        2. Generate statistical summaries for numerical and categorical variables
        3. Identify missing values, outliers, and data quality issues
        4. Analyze feature distributions and relationships
        5. Provide insights and recommendations
        
        ## Available Libraries:
        - pandas as pd
        - numpy as np
        - matplotlib.pyplot as plt
        - seaborn as sns
        
        ## Expected Output:
        Store your analysis results in a variable called 'result' as a dictionary containing:
        - 'summary': Text summary of findings
        - 'statistics': Key statistics
        - 'recommendations': List of recommendations
        - 'visualizations': Any plots created
        
        ## Code:
        """).strip()
    
    def _get_visualization_template(self) -> str:
        """Get visualization prompt template."""
        return textwrap.dedent("""
        # Data Visualization Task
        
        You are tasked with creating visualizations for the provided dataset.
        
        ## Dataset Information:
        - Shape: {data_info[shape]}
        - Columns: {data_info[columns]}
        - Target column: {data_info[target_column]}
        
        ## User Request:
        {prompt}
        
        ## Instructions:
        1. Create appropriate visualizations based on the request
        2. Choose the right plot types for the data types
        3. Ensure plots are clear, labeled, and informative
        4. Use proper color schemes and styling
        
        ## Available Libraries:
        - pandas as pd
        - numpy as np
        - matplotlib.pyplot as plt
        - seaborn as sns
        
        ## Expected Output:
        Store your visualization results in a variable called 'result' containing the plot objects.
        
        ## Code:
        """).strip()
    
    def _get_encoding_template(self) -> str:
        """Get encoding prompt template."""
        return textwrap.dedent("""
        # Categorical Encoding Task
        
        You are tasked with encoding categorical variables in the provided dataset.
        
        ## Dataset Information:
        - Shape: {data_info[shape]}
        - Categorical columns: {data_info[categorical_columns]}
        - Target column: {data_info[target_column]}
        
        ## User Request:
        {prompt}
        
        ## Instructions:
        1. Identify appropriate encoding strategies for each categorical variable
        2. Consider cardinality, target relationship, and data characteristics
        3. Apply encoding techniques (OneHot, Ordinal, Target, etc.)
        4. Handle missing values appropriately
        5. Avoid target leakage
        
        ## Available Libraries:
        - pandas as pd
        - numpy as np
        - sklearn.preprocessing
        
        ## Expected Output:
        Store your encoded dataset in a variable called 'result' as a dictionary containing:
        - 'encoded_data': The encoded DataFrame
        - 'encoding_info': Information about applied encodings
        - 'feature_names': New feature names after encoding
        
        ## Code:
        """).strip()
    
    def _get_modeling_template(self) -> str:
        """Get modeling prompt template."""
        return textwrap.dedent("""
        # Machine Learning Modeling Task
        
        You are tasked with building and training machine learning models.
        
        ## Dataset Information:
        - Shape: {data_info[shape]}
        - Target column: {data_info[target_column]}
        - Task type: {data_info[task_type]}
        - Feature columns: {data_info[feature_columns]}
        
        ## User Request:
        {prompt}
        
        ## Instructions:
        1. Prepare the data for modeling (train/test split, scaling if needed)
        2. Select appropriate algorithms based on the task type and data characteristics
        3. Train multiple models and compare performance
        4. Use cross-validation for robust evaluation
        5. Tune hyperparameters if requested
        
        ## Available Libraries:
        - pandas as pd
        - numpy as np
        - sklearn (all modules)
        
        ## Expected Output:
        Store your modeling results in a variable called 'result' as a dictionary containing:
        - 'best_model': The best performing model
        - 'scores': Performance scores
        - 'model_comparison': Comparison of different models
        - 'feature_importance': Feature importance if available
        
        ## Code:
        """).strip()
    
    def _get_evaluation_template(self) -> str:
        """Get evaluation prompt template."""
        return textwrap.dedent("""
        # Model Evaluation Task
        
        You are tasked with evaluating machine learning model performance.
        
        ## Dataset Information:
        - Task type: {data_info[task_type]}
        - Target column: {data_info[target_column]}
        
        ## User Request:
        {prompt}
        
        ## Instructions:
        1. Calculate appropriate evaluation metrics based on task type
        2. For classification: accuracy, precision, recall, F1-score, ROC-AUC
        3. For regression: MSE, RMSE, MAE, R²
        4. Generate confusion matrix or residual plots as appropriate
        5. Provide interpretation of results
        
        ## Available Libraries:
        - pandas as pd
        - numpy as np
        - sklearn.metrics
        - matplotlib.pyplot as plt
        - seaborn as sns
        
        ## Expected Output:
        Store your evaluation results in a variable called 'result' as a dictionary containing:
        - 'metrics': Dictionary of calculated metrics
        - 'visualizations': Evaluation plots
        - 'interpretation': Text interpretation of results
        
        ## Code:
        """).strip()
    
    def _get_general_template(self) -> str:
        """Get general prompt template."""
        return textwrap.dedent("""
        # Data Science Task
        
        You are tasked with performing a data science operation on the provided dataset.
        
        ## Dataset Information:
        - Shape: {data_info[shape]}
        - Columns: {data_info[columns]}
        
        ## User Request:
        {prompt}
        
        ## Instructions:
        1. Understand the user's request
        2. Implement the appropriate solution using data science best practices
        3. Provide clear, well-commented code
        4. Include error handling where appropriate
        
        ## Available Libraries:
        - pandas as pd
        - numpy as np
        - matplotlib.pyplot as plt
        - seaborn as sns
        - sklearn (all modules)
        
        ## Expected Output:
        Store your results in a variable called 'result'.
        
        ## Code:
        """).strip()
