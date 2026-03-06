import os
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, status

from ..api.schemas import MenuGenRequest, MenuGenResponse, GeneratedCategory, GeneratedMenuItem

router = APIRouter()


@router.post("/menu-gen", response_model=MenuGenResponse)
async def generate_menu(request: MenuGenRequest) -> MenuGenResponse:
    """Generate a draft menu using an external LLM (Anthropic Claude).

    For MVP this calls the Anthropic messages API if ANTHROPIC_API_KEY is set.
    If not, it falls back to a simple heuristic response.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        # Fallback: simple static menu based on input.
        return MenuGenResponse(
            categories=[
                GeneratedCategory(
                    name=f"{request.cuisine.title()} Specials",
                    items=[
                        GeneratedMenuItem(
                            name=f"Signature {request.cuisine.title()} Dish",
                            description=f"House specialty at {request.restaurant_name}.",
                            price=18.0,
                        )
                    ],
                )
            ]
        )

    prompt = (
        "You are an expert restaurant menu designer. "
        "Return ONLY JSON matching this schema: "
        "{categories: [{name: string, items: [{name: string, description: string, price: number}]}]} "
        f"for a {request.cuisine} restaurant named {request.restaurant_name} "
        f"with a {request.price_level} price level."
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-3-opus-20240229",
                    "max_tokens": 800,
                    "messages": [
                        {"role": "user", "content": prompt},
                    ],
                },
            )
        resp.raise_for_status()
        data: Any = resp.json()
        # Very simplified extraction; in production you'd parse message content robustly.
        content = data.get("content", [])
        if not content:
            raise ValueError("Empty content from Claude")
        # Assume first block has JSON text.
        text = content[0].get("text") or content[0].get("content") or ""
        import json

        parsed = json.loads(text)
        return MenuGenResponse.model_validate(parsed)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI menu generation failed: {exc}",
        )

