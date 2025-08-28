"""Agent package initialization."""

from .copilot_agent import AutoDSCopilotAgent
from .response_handler import ResponseHandler

# Backward compatibility
CopilotAgent = AutoDSCopilotAgent

__all__ = ["AutoDSCopilotAgent", "CopilotAgent", "ResponseHandler"]
