"""
AutoDSCopilotAgent - Main orchestrator for AutoDS workflows with LLM integration.

This module contains the primary agent that interprets natural language prompts
and coordinates various data science operations with OpenAI GPT-4o integration.
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd
import logging
from pathlib import Path

from ..interpreter.python_executor import PythonExecutor
from ..modules.eda.analyzer import EDAAnalyzer
from ..modules.encoding.categorical import CategoricalEncoder
from ..modules.modeling.classifier import ClassificationManager
from ..modules.modeling.regressor import RegressionManager
from ..prompts.prompt_manager import PromptManager
from ..utils.logger import get_logger
from ..utils.validators import DataValidator
from .response_handler import ResponseHandler

# Import LLM adapters (with fallback if not available)
try:
    from ..llm.openai_adapter import OpenAIAdapter
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# Import enhanced NLP processor
try:
    from ..nlp.query_processor import EnhancedQueryProcessor
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False


class AutoDSCopilotAgent:
    """
    Main agent for AutoDS Copilot that interprets natural language prompts
    and orchestrates data science workflows with LLM integration.
    
    Attributes:
        data (pd.DataFrame): The loaded dataset
        target_column (str): Name of the target variable
        feature_columns (List[str]): Names of feature variables
        task_type (str): 'classification' or 'regression'
        history (List[Dict]): Execution history
        llm_adapter: OpenAI adapter for code generation
    """
    
    def __init__(self, config_path: Optional[str] = None, 
                 openai_api_key: Optional[str] = None,
                 llm_model: str = "gpt-4o"):
        """
        Initialize the AutoDSCopilotAgent.
        
        Args:
            config_path: Path to configuration file (optional)
            openai_api_key: OpenAI API key for LLM integration (optional)
            llm_model: LLM model to use (default: gpt-4o)
        """
        self.logger = get_logger(__name__)
        self.data: Optional[pd.DataFrame] = None
        self.target_column: Optional[str] = None
        self.feature_columns: List[str] = []
        self.task_type: Optional[str] = None
        self.history: List[Dict[str, Any]] = []
        
        # Initialize LLM adapter if API key provided
        self.llm_adapter: Optional[OpenAIAdapter] = None
        self.use_llm = False
        
        if openai_api_key and LLM_AVAILABLE:
            try:
                self.llm_adapter = OpenAIAdapter(
                    api_key=openai_api_key,
                    model=llm_model
                )
                self.use_llm = True
                self.logger.info("🤖 LLM integration enabled with OpenAI GPT-4o")
            except Exception as e:
                self.logger.warning(f"Failed to initialize LLM adapter: {str(e)}")
                self.logger.info("Falling back to template-based code generation")
        elif openai_api_key and not LLM_AVAILABLE:
            self.logger.warning("OpenAI package not installed. Install with: pip install openai")
            self.logger.info("Falling back to template-based code generation")
        else:
            self.logger.info("No OpenAI API key provided. Using template-based code generation")
        
        # Initialize components
        self.executor = PythonExecutor()
        self.eda_analyzer = EDAAnalyzer()
        self.categorical_encoder = CategoricalEncoder()
        self.classification_manager = ClassificationManager()
        self.regression_manager = RegressionManager()
        self.prompt_manager = PromptManager()
        self.response_handler = ResponseHandler()
        self.data_validator = DataValidator()
        
        # Initialize enhanced query processor
        if NLP_AVAILABLE:
            self.query_processor = EnhancedQueryProcessor()
            self.logger.info("🧠 Enhanced NLP query processor enabled")
        else:
            self.query_processor = None
            self.logger.info("Using basic intent parsing")
        
        self.logger.info("AutoDSCopilotAgent initialized successfully")
    
    def load_csv(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """
        Load data from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            **kwargs: Additional arguments for pd.read_csv()
            
        Returns:
            Loaded DataFrame
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file cannot be parsed
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            self.data = pd.read_csv(file_path, **kwargs)
            self.logger.info(f"Successfully loaded data from {file_path}")
            self.logger.info(f"Data shape: {self.data.shape}")
            
            # Perform basic validation
            self.data_validator.validate_dataframe(self.data)
            
            return self.data
            
        except Exception as e:
            self.logger.error(f"Error loading CSV file: {str(e)}")
            raise
    
    def load_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Load data from a pandas DataFrame.
        
        Args:
            df: Input DataFrame
            
        Returns:
            The loaded DataFrame
            
        Raises:
            ValueError: If the DataFrame is invalid
        """
        try:
            if not isinstance(df, pd.DataFrame):
                raise ValueError("Input must be a pandas DataFrame")
            
            self.data = df.copy()
            self.logger.info(f"Successfully loaded DataFrame with shape: {self.data.shape}")
            
            # Perform basic validation
            self.data_validator.validate_dataframe(self.data)
            
            return self.data
            
        except Exception as e:
            self.logger.error(f"Error loading DataFrame: {str(e)}")
            raise
    
    def run(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a natural language prompt and return results.
        
        Args:
            prompt: Natural language instruction
            context: Additional context for the prompt
            
        Returns:
            Dictionary containing execution results
            
        Raises:
            ValueError: If no data is loaded or prompt is invalid
        """
        if self.data is None:
            raise ValueError("No data loaded. Please use load_csv() or load_dataframe() first.")
        
        try:
            self.logger.info(f"Processing prompt: {prompt}")
            
            # Parse the prompt to understand intent
            intent = self._parse_intent(prompt)
            
            # Generate appropriate code based on intent
            code = self.generate_code(prompt, intent, context)
            
            # Execute the generated code
            result = self.execute_code(code, context)
            
            # Process and format the response
            response = self.response_handler.format_response(result, intent)
            
            # Store in history
            self._add_to_history(prompt, intent, code, response)
            
            self.logger.info("Prompt execution completed successfully")
            return response
            
        except Exception as e:
            self.logger.error(f"Error executing prompt: {str(e)}")
            raise
    
    def generate_code(self, prompt: str, intent: Dict[str, Any], 
                     context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate Python code based on the prompt and intent.
        
        Args:
            prompt: Original natural language prompt
            intent: Parsed intent dictionary
            context: Additional context
            
        Returns:
            Generated Python code as string
        """
        try:
            # Use LLM if available and enabled
            if self.use_llm and self.llm_adapter:
                self.logger.debug("Using LLM for code generation")
                
                # Prepare context for LLM
                llm_context = {
                    'data_info': self._get_data_info(),
                    'intent': intent,
                    'context': context or {}
                }
                
                # Generate code using LLM
                try:
                    code = self.llm_adapter.generate_code(prompt, llm_context)
                    self.logger.debug(f"LLM generated code with {len(code)} characters")
                    return code
                except Exception as e:
                    self.logger.warning(f"LLM code generation failed: {str(e)}")
                    self.logger.info("Falling back to template-based generation")
            
            # Fallback to template-based generation
            self.logger.debug("Using template-based code generation")
            
            # Use enhanced query processor if available
            if self.query_processor:
                query_intent = self.query_processor.process_query(
                    prompt, 
                    {'data_info': self._get_data_info()}
                )
                
                if query_intent.confidence >= 0.7:
                    self.logger.debug(f"Enhanced NLP: {query_intent.primary_action} (confidence: {query_intent.confidence:.2f})")
                    code = self.query_processor.generate_response_template(
                        query_intent, 
                        {'data_info': self._get_data_info(), 'context': context or {}}
                    )
                    return code
            
            # Get appropriate prompt template
            template = self.prompt_manager.get_template(intent['category'])
            
            # Prepare template variables
            template_vars = {
                'data_info': self._get_data_info(),
                'prompt': prompt,
                'intent': intent,
                'context': context or {}
            }
            
            # Generate code using the template
            code = template.format(**template_vars)
            
            self.logger.debug(f"Generated code for intent '{intent['category']}'")
            return code
            
        except Exception as e:
            self.logger.error(f"Error generating code: {str(e)}")
            raise
    
    def execute_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Safely execute generated Python code.
        
        Args:
            code: Python code to execute
            context: Execution context variables
            
        Returns:
            Execution result
        """
        try:
            # Prepare execution context
            exec_context = {
                'data': self.data,
                'pd': pd,
                'np': __import__('numpy'),
                'plt': __import__('matplotlib.pyplot'),
                'sns': __import__('seaborn'),
                'agent': self
            }
            
            if context:
                exec_context.update(context)
            
            # Execute code safely
            result = self.executor.execute(code, exec_context)
            
            self.logger.debug("Code execution completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing code: {str(e)}")
            raise
    
    def get_data_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the loaded data.
        
        Returns:
            Dictionary containing data information
        """
        if self.data is None:
            return {}
        
        return self._get_data_info()
    
    def set_target(self, column_name: str) -> None:
        """
        Set the target column for modeling.
        
        Args:
            column_name: Name of the target column
            
        Raises:
            ValueError: If column doesn't exist in the data
        """
        if self.data is None:
            raise ValueError("No data loaded")
        
        if column_name not in self.data.columns:
            raise ValueError(f"Column '{column_name}' not found in data")
        
        self.target_column = column_name
        self.feature_columns = [col for col in self.data.columns if col != column_name]
        
        # Determine task type
        self.task_type = self._determine_task_type(self.data[column_name])
        
        self.logger.info(f"Target set to '{column_name}', task type: {self.task_type}")
    
    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get the execution history.
        
        Returns:
            List of execution history entries
        """
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Clear the execution history."""
        self.history.clear()
        self.logger.info("Execution history cleared")
    
    def _parse_intent(self, prompt: str) -> Dict[str, Any]:
        """
        Parse the user's intent from the prompt.
        
        Args:
            prompt: Natural language prompt
            
        Returns:
            Dictionary containing parsed intent
        """
        prompt_lower = prompt.lower()
        
        # Define intent keywords
        intent_keywords = {
            'eda': ['explore', 'analyze', 'eda', 'exploratory', 'summary', 'describe'],
            'visualization': ['plot', 'visualize', 'chart', 'graph', 'heatmap', 'histogram'],
            'encoding': ['encode', 'categorical', 'onehot', 'ordinal', 'label'],
            'modeling': ['model', 'train', 'predict', 'classification', 'regression'],
            'evaluation': ['evaluate', 'metrics', 'performance', 'accuracy', 'score']
        }
        
        # Determine primary intent
        intent_scores = {}
        for category, keywords in intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in prompt_lower)
            if score > 0:
                intent_scores[category] = score
        
        if not intent_scores:
            primary_intent = 'general'
        else:
            primary_intent = max(intent_scores, key=intent_scores.get)
        
        return {
            'category': primary_intent,
            'keywords': intent_keywords.get(primary_intent, []),
            'confidence': intent_scores.get(primary_intent, 0),
            'raw_prompt': prompt
        }
    
    def _get_data_info(self) -> Dict[str, Any]:
        """Get detailed information about the current dataset."""
        if self.data is None:
            return {}
        
        return {
            'shape': self.data.shape,
            'columns': list(self.data.columns),
            'dtypes': self.data.dtypes.to_dict(),
            'null_counts': self.data.isnull().sum().to_dict(),
            'target_column': self.target_column,
            'feature_columns': self.feature_columns,
            'task_type': self.task_type,
            'memory_usage': self.data.memory_usage(deep=True).sum()
        }
    
    def set_llm_model(self, model: str) -> None:
        """
        Update the LLM model being used.
        
        Args:
            model: Model name (e.g., 'gpt-4o', 'gpt-4o-mini')
        """
        if self.use_llm and self.llm_adapter:
            self.llm_adapter.update_model(model)
            self.logger.info(f"Updated LLM model to: {model}")
        else:
            self.logger.warning("LLM adapter not available")
    
    def set_llm_temperature(self, temperature: float) -> None:
        """
        Update the LLM temperature setting.
        
        Args:
            temperature: Temperature value (0.0-2.0)
        """
        if self.use_llm and self.llm_adapter:
            self.llm_adapter.update_temperature(temperature)
            self.logger.info(f"Updated LLM temperature to: {temperature}")
        else:
            self.logger.warning("LLM adapter not available")
    
    def test_llm_connection(self) -> bool:
        """
        Test the LLM connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        if self.use_llm and self.llm_adapter:
            return self.llm_adapter.test_connection()
        else:
            self.logger.warning("LLM adapter not available")
            return False
    
    def get_llm_info(self) -> Dict[str, Any]:
        """
        Get information about the current LLM configuration.
        
        Returns:
            Dictionary with LLM configuration details
        """
        if self.use_llm and self.llm_adapter:
            return {
                'enabled': True,
                'model': self.llm_adapter.model,
                'temperature': self.llm_adapter.temperature,
                'max_tokens': self.llm_adapter.max_tokens
            }
        else:
            return {
                'enabled': False,
                'reason': 'No API key provided or OpenAI package not installed'
            }
    
    def _determine_task_type(self, target_series: pd.Series) -> str:
        """
        Determine if the task is classification or regression.
        
        Args:
            target_series: Target variable series
            
        Returns:
            'classification' or 'regression'
        """
        if target_series.dtype in ['object', 'category', 'bool']:
            return 'classification'
        elif target_series.dtype in ['int64', 'float64']:
            unique_ratio = target_series.nunique() / len(target_series)
            if unique_ratio < 0.05:  # Less than 5% unique values
                return 'classification'
            else:
                return 'regression'
        else:
            return 'classification'  # Default fallback
    
    def _add_to_history(self, prompt: str, intent: Dict[str, Any], 
                       code: str, response: Dict[str, Any]) -> None:
        """Add an execution entry to history."""
        entry = {
            'timestamp': pd.Timestamp.now(),
            'prompt': prompt,
            'intent': intent,
            'code': code,
            'response': response,
            'success': response.get('success', False)
        }
        self.history.append(entry)
