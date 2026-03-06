
from pydantic import BaseModel


class MenuGenRequest(BaseModel):
    restaurant_name: str
    cuisine: str
    price_level: str  # e.g. "budget", "mid", "premium"


class GeneratedMenuItem(BaseModel):
    name: str
    description: str
    price: float


class GeneratedCategory(BaseModel):
    name: str
    items: list[GeneratedMenuItem]


class MenuGenResponse(BaseModel):
    categories: list[GeneratedCategory]

