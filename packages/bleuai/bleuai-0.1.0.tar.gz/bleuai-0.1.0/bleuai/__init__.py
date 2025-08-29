"""
Bleu AI Python SDK

A Python client for interacting with Bleu AI workflows.
"""

from .client import BleuAI
from .exceptions import (
    BleuAIError,
    AuthenticationError,
    WorkflowNotFoundError,
    InsufficientCreditsError,
    WorkflowExecutionError
)
from .types import WorkflowResult, WorkflowStatus

__version__ = "0.1.0"
__all__ = [
    "BleuAI",
    "BleuAIError",
    "AuthenticationError",
    "WorkflowNotFoundError",
    "InsufficientCreditsError",
    "WorkflowExecutionError",
    "WorkflowResult",
    "WorkflowStatus"
]
