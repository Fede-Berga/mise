from typing import List

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
    items: List[GeneratedMenuItem]


class MenuGenResponse(BaseModel):
    categories: List[GeneratedCategory]

