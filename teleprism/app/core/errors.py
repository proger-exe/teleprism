"""Domain exceptions for TelePrism."""


class TelePrismError(Exception):
    """Base application error."""


class ValidationError(TelePrismError):
    """Raised when user input is invalid."""


class TransitionError(TelePrismError):
    """Raised when an order status transition is not allowed."""


class PaymentProviderError(TelePrismError):
    """Raised when CryptAPI cannot complete a provider operation."""


class NotFoundError(TelePrismError):
    """Raised when an entity is not found."""


class PermissionDeniedError(TelePrismError):
    """Raised when a user role cannot perform an action."""
