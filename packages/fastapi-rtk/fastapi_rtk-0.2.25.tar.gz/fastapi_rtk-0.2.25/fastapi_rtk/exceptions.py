__all__ = ["FastAPIReactToolkitException", "RolesMismatchException"]


class FastAPIReactToolkitException(Exception):
    """Base exception for FastAPI React Toolkit errors."""


class RolesMismatchException(FastAPIReactToolkitException):
    """Exception raised when the roles do not match the expected roles."""
