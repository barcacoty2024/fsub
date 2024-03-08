import os
import uvloop
import logging

from pyromod import Client
from pyrogram.types import BotCommand


logging.basicConfig(
    format="[%(levelname)s] %(pathname)s:%(lineno)d -> %(message)s",
    level=logging.INFO)
LOGGER = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

DATABASE_NAME = BOT_TOKEN.split(":", 1)[0]
DATABASE_URL  = os.environ.get("DATABASE_URL")

CHANNEL_DB = int(os.environ.get("CHANNEL_DB"))

ADMINS = [int(i) for i in os.environ.get("ADMINS").split()]

FORCE_SUB_TOTAL = 1
FORCE_SUB_      = {}
while True:
    key = f"FORCE_SUB_{FORCE_SUB_TOTAL}"
    value = os.environ.get(key)
    if value is None:
        break
    FORCE_SUB_[FORCE_SUB_TOTAL] = int(value)
    FORCE_SUB_TOTAL += 1

PROTECT_CONTENT = eval(os.environ.get("PROTECT_CONTENT", "True"))


class Bot(Client):
    def __init__(self):
        super().__init__(
            "Bot", 2040, "b18441a1ff607e10a989891a5462e627",
            bot_token=BOT_TOKEN, in_memory=True, plugins=dict(root="fsub/plugins"))

    async def start(self):
        try:
            uvloop.install()
            await super().start()
            get_me = await self.get_me()
            self.username = get_me.username
            LOGGER.info(f"Memulai bot: @{self.username} (ID: {get_me.id})")
        except Exception as e:
            LOGGER.error(e)
            exit()
        
        try:
            LOGGER.info("Menyetel perintah bot...")
            await self.set_bot_commands([
                BotCommand("start", "Memulai bot"),
                BotCommand("batch", "[Khusus admin] Batch pesan"),
                BotCommand("broadcast", "[Khusus admin] Kirim pesan siaran"),
                BotCommand("restart", "[Khusus Admin] Mulai ulang bot")])
            LOGGER.info("Perintah bot berhasil disetel.")
        except Exception as e:
            LOGGER.error(e)
            pass

        for key, chat_id in FORCE_SUB_.items():
            try:
                LOGGER.info("Memeriksa akses bot di FORCE_SUB...")
                get_chat = await self.get_chat(chat_id)
                invite_link = get_chat.invite_link
                if not invite_link:
                    await self.export_chat_invite_link(chat_id)
                    invite_link = get_chat.invite_link
                setattr(self, f"FORCE_SUB_{key}", invite_link)
                LOGGER.info(f"FORCE_SUB_{key} terdeteksi: {get_chat.title} (ID: {get_chat.id})")
            except Exception as e:
                LOGGER.error(e)
                LOGGER.error(f"@{self.username} tidak memiliki akses mengundang pengguna dengan tautan di FORCE_SUB_{key}.")
                exit()

        try:
            LOGGER.info("Memeriksa akses bot di CHANNEL_DB...")
            hello = await self.send_message(CHANNEL_DB, "Hello World!") ; await hello.delete()
            LOGGER.info(f"CHANNEL_DB terdeteksi: {get_chat.title} (ID: {get_chat.id})")
        except Exception as e:
            LOGGER.error(e)
            LOGGER.error(f"@{self.username} tidak memiliki akses mengirim pesan di CHANNEL_DB.")
            exit()
        
        if os.path.exists('restart.txt'):
            with open('restart.txt', 'r') as f:
                chat_id = int(f.readline().strip())
                message_id = int(f.readline().strip())
                await self.edit_message_text(chat_id, message_id, "Bot dimulai ulang.")
            
            os.remove('restart.txt')

        LOGGER.info("Bot berhasil diaktifkan!")
    
    async def stop(self, *args):
        await super().stop()
        LOGGER.warning("Bot telah berhenti!")
    
app = Bot()