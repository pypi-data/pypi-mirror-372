"""Basic data types."""

from datetime import date
from typing import Any, NewType, TypedDict

from kaiju_models import BooleanField, DateField, EmailField, IntegerField, JsonMapField, Model, StringField


__all__ = ["CustomerId", "Customer", "CustomerUpdate", "CustomerCreate", "SearchFilter"]

CustomerId = NewType("CustomerId", int)


class SearchFilter(TypedDict):
    """UI search filter data."""

    id: str
    kind: str
    condition: str
    value: Any


class CustomerUpdate(Model["CustomerUpdate.Fields"]):
    """Data to update customer."""

    class Fields(Model.Fields):
        blocked: bool = BooleanField()
        email: str | None = EmailField()
        email_confirmed: bool = BooleanField()
        profile: dict[str, Any] = JsonMapField()  # profile data is dynamic and determined by settings
        meta: dict[str, Any] = JsonMapField()  # meta is dynamic and determined by settings
        subscriptions: dict[str, Any] = JsonMapField()  # subs data is dynamic and determined by settings
        loyalty_enabled: bool = BooleanField()


class CustomerCreate(Model["CustomerCreate.Fields"]):
    """Data to create a new customer."""

    class Fields(Model.Fields):
        phone: str = StringField(pattern="7[0-9]{10}", required=True)
        source_id: str | None = StringField()
        email: str | None = EmailField()
        email_confirmed: bool = BooleanField(default=False)
        profile: dict[str, Any] = JsonMapField()  # profile data is dynamic and determined by settings
        meta: dict[str, Any] = JsonMapField()  # meta is dynamic and determined by settings
        subscriptions: dict[str, Any] = JsonMapField()  # subs data is dynamic and determined by settings
        loyalty_enabled: bool = BooleanField(default=False)
        accept_tender_offer: bool = BooleanField(default=True)
        created: date = DateField()  # TODO: remove after loading the initial db


class Customer(Model["Customer.Fields"]):
    """Customer data"""

    class Fields(Model.Fields):
        id: CustomerId = IntegerField()
        phone: str = StringField()
        source_id: str | None = StringField()
        email: str | None = EmailField()
        email_confirmed: bool = BooleanField(default=False)
        blocked: bool = BooleanField(default=False)
        profile: dict[str, Any] = JsonMapField()  # profile data is dynamic and determined by settings
        meta: dict[str, Any] = JsonMapField()  # meta is dynamic and determined by settings
        subscriptions: dict[str, Any] = JsonMapField()  # subs data is dynamic and determined by settings
        loyalty_enabled: bool = BooleanField(default=False)
        created: date = DateField()
        accept_tender_offer: bool = BooleanField(default=True)
