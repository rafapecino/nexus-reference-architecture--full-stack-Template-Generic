# Errores comunes y un AppError base para la aplicación.
# Ayuda a API (convertir a HTTP 400/404) y workers a manejar errores de forma consistente.


class AppError(Exception):
    """Base class for application errors."""


class NotFoundError(AppError):
    """Resource not found."""


class ValidationError(AppError):
    """Invalid input."""
