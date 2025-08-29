class SentorAPIError(Exception):
    """Base exception for all Sentor API errors."""

    def __init__(self, response):
        self.message = response.get("detail", "An error occurred")
        self.code = response.get("status_code", "unknown")
        super().__init__(self.message)


class RateLimitError(SentorAPIError):
    """Exception raised when API rate limit is exceeded."""

    def __init__(self, response):
        super().__init__(response)
        self.retry_after = response.get("retry_after", 60)


class AuthenticationError(SentorAPIError):
    """Exception raised when API authentication fails."""

    pass
