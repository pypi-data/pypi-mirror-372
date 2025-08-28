"""
AutoDS Copilot - GenAI-powered agent-based tool for automated data science workflows.

A Python package that automates exploratory data analysis, feature engineering, 
and machine learning model development through natural language prompts with
OpenAI GPT-4o integration.
"""

__version__ = "0.1.0"
__author__ = "MaheshKumarsg036"
__email__ = "contact@autods-copilot.com"

from .agent.copilot_agent import AutoDSCopilotAgent
from .utils.config import Config
from .utils.logger import get_logger

# Backward compatibility
CopilotAgent = AutoDSCopilotAgent

__all__ = [
    "AutoDSCopilotAgent",
    "CopilotAgent",  # Backward compatibility
    "Config", 
    "get_logger"
]
