import asyncio
import sys
import os
from contextlib import asynccontextmanager
from pyrogram import Client

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from database.db_commands import get_account_by_id
from database.models import get_db


@asynccontextmanager
async def get_temp_client(account_id: int):
    with get_db() as db:
        account = get_account_by_id(db, account_id)

    if not account:
        raise ValueError(f"Аккаунт с ID {account_id} не найден в базе данных.")

    client = Client(
        name=str(account.id),
        api_id=account.api_id,
        api_hash=account.api_hash,
        workdir="data/"
    )

    try:
        await client.start()
        yield client
    finally:
        if client.is_connected:
            await client.stop()