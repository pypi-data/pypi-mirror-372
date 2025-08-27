class OpenDEAError(Exception):
    """Base exception for OpenDEA."""


class InfeasibleModelError(OpenDEAError):
    """Raised when LP/QP does not converge to a feasible optimum."""


class DataValidationError(OpenDEAError):
    """Raised when inputs/outputs do not pass validation checks."""
