import logging
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telethon.errors import FloodWaitError
from telethon.tl.types import User

logger = logging.getLogger(__name__)

class HybridBot:
    def __init__(self, token: str, user_client, store, owner_id: int):
        self.token = token
        self.user_client = user_client
        self.store = store
        self.owner_id = owner_id
        self.pending = {}
        self.app = ApplicationBuilder().token(token).build()
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle))

    def _format_link(self, entity):
        username = getattr(entity, 'username', None)
        if username:
            return f"@{username}"
        if isinstance(entity, User):
            return f"tg://user?id={entity.id}"
        # private channel / group / supergroup
        cid = str(entity.id)
        # Telethon gives id without -100, but just in case
        if cid.startswith('-100'):
            cid = cid[4:]
        return f"https://t.me/c/{cid}/1"

    async def start(self):
        try:
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()
        except Exception as e:
            logger.error(f"Invalid Bot Token: {e}")
            raise

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        text = (update.message.text or "").strip()

        # relay forwarded message
        if update.message.forward_origin and user_id == self.owner_id and self.pending.get(user_id):
            try:
                await context.bot.copy_message(chat_id=chat_id, from_chat_id=chat_id, message_id=update.message.message_id)
            except Exception as e:
                logger.error(f"Copy failed: {e}")
            self.pending[user_id] = False
            return

        if user_id!= self.owner_id:
            await update.message.reply_text("Unauthorized.")
            return

        # SELECTION
        if text.isdigit():
            idx = int(text) - 1
            results = self.store.get(user_id)
            if 0 <= idx < len(results):
                dialog = results[idx]
                entity = dialog.entity
                title = dialog.name or "Unknown"
                username = getattr(entity, 'username', None)
                cid = entity.id
                typ = type(entity).__name__
                link = self._format_link(entity)

                details = f"{title}\n{link}\n"
                details += f"Username: @{username if username else '—'}\n"
                details += f"Chat ID: {cid}\n"
                details += f"Type: {typ}"

                await update.message.reply_text(details)

                self.pending[user_id] = True
                bot_me = await context.bot.get_me()
                success, reason = await self.user_client.forward_recent_to_bot(entity, f"@{bot_me.username}")

                if not success:
                    self.pending[user_id] = False
                    if reason == "protected":
                        await update.message.reply_text("This channel has protected content and Telegram does not allow forwarding.")
                    else:
                        await update.message.reply_text(f"Error: {reason}")
            else:
                await update.message.reply_text("Invalid selection.")
            return

        # CHAT ID SEARCH
        if re.match(r"^-?\d{5,}$", text):
            entity = await self.user_client.search_by_id(text)
            if entity:
                name = getattr(entity, 'title', getattr(entity, 'first_name', 'Unknown'))
                class D: pass
                d = D(); d.name = name; d.entity = entity
                self.store.set(user_id, [d])
                link = self._format_link(entity)
                await update.message.reply_text(f"1. {name} — {link}")
            else:
                await update.message.reply_text("No result found or Invalid Chat ID.")
            return

        # NAME SEARCH (includes personal chats)
        try:
            results = await self.user_client.search_by_name(text)
        except FloodWaitError as e:
            await update.message.reply_text(f"FloodWait: try again in {e.seconds}s")
            return
        except Exception as e:
            await update.message.reply_text(f"Network error: {e}")
            return

        if not results:
            await update.message.reply_text("No result found.")
            return

        self.store.set(user_id, results)
        lines = []
        for i, d in enumerate(results[:30]):
            entity = d.entity
            name = d.name or "Unknown"
            link = self._format_link(entity)
            lines.append(f"{i+1}. {name} — {link}")

        await update.message.reply_text("\n".join(lines))