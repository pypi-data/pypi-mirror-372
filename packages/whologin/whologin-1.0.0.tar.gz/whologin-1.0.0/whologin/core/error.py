class WhoLoginAPIError(Exception):
    """Custom error raised when API returns { success: false }."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
