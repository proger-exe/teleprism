"""CryptAPI typed payloads."""

from pydantic import BaseModel, Field


class CreateAddressResponse(BaseModel):
    """CryptAPI address creation response."""

    address_in: str
    address_out: str | None = None
    callback_url: str
    minimum_transaction_coin: str | int | float | None = None
    status: str


class TransactionItem(BaseModel):
    """CryptAPI log transaction item."""

    txid_in: str
    txid_out: str | None = None
    value_coin: str = "0"
    value_forwarded_coin: str | None = None
    fee_coin: str | None = None
    confirmations: int = 0
    pending: bool = False
    confirmed: bool = False
    raw: dict[str, object] = Field(default_factory=dict)


class LogsResponse(BaseModel):
    """CryptAPI logs response."""

    callbacks: list[TransactionItem] = Field(default_factory=list)
