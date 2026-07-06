import asyncio
import logging
from config import ensure_config
from telethon_client import UserClient
from storage import MemoryStore
from bot import HybridBot

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    cfg = ensure_config()

    # Start Telethon first (needs login)
    user_client = UserClient(cfg['api_id'], cfg['api_hash'], cfg['phone'])
    await user_client.start()
    owner_id = user_client.me.id
    logger.info(f"Telethon logged in as {user_client.me.first_name} ({owner_id})")

    store = MemoryStore()
    bot = HybridBot(cfg['bot_token'], user_client, store, owner_id)

    await bot.start()
    logger.info("Both Bot and User client are online. Press Ctrl+C to stop.")

    # Keep alive
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped by user")