"""Read this second: API messages and database rows serve different purposes."""
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field as InputField
from sqlalchemy import CheckConstraint
from sqlmodel import Field, SQLModel

PositiveInt = Annotated[int, InputField(strict=True, ge=1)]


# These models describe JSON at the HTTP boundary. They do not create tables.
class OrderLineInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    menu_item_id: PositiveInt
    quantity: PositiveInt


class OrderInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    table: PositiveInt
    items: list[OrderLineInput] = InputField(min_length=1)


class OrderOutput(OrderInput):
    id: int
    status: Literal["pending"]


class AvailabilityInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    available: bool = InputField(strict=True)


# table=True adds relational mapping. Each instance corresponds to a row.
class MenuItem(SQLModel, table=True):
    __tablename__ = "menu_item"
    __table_args__ = (CheckConstraint("price >= 0"),)
    id: int | None = Field(default=None, primary_key=True)
    name: str
    price: float  # Retains the earlier example's format; money design is outside this demo.
    currency: str = "CHF"
    available: bool = True


class BarOrder(SQLModel, table=True):
    __tablename__ = "bar_order"
    __table_args__ = (CheckConstraint("table_number > 0"), CheckConstraint("status = 'pending'"))
    id: int | None = Field(default=None, primary_key=True)
    table_number: int  # The API calls this field "table".
    status: str = "pending"


class OrderLine(SQLModel, table=True):
    __tablename__ = "order_line"
    __table_args__ = (CheckConstraint("quantity > 0"),)
    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="bar_order.id", index=True)
    menu_item_id: int = Field(foreign_key="menu_item.id")
    quantity: int
