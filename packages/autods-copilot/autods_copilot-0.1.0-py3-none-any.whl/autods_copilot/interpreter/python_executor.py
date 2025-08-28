"""
Python Executor - Safe code execution engine for AutoDS.

This module provides a secure environment for executing dynamically generated
Python code with appropriate safety measures and sandboxing.
"""

import ast
import sys
import io
import traceback
import types
from typing import Any, Dict, List, Optional, Set, Tuple
from contextlib import redirect_stdout, redirect_stderr
import logging

from .security import SecurityValidator
from ..utils.logger import get_logger


class ExecutionResult:
    """Container for code execution results."""
    
    def __init__(self, success: bool, result: Any = None, error: str = None, 
                 stdout: str = "", stderr: str = ""):
        self.success = success
        self.result = result
        self.error = error
        self.stdout = stdout
        self.stderr = stderr


class PythonExecutor:
    """
    Safe Python code executor with security restrictions.
    
    This class provides a controlled environment for executing Python code
    with built-in security measures to prevent malicious operations.
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the Python executor.
        
        Args:
            timeout: Maximum execution time in seconds
        """
        self.logger = get_logger(__name__)
        self.timeout = timeout
        self.security_validator = SecurityValidator()
        
        # Define allowed built-ins for code execution
        self.allowed_builtins = {
            'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'dir', 'divmod',
            'enumerate', 'filter', 'float', 'format', 'frozenset', 'getattr',
            'hasattr', 'hex', 'id', 'int', 'isinstance', 'issubclass', 'iter',
            'len', 'list', 'map', 'max', 'min', 'oct', 'ord', 'pow', 'print',
            'range', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
            'sorted', 'str', 'sum', 'tuple', 'type', 'vars', 'zip',
            '__import__'  # Essential for importing modules
        }
        
        # Define restricted modules/functions
        self.restricted_imports = {
            'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests',
            'importlib', '__import__', 'eval', 'exec', 'compile', 'open'
        }
    
    def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        """
        Execute Python code in a controlled environment.
        
        Args:
            code: Python code to execute
            context: Execution context variables
            
        Returns:
            ExecutionResult containing the execution outcome
        """
        try:
            # Validate code security
            if not self.security_validator.validate_code(code):
                return ExecutionResult(
                    success=False,
                    error="Code failed security validation"
                )
            
            # Parse code to AST for additional validation
            try:
                parsed_ast = ast.parse(code)
                if not self._validate_ast(parsed_ast):
                    return ExecutionResult(
                        success=False,
                        error="Code contains restricted operations"
                    )
            except SyntaxError as e:
                return ExecutionResult(
                    success=False,
                    error=f"Syntax error: {str(e)}"
                )
            
            # Prepare execution environment
            exec_globals = self._create_safe_globals(context)
            exec_locals = {}
            
            # Capture stdout and stderr
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            try:
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    # Execute the code
                    exec(code, exec_globals, exec_locals)
                
                # Get captured output
                stdout_output = stdout_capture.getvalue()
                stderr_output = stderr_capture.getvalue()
                
                # Extract result (last expression value if any)
                result = exec_locals.get('result') or exec_locals.get('_')
                
                self.logger.debug("Code executed successfully")
                return ExecutionResult(
                    success=True,
                    result=result,
                    stdout=stdout_output,
                    stderr=stderr_output
                )
                
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                
                # Provide helpful messages for common pandas errors
                if isinstance(e, ValueError) and "truth value of a Series is ambiguous" in str(e):
                    error_msg += "\n💡 Tip: When checking pandas Series in boolean context, use .empty, .any(), .all(), or .bool() methods"
                    error_msg += "\n   Example: 'if not series.empty:' instead of 'if series:'"
                
                self.logger.warning(f"Code execution error: {error_msg}")
                
                return ExecutionResult(
                    success=False,
                    error=error_msg,
                    stdout=stdout_capture.getvalue(),
                    stderr=stderr_capture.getvalue()
                )
        
        except Exception as e:
            self.logger.error(f"Execution failed: {str(e)}")
            return ExecutionResult(
                success=False,
                error=f"Execution failed: {str(e)}"
            )
    
    def _create_safe_globals(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a safe global environment for code execution.
        
        Args:
            context: Additional context variables to include
            
        Returns:
            Safe globals dictionary
        """
        # Handle __builtins__ which can be either dict or module
        if isinstance(__builtins__, dict):
            builtins_source = __builtins__
        else:
            builtins_source = __builtins__.__dict__
        
        # Start with minimal builtins
        safe_builtins = {name: builtins_source[name] 
                        for name in self.allowed_builtins 
                        if name in builtins_source}
        
        safe_globals = {
            '__builtins__': safe_builtins,
            '__name__': '__main__',
            '__doc__': None,
        }
        
        # Add safe modules
        safe_modules = self._get_safe_modules()
        safe_globals.update(safe_modules)
        
        # Add context variables if provided
        if context:
            for key, value in context.items():
                if self._is_safe_variable(key, value):
                    safe_globals[key] = value
        
        return safe_globals
    
    def _get_safe_modules(self) -> Dict[str, Any]:
        """Get dictionary of safe modules for execution."""
        safe_modules = {}
        
        try:
            # Data science libraries
            import pandas as pd
            import numpy as np
            import matplotlib.pyplot as plt
            import seaborn as sns
            from sklearn import metrics, preprocessing, model_selection
            import warnings
            
            safe_modules.update({
                'pd': pd,
                'pandas': pd,
                'np': np,
                'numpy': np,
                'plt': plt,
                'matplotlib': __import__('matplotlib'),
                'sns': sns,
                'seaborn': sns,
                'metrics': metrics,
                'preprocessing': preprocessing,
                'model_selection': model_selection,
                'warnings': warnings
            })
            
        except ImportError as e:
            self.logger.warning(f"Some modules not available: {str(e)}")
        
        return safe_modules
    
    def _validate_ast(self, node: ast.AST) -> bool:
        """
        Validate AST for security restrictions.
        
        Args:
            node: AST node to validate
            
        Returns:
            True if safe, False otherwise
        """
        for child in ast.walk(node):
            # Check for restricted operations
            if isinstance(child, ast.Import):
                for alias in child.names:
                    if alias.name in self.restricted_imports:
                        return False
            
            elif isinstance(child, ast.ImportFrom):
                if child.module in self.restricted_imports:
                    return False
            
            elif isinstance(child, (ast.Call)):
                # Check function calls
                if isinstance(child.func, ast.Name):
                    if child.func.id in self.restricted_imports:
                        return False
                elif isinstance(child.func, ast.Attribute):
                    # Check for dangerous method calls
                    if child.func.attr in ['system', 'popen', 'exec', 'eval']:
                        return False
            
            elif isinstance(child, ast.Attribute):
                # Check for dangerous attributes
                if child.attr in ['__class__', '__bases__', '__subclasses__']:
                    return False
        
        return True
    
    def _is_safe_variable(self, name: str, value: Any) -> bool:
        """
        Check if a variable is safe to include in execution context.
        
        Args:
            name: Variable name
            value: Variable value
            
        Returns:
            True if safe, False otherwise
        """
        # Don't allow private/magic variables
        if name.startswith('_'):
            return False
        
        # Don't allow certain types
        unsafe_types = (types.ModuleType, types.FunctionType, types.MethodType)
        if isinstance(value, unsafe_types):
            return False
        
        return True
