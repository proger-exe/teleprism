"""Shared enumerations for TelePrism."""

from enum import StrEnum


class UserRole(StrEnum):
    """Telegram user role stored in SQLite."""

    USER = "USER"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"
    OWNER = "OWNER"


class OrderStatus(StrEnum):
    """Order lifecycle status."""

    DRAFT = "DRAFT"
    AWAITING_PAYMENT = "AWAITING_PAYMENT"
    PAYMENT_DETECTED = "PAYMENT_DETECTED"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    QUEUED = "QUEUED"
    ASSIGNED = "ASSIGNED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"
    ISSUE = "ISSUE"
    REFUND_REQUIRED = "REFUND_REQUIRED"


class PaymentStatus(StrEnum):
    """CryptAPI payment status."""

    CREATING = "CREATING"
    WAITING = "WAITING"
    DETECTED = "DETECTED"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    CONFIRMED = "CONFIRMED"
    OVERPAID = "OVERPAID"
    LATE_PAID = "LATE_PAID"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"


class TicketStatus(StrEnum):
    """Support ticket status."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"


class SessionState(StrEnum):
    """Persistent conversation state."""

    WAITING_RECIPIENT = "WAITING_RECIPIENT"
    WAITING_CUSTOM_STARS = "WAITING_CUSTOM_STARS"
    WAITING_SUPPORT_MESSAGE = "WAITING_SUPPORT_MESSAGE"
    WAITING_MANAGER_COMMENT = "WAITING_MANAGER_COMMENT"
    WAITING_PROOF = "WAITING_PROOF"
    WAITING_ADMIN_VALUE = "WAITING_ADMIN_VALUE"
