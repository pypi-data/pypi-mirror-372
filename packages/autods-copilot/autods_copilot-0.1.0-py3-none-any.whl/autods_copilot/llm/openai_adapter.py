"""
OpenAI LLM Adapter - Integration with OpenAI GPT models.

This module provides integration with OpenAI's GPT models for generating
Python code from natural language prompts.
"""

from typing import Dict, Any, Optional, List
import json
import time
import logging

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIAdapter:
    """
    Adapter for OpenAI GPT models to generate Python code from prompts.
    
    This class handles communication with OpenAI's API and manages
    prompt formatting for data science code generation.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o", 
                 max_tokens: int = 2000, temperature: float = 0.1):
        """
        Initialize the OpenAI adapter.
        
        Args:
            api_key: OpenAI API key
            model: Model name (gpt-4o, gpt-4o-mini, gpt-4-turbo, etc.)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-2.0)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
        
        self.logger = logging.getLogger(__name__)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Initialize OpenAI client
        try:
            self.client = openai.OpenAI(api_key=api_key)
            self.logger.info(f"OpenAI adapter initialized with model: {model}")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise
    
    def generate_code(self, prompt: str, context: Dict[str, Any]) -> str:
        """
        Generate Python code from a natural language prompt.
        
        Args:
            prompt: Natural language instruction
            context: Context information including data info and templates
            
        Returns:
            Generated Python code as string
        """
        try:
            # Prepare the system message for data science code generation
            system_message = self._create_system_message()
            
            # Prepare the user message with context and prompt
            user_message = self._create_user_message(prompt, context)
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stop=None
            )
            
            # Extract generated code
            generated_content = response.choices[0].message.content
            code = self._extract_code_from_response(generated_content)
            
            # Post-process code to fix common pandas issues
            code = self._fix_pandas_boolean_issues(code)
            
            self.logger.debug(f"Generated code with {len(code)} characters")
            return code
            
        except Exception as e:
            self.logger.error(f"Error generating code: {str(e)}")
            # Fallback to template-based generation
            return self._fallback_code_generation(prompt, context)
    
    def _create_system_message(self) -> str:
        """Create the system message for the AI assistant."""
        return """You are an expert data scientist and Python programmer specializing in automated data analysis and machine learning. Your task is to generate clean, efficient, and well-documented Python code based on natural language instructions.

Key Guidelines:
1. Generate only Python code, no explanations unless requested
2. Use pandas, numpy, scikit-learn, matplotlib, and seaborn
3. Follow data science best practices
4. Handle errors gracefully with try-catch blocks
5. Store results in a variable called 'result'
6. Include relevant visualizations when appropriate
7. Use proper variable names and add brief comments
8. Ensure code is safe and doesn't perform file operations
9. Focus on the specific task requested

Available libraries:
- pandas as pd
- numpy as np
- matplotlib.pyplot as plt
- seaborn as sns
- sklearn (all modules)
- scipy.stats for statistical tests

The dataset is available as 'data' variable (pandas DataFrame).
Always store your final output in a variable called 'result'."""
    
    def _create_user_message(self, prompt: str, context: Dict[str, Any]) -> str:
        """Create the user message with context and prompt."""
        data_info = context.get('data_info', {})
        intent = context.get('intent', {})
        
        message_parts = [
            f"Dataset Information:",
            f"- Shape: {data_info.get('shape', 'Unknown')}",
            f"- Columns: {data_info.get('columns', [])}",
            f"- Data Types: {data_info.get('dtypes', {})}",
            f"- Target Column: {data_info.get('target_column', 'None')}",
            f"- Task Type: {data_info.get('task_type', 'Unknown')}",
            "",
            f"Task Category: {intent.get('category', 'general')}",
            "",
            f"User Request: {prompt}",
            "",
            "Generate Python code to accomplish this task. Remember to:",
            "1. Use 'data' as the DataFrame variable name",
            "2. Store final results in 'result' variable",
            "3. Include visualizations if appropriate",
            "4. Handle missing values appropriately",
            "5. Add brief comments explaining key steps"
        ]
        
        return "\n".join(message_parts)
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract Python code from the AI response."""
        # Remove code block markers if present
        code = response.strip()
        
        # Remove markdown code block syntax
        if code.startswith("```python"):
            code = code[9:]  # Remove ```python
        elif code.startswith("```"):
            code = code[3:]   # Remove ```
        
        if code.endswith("```"):
            code = code[:-3]  # Remove trailing ```
        
        # Clean up the code
        code = code.strip()
        
        # Ensure we have valid Python code
        if not code or len(code) < 10:
            raise ValueError("Generated code is too short or empty")
        
        return code
    
    def _fix_pandas_boolean_issues(self, code: str) -> str:
        """
        Fix common pandas Series boolean evaluation issues that cause ambiguous truth value errors.
        
        Args:
            code: Generated Python code
            
        Returns:
            Fixed Python code with safer boolean evaluations
        """
        try:
            import ast
            import re
            
            # First, try a simple text-based fix for the most common patterns
            # These are patterns that frequently cause the error in AI-generated code
            
            # Pattern 1: Direct Series check like "if data['column']:"
            code = re.sub(
                r'\bif\s+(data\[[\'"][^\'"]+[\'"]\])\s*:',
                r'if not \1.empty and \1.any():',
                code
            )
            
            # Pattern 2: DataFrame column boolean check
            code = re.sub(
                r'\bif\s+(df\[[\'"][^\'"]+[\'"]\])\s*:',
                r'if not \1.empty and \1.any():',
                code
            )
            
            # Pattern 3: Series variable check (improved pattern)
            code = re.sub(
                r'\bif\s+([a-zA-Z_][a-zA-Z0-9_]*(?:_(?:series|data|counts))?)\s*:',
                lambda m: f'if not {m.group(1)}.empty and {m.group(1)}.any():' 
                         if any(indicator in m.group(1).lower() for indicator in ['series', 'data', 'counts']) 
                         else m.group(0),
                code
            )
            
            # Pattern 4: value_counts() result check (improved)
            code = re.sub(
                r'\bif\s+([^:]+\.value_counts\(\))\s*:',
                r'if not (\1).empty:',
                code
            )
            
            # Add safety check for common Series operations that might be used in boolean context
            safety_additions = []
            
            # If code contains operations that return Series, add a comment about boolean evaluation
            if any(pattern in code for pattern in ['value_counts()', 'groupby(', 'filter(']):
                safety_additions.append(
                    "# Note: When checking pandas Series in boolean context, use .empty, .any(), .all() methods"
                )
            
            if safety_additions:
                code = '\n'.join(safety_additions) + '\n' + code
            
            self.logger.debug("Applied pandas Series safety fixes")
            return code
            
        except Exception as e:
            self.logger.warning(f"Could not apply pandas boolean fixes: {str(e)}")
            return code
    
    def _fallback_code_generation(self, prompt: str, context: Dict[str, Any]) -> str:
        """Fallback code generation when API fails."""
        self.logger.warning("Using fallback code generation")
        
        intent = context.get('intent', {})
        category = intent.get('category', 'general')
        
        # Simple template-based fallback
        if category == 'eda':
            return """
# Basic EDA Analysis
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

result = {}

# Basic info
result['shape'] = data.shape
result['columns'] = list(data.columns)
result['dtypes'] = data.dtypes.to_dict()
result['missing_values'] = data.isnull().sum().to_dict()

# Statistical summary
result['numerical_summary'] = data.describe().to_dict()

# Display basic information
print(f"Dataset shape: {data.shape}")
print(f"Missing values: {data.isnull().sum().sum()}")
print("\\nColumn data types:")
print(data.dtypes)
"""
        
        elif category == 'modeling':
            return """
# Basic modeling
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, accuracy_score

result = {}

# Prepare features and target
features = [col for col in data.columns if col != target_column]
X = data[features].select_dtypes(include=[np.number])
y = data[target_column]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
if task_type == 'regression':
    model = RandomForestRegressor(random_state=42)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    score = mean_squared_error(y_test, predictions)
    result['metric'] = 'mse'
else:
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    score = accuracy_score(y_test, predictions)
    result['metric'] = 'accuracy'

result['model'] = model
result['score'] = score
result['predictions'] = predictions
"""
        
        else:
            return """
# General analysis
result = {
    'message': 'Task completed',
    'data_shape': data.shape,
    'columns': list(data.columns)
}
print(f"Completed task: {prompt}")
"""
    
    def test_connection(self) -> bool:
        """Test the OpenAI API connection."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello, this is a test. Respond with 'OK'."}],
                max_tokens=10,
                temperature=0
            )
            return True
        except Exception as e:
            self.logger.error(f"API connection test failed: {str(e)}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models."""
        try:
            models = self.client.models.list()
            model_names = [model.id for model in models.data if 'gpt' in model.id]
            return sorted(model_names)
        except Exception as e:
            self.logger.error(f"Error fetching models: {str(e)}")
            return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]  # Default list
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Rough estimation: 1 token ≈ 0.75 words ≈ 4 characters
        return len(text) // 4
    
    def update_model(self, model: str) -> None:
        """Update the model being used."""
        self.model = model
        self.logger.info(f"Updated model to: {model}")
    
    def update_temperature(self, temperature: float) -> None:
        """Update the temperature setting."""
        if 0.0 <= temperature <= 2.0:
            self.temperature = temperature
            self.logger.info(f"Updated temperature to: {temperature}")
        else:
            raise ValueError("Temperature must be between 0.0 and 2.0")
