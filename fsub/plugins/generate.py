import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from pyromod.helpers import ikb

from fsub import ADMINS, CHANNEL_DB
from fsub.helper.func import str_encoder


@Client.on_message(
    filters.private & 
    filters.user(ADMINS) &
    ~filters.command(
        ["start", "batch", "broadcast", "restart"]))
async def generate_command(client, message):
    generate = await message.reply("...", quote=True)
    copied = await message.copy(chat_id=CHANNEL_DB, disable_notification=True)
    converted_id = copied.id * abs(CHANNEL_DB)
    string = f"get-{converted_id}"
    base64_string = str_encoder(string)
    
    link = f"t.me/{client.username}?start={base64_string}"
    share_button = ikb([
            [("Bagikan", f"t.me/share/url?url={link}", "url")]])
    return await generate.edit(link, reply_markup=share_button)