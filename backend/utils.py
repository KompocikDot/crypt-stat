import os
from functools import lru_cache

from asyncpg import create_pool
from asyncpg.exceptions import InterfaceError
from exceptions import DbConnectionException, MissingDBUrlException


@lru_cache
async def get_db_pool():
    db_url = os.getenv("DB_URL")

    if not db_url:
        raise MissingDBUrlException
    try:
        return await create_pool(db_url)

    except InterfaceError:
        raise DbConnectionException
