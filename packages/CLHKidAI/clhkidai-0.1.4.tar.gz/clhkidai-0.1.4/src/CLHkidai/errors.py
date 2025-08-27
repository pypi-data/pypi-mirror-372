class CLHKidAIError(Exception):
    """Base error for kidai."""


class CLHKidAISafetyError(CLHKidAIError):
    """Raised when content is blocked by safe mode."""
