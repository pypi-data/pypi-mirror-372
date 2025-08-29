class GitOperationError(Exception):
    """Exception raised when a Git operation fails."""

    def __init__(self, message: str, operation: str = None):
        """
        Initialize the GitOperationError.

        Args:
            message: The error message.
            operation: The specific git operation that failed (optional).
        """
        self.operation = operation
        if operation:
            message = f"Git {operation} failed: {message}"
        super().__init__(message)
