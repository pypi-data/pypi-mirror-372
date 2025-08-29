import asyncio

from pyrogram import Client
from d4rk.Logs import setup_logger

logger = setup_logger(__name__)

async def delete(client: Client, chat_id: int, message_id: int,timeout: int=3):
    await asyncio.create_task(delete_message_worker(client,chat_id, message_id, timeout))

async def delete_message_worker(client,chat_id, message_id, timeout):
    await asyncio.sleep(timeout)
    try:
        await client.delete_messages(chat_id=chat_id, message_ids=message_id)
    except Exception as e:
        logger.error(f"Error deleting message {message_id}: {e}")