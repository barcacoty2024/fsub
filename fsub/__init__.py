import os
import uvloop
import logging

from pyromod import Client
from pyrogram.types import BotCommand


logging.basicConfig(level=logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
LOGGER = logging.getLogger("fsub")

API_ID    = int(os.environ.get("API_ID", 2040))
API_HASH  = os.environ.get("API_HASH", "b18441a1ff607e10a989891a5462e627")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

DATABASE_NAME = BOT_TOKEN.split(":", 1)[0]
DATABASE_URL  = os.environ.get("DATABASE_URL")

CHANNEL_DB = int(os.environ.get("CHANNEL_DB"))

ADMINS = [int(i) for i in os.environ.get("ADMINS").split()]

FORCE_SUB_TOTAL = 1
FORCE_SUB_      = {}
while True:
    key   = f"FORCE_SUB_{FORCE_SUB_TOTAL}"
    value = os.environ.get(key)
    if value is None:
        break
    FORCE_SUB_[FORCE_SUB_TOTAL] = int(value)
    FORCE_SUB_TOTAL += 1

PROTECT_CONTENT = eval(os.environ.get("PROTECT_CONTENT", "True"))


class Bot(Client):
    def __init__(self):
        super().__init__(
            name      = "Bot",
            api_id    = API_ID, 
            api_hash  = API_HASH,
            bot_token = BOT_TOKEN,
            in_memory = True,
            plugins   = dict(root="fsub/plugins"))

    async def start(self):
        try:
            uvloop.install()
            await super().start()
            get_bot_profile = await self.get_me()
            self.bot_logger = LOGGER
            self.username   = get_bot_profile.username
            self.bot_logger.info(f"Memulai bot: @{self.username} (ID: {get_bot_profile.id})")
        except Exception as e:
            LOGGER.error(e)
            exit()
        
        try:
            self.bot_logger.info("Menyetel perintah bot...")
            await self.set_bot_commands([
                BotCommand("start", "Memulai bot"),
                BotCommand("batch", "[Khusus admin] Batch pesan"),
                BotCommand("broadcast", "[Khusus admin] Kirim pesan siaran"),
                BotCommand("restart", "[Khusus admin] Mulai ulang bot")])
            self.bot_logger.info("Perintah bot berhasil disetel.")
        except Exception as e:
            self.bot_logger.error(e)
            pass

        for key, chat_id in FORCE_SUB_.items():
            try:
                self.bot_logger.info("Memeriksa akses bot di FORCE_SUB...")
                get_chat    = await self.get_chat(chat_id)
                invite_link = get_chat.invite_link
                if not invite_link:
                    await self.export_chat_invite_link(chat_id)
                    invite_link = get_chat.invite_link
                setattr(self, f"FORCE_SUB_{key}", invite_link)
                self.bot_logger.info(f"FORCE_SUB_{key} terdeteksi: {get_chat.title} (ID: {get_chat.id})")
            except Exception as e:
                self.bot_logger.error(e)
                self.bot_logger.error(f"@{self.username} tidak memiliki akses mengundang pengguna dengan tautan di FORCE_SUB_{key}.")
                exit()

        try:
            self.bot_logger.info("Memeriksa akses bot di CHANNEL_DB...")
            hello_world = await self.send_message(CHANNEL_DB, "Hello World!") ; await hello_world.delete()
            get_chat    = await self.get_chat(CHANNEL_DB)
            self.bot_logger.info(f"CHANNEL_DB terdeteksi: {get_chat.title} (ID: {get_chat.id})")
        except Exception as e:
            self.bot_logger.error(e)
            self.bot_logger.error(f"@{self.username} tidak memiliki akses mengirim pesan di CHANNEL_DB.")
            exit()
        
        if os.path.exists('restart.txt'):
            with open('restart.txt', 'r') as f:
                chat_id    = int(f.readline().strip())
                message_id = int(f.readline().strip())
                await self.edit_message_text(chat_id, message_id, "Bot dimulai ulang.")
            
            os.remove('restart.txt')

        self.bot_logger.info("Bot berhasil diaktifkan!")
    
    async def stop(self, *args):
        await super().stop()
        self.bot_logger.warning("Bot telah berhenti!")
    
app = Bot()