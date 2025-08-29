"""
Exception classes for the Bleu AI SDK.
"""


class BleuAIError(Exception):
    """Base exception for all Bleu AI SDK errors."""
    pass


class AuthenticationError(BleuAIError):
    """Raised when authentication fails."""
    pass


class WorkflowNotFoundError(BleuAIError):
    """Raised when a workflow cannot be found."""
    pass


class InsufficientCreditsError(BleuAIError):
    """Raised when the user has insufficient credits to run a workflow."""
    pass


class WorkflowExecutionError(BleuAIError):
    """Raised when a workflow execution fails."""
    pass


class ConnectionError(BleuAIError):
    """Raised when connection to Bleu AI services fails."""
    pass
