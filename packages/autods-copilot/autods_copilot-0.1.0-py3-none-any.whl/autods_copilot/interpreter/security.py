"""
Security Validator - Code security validation for AutoDS.

This module provides security validation for dynamically generated code
to prevent malicious operations and ensure safe execution.
"""

import ast
import re
from typing import List, Set, Pattern
from ..utils.logger import get_logger


class SecurityValidator:
    """
    Validates Python code for security risks before execution.
    
    This class implements multiple layers of security validation to prevent
    execution of potentially malicious or dangerous code.
    """
    
    def __init__(self):
        """Initialize the SecurityValidator."""
        self.logger = get_logger(__name__)
        
        # Define dangerous patterns
        self.dangerous_patterns = [
            # System operations
            r'\bos\.',
            r'\bsys\.',
            r'\bsubprocess\.',
            r'\bsocket\.',
            r'\burllib\.',
            r'\brequests\.',
            
            # File operations
            r'\bopen\s*\(',
            r'\bfile\s*\(',
            r'\.read\s*\(',
            r'\.write\s*\(',
            r'\.delete\s*\(',
            
            # Execution functions
            r'\beval\s*\(',
            r'\bexec\s*\(',
            r'\bcompile\s*\(',
            r'\b__import__\s*\(',
            
            # Network operations
            r'\bconnect\s*\(',
            r'\bbind\s*\(',
            r'\blisten\s*\(',
            
            # Process operations
            r'\.system\s*\(',
            r'\.popen\s*\(',
            r'\.spawn\s*\(',
            
            # Magic methods that could be dangerous
            r'__class__',
            r'__bases__',
            r'__subclasses__',
            r'__globals__',
            r'__dict__',
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) 
                                 for pattern in self.dangerous_patterns]
        
        # Define allowed imports
        self.allowed_imports = {
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'sklearn',
            'scipy', 'statsmodels', 'plotly', 'warnings', 'math',
            'random', 'datetime', 'json', 'csv', 'itertools',
            'collections', 'functools', 'operator'
        }
        
        # Define dangerous imports
        self.dangerous_imports = {
            'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests',
            'importlib', 'ctypes', 'multiprocessing', 'threading',
            'tempfile', 'shutil', 'glob', 'pickle', 'marshal'
        }
    
    def validate_code(self, code: str) -> bool:
        """
        Validate Python code for security risks.
        
        Args:
            code: Python code string to validate
            
        Returns:
            True if code is safe, False otherwise
        """
        try:
            # Check for dangerous patterns
            if not self._check_patterns(code):
                self.logger.warning("Code contains dangerous patterns")
                return False
            
            # Parse and validate AST
            if not self._validate_ast_security(code):
                self.logger.warning("Code failed AST security validation")
                return False
            
            # Check imports
            if not self._validate_imports(code):
                self.logger.warning("Code contains dangerous imports")
                return False
            
            # Additional validations
            if not self._validate_complexity(code):
                self.logger.warning("Code is too complex")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating code: {str(e)}")
            return False
    
    def _check_patterns(self, code: str) -> bool:
        """
        Check code against dangerous regex patterns.
        
        Args:
            code: Code to check
            
        Returns:
            True if safe, False if dangerous patterns found
        """
        for pattern in self.compiled_patterns:
            if pattern.search(code):
                return False
        return True
    
    def _validate_ast_security(self, code: str) -> bool:
        """
        Validate code using AST analysis.
        
        Args:
            code: Code to validate
            
        Returns:
            True if safe, False otherwise
        """
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Check for dangerous node types
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.dangerous_imports:
                            return False
                        if alias.name not in self.allowed_imports:
                            # Allow specific submodules of allowed packages
                            root_module = alias.name.split('.')[0]
                            if root_module not in self.allowed_imports:
                                return False
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module in self.dangerous_imports:
                        return False
                    if node.module:
                        # Allow sklearn submodules explicitly
                        if node.module.startswith('sklearn.'):
                            pass  # sklearn submodules are allowed
                        elif node.module.split('.')[0] not in self.allowed_imports:
                            return False
                
                elif isinstance(node, ast.Call):
                    # Check for dangerous function calls
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['eval', 'exec', 'compile', '__import__']:
                            return False
                    elif isinstance(node.func, ast.Attribute):
                        if node.func.attr in ['system', 'popen', 'exec', 'eval']:
                            return False
                
                elif isinstance(node, ast.Attribute):
                    # Check for dangerous attribute access
                    if node.attr in ['__class__', '__bases__', '__subclasses__',
                                   '__globals__', '__dict__', '__code__']:
                        return False
                
                elif isinstance(node, ast.FunctionDef):
                    # Restrict certain function names
                    if node.name.startswith('__') and node.name.endswith('__'):
                        return False
            
            return True
            
        except SyntaxError:
            return False
    
    def _validate_imports(self, code: str) -> bool:
        """
        Validate import statements in the code.
        
        Args:
            code: Code to validate
            
        Returns:
            True if imports are safe, False otherwise
        """
        # Extract import statements using regex
        import_patterns = [
            r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
            r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import'
        ]
        
        for pattern in import_patterns:
            matches = re.finditer(pattern, code, re.MULTILINE)
            for match in matches:
                module_name = match.group(1)
                root_module = module_name.split('.')[0]
                
                if root_module in self.dangerous_imports:
                    return False
                if root_module not in self.allowed_imports:
                    return False
        
        return True
    
    def _validate_complexity(self, code: str) -> bool:
        """
        Validate code complexity to prevent resource abuse.
        
        Args:
            code: Code to validate
            
        Returns:
            True if complexity is acceptable, False otherwise
        """
        # Check code length
        if len(code) > 10000:  # 10KB limit
            return False
        
        # Check number of lines
        lines = code.split('\n')
        if len(lines) > 500:  # 500 lines limit
            return False
        
        # Check for deeply nested structures
        try:
            tree = ast.parse(code)
            max_depth = self._calculate_ast_depth(tree)
            if max_depth > 20:  # Maximum nesting depth
                return False
        except:
            return False
        
        return True
    
    def _calculate_ast_depth(self, node: ast.AST, depth: int = 0) -> int:
        """
        Calculate the maximum depth of an AST.
        
        Args:
            node: AST node
            depth: Current depth
            
        Returns:
            Maximum depth found
        """
        max_depth = depth
        
        for child in ast.iter_child_nodes(node):
            child_depth = self._calculate_ast_depth(child, depth + 1)
            max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def get_security_report(self, code: str) -> dict:
        """
        Generate a detailed security report for the code.
        
        Args:
            code: Code to analyze
            
        Returns:
            Dictionary containing security analysis results
        """
        report = {
            'is_safe': True,
            'issues': [],
            'warnings': [],
            'complexity': {
                'lines': len(code.split('\n')),
                'characters': len(code),
                'ast_depth': 0
            }
        }
        
        try:
            # Check patterns
            for i, pattern in enumerate(self.compiled_patterns):
                if pattern.search(code):
                    report['is_safe'] = False
                    report['issues'].append(f"Dangerous pattern found: {self.dangerous_patterns[i]}")
            
            # AST analysis
            try:
                tree = ast.parse(code)
                report['complexity']['ast_depth'] = self._calculate_ast_depth(tree)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name in self.dangerous_imports:
                                report['is_safe'] = False
                                report['issues'].append(f"Dangerous import: {alias.name}")
            except SyntaxError as e:
                report['is_safe'] = False
                report['issues'].append(f"Syntax error: {str(e)}")
            
            # Complexity checks
            if report['complexity']['lines'] > 500:
                report['warnings'].append("Code is very long (>500 lines)")
            if report['complexity']['characters'] > 10000:
                report['warnings'].append("Code is very large (>10KB)")
            if report['complexity']['ast_depth'] > 20:
                report['warnings'].append("Code has deep nesting (>20 levels)")
            
        except Exception as e:
            report['is_safe'] = False
            report['issues'].append(f"Analysis error: {str(e)}")
        
        return report
