import logging
from typing import Any

try:
    from motor.motor_asyncio import (
        AsyncIOMotorClient,
        AsyncIOMotorCollection,
        AsyncIOMotorDatabase,
    )
except ImportError:
    raise RuntimeError("Mongodb extra is not installed. Run `pip install snakestack[mongodb]`.")

from snakestack.config import settings


class DB:
    client: AsyncIOMotorClient[Any] | None = None

db = DB()

logger = logging.getLogger(__name__)


async def open_mongodb_connection() -> None:
    logger.debug("Connecting to mongodb...")
    if not settings.snakestack_mongodb_url.startswith("mongodb"):
        raise ValueError("Invalid MongoDB URL configured.")
    db.client = AsyncIOMotorClient(settings.snakestack_mongodb_url)
    logger.debug("Connecting to mongodb successful.")


async def close_mongodb_connection() -> None:
    logger.debug("Closing connection with mongodb...")
    if db.client:
        db.client.close()
    logger.debug("Connection with mongodb is closed.")


def get_collection(collection: str) -> AsyncIOMotorCollection[Any]:
    if not db.client:
        raise RuntimeError("Connection with mongodb is not starting.")
    return db.client[settings.snakestack_mongodb_dbname][collection]


def get_database() -> AsyncIOMotorDatabase[Any]:
    if not db.client:
        raise RuntimeError("Connection with mongodb is not starting.")
    return db.client[settings.snakestack_mongodb_dbname]
