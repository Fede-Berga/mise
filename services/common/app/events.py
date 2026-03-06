"""NATS JetStream event publishing for Mise services.

Provides publish_event for order-service and other publishers.
Stream bootstrap ensures the MISE stream exists with subjects mise.>.
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
from collections.abc import Awaitable
from typing import Any

import nats

from common.app.config import get_settings

logger = logging.getLogger(__name__)

STREAM_NAME = "MISE"
STREAM_SUBJECTS = ["mise.>"]


def _run_async(coro: Awaitable[Any]) -> Any:
    """Run async coroutine from sync context.

    If called from a running event loop, execute the coroutine in a dedicated
    thread with its own loop to avoid ``run_until_complete`` runtime errors.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    result: dict[str, Any] = {}
    error: dict[str, BaseException] = {}

    def _runner() -> None:
        try:
            result["value"] = asyncio.run(coro)
        except BaseException as exc:  # noqa: BLE001
            error["value"] = exc

    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()
    thread.join()

    if "value" in error:
        raise error["value"]
    return result.get("value")


async def _ensure_stream(nc: nats.NATS) -> None:
    """Create MISE stream if it does not exist."""
    try:
        js = nc.jetstream()
        await js.add_stream(
            name=STREAM_NAME,
            subjects=STREAM_SUBJECTS,
            storage="file",
        )
        logger.debug("NATS stream %s ensured", STREAM_NAME)
    except Exception as e:
        if "already in use" in str(e).lower() or "stream name already in use" in str(e).lower():
            logger.debug("Stream %s already exists", STREAM_NAME)
        else:
            raise


def publish_event(subject: str, payload: dict) -> None:
    """Publish a JSON event to NATS JetStream.

    Uses a fresh connection per call for simplicity (MVP).
    For high throughput, consider a connection pool.
    """
    settings = get_settings()
    url = settings.nats_url

    async def _publish() -> None:
        nc = await nats.connect(servers=[url])
        try:
            js = nc.jetstream()
            await _ensure_stream(nc)
            data = json.dumps(payload).encode("utf-8")
            ack = await js.publish(subject, data)
            logger.debug("Published %s seq=%s", subject, ack.seq)
        finally:
            await nc.drain()
            nc.close()

    try:
        _run_async(_publish())
    except Exception as e:
        logger.warning("Failed to publish %s: %s", subject, e, exc_info=True)


async def subscribe_orders_placed(callback) -> None:  # type: ignore[no-untyped-def]
    """Subscribe to mise.orders.placed and invoke callback for each message.

    callback(order_payload: dict) is called with the parsed JSON payload.
    Runs until cancelled. Use in a FastAPI lifespan background task.
    """
    settings = get_settings()
    nc = await nats.connect(servers=[settings.nats_url])
    js = nc.jetstream()
    await _ensure_stream(nc)

    async def handler(msg):
        try:
            data = json.loads(msg.data.decode("utf-8"))
            await callback(data)
            await msg.ack()
        except Exception as e:
            logger.exception("Error handling mise.orders.placed: %s", e)
            await msg.nak()

    sub = await js.subscribe("mise.orders.placed", cb=handler, durable="kitchen-orders-consumer")
    logger.debug("Subscribed to mise.orders.placed")
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        await sub.unsubscribe()
        await nc.drain()
        nc.close()


async def subscribe_orders_status_changed(callback) -> None:  # type: ignore[no-untyped-def]
    """Subscribe to mise.orders.status_changed and invoke callback for each message."""
    settings = get_settings()
    nc = await nats.connect(servers=[settings.nats_url])
    js = nc.jetstream()
    await _ensure_stream(nc)

    async def handler(msg):
        try:
            data = json.loads(msg.data.decode("utf-8"))
            await callback(data)
            await msg.ack()
        except Exception as e:
            logger.exception("Error handling mise.orders.status_changed: %s", e)
            await msg.nak()

    sub = await js.subscribe(
        "mise.orders.status_changed",
        cb=handler,
        durable="kitchen-order-status-consumer",
    )
    logger.debug("Subscribed to mise.orders.status_changed")
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        await sub.unsubscribe()
        await nc.drain()
        nc.close()
