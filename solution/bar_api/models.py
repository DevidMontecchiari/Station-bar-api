"""API data shapes. Existence and availability checks belong in the service."""
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field

PositiveInt = Annotated[int, Field(strict=True, ge=1)]

class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class MenuItemInput(InputModel):
    name: str = Field(min_length=1)
    price: float = Field(ge=0, strict=True, allow_inf_nan=False)
    currency: Literal["CHF"]
    available: bool = Field(strict=True)

class MenuItem(MenuItemInput):
    id: PositiveInt

class OrderLine(InputModel):
    menu_item_id: PositiveInt
    quantity: PositiveInt

class OrderInput(InputModel):
    table: PositiveInt
    items: list[OrderLine] = Field(min_length=1)

class Order(OrderInput):
    id: PositiveInt
    status: Literal["pending", "preparing", "ready", "served", "cancelled"]

class Error(InputModel):
    code: str
    message: str
