import logging
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError, RPCError
from search import search_dialogs_by_name, get_entity_by_id, get_recent_forwardable

logger = logging.getLogger(__name__)

class UserClient:
    def __init__(self, api_id: int, api_hash: str, phone: str, session: str = "user_session"):
        self.client = TelegramClient(session, api_id, api_hash)
        self.phone = phone
        self.me = None

    async def start(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            try:
                await self.client.send_code_request(self.phone)
                code = input("Enter Telegram login code: ").strip()
                await self.client.sign_in(self.phone, code)
            except SessionPasswordNeededError:
                pwd = input("2-Step Verification Password: ").strip()
                await self.client.sign_in(password=pwd)
            except FloodWaitError as e:
                logger.error(f"FloodWait: wait {e.seconds}s")
                raise
        self.me = await self.client.get_me()

    async def search_by_name(self, query: str):
        try:
            return await search_dialogs_by_name(self.client, query)
        except RPCError as e:
            logger.error(f"Search error: {e}")
            return []

    async def search_by_id(self, chat_id: str):
        return await get_entity_by_id(self.client, chat_id)

    async def forward_recent_to_bot(self, entity, bot_username: str):
        try:
            msg = await get_recent_forwardable(self.client, entity)
            if not msg:
                return False, "protected"
            await self.client.forward_messages(bot_username, msg)
            return True, None
        except FloodWaitError as e:
            return False, f"FloodWait {e.seconds}s"
        except Exception as e:
            logger.error(f"Forward failed: {e}")
            return False, str(e)