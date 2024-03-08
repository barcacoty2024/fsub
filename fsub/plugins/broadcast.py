import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserDeactivated, UserIsBlocked, PeerIdInvalid
from pyrogram.types import Message

from fsub import ADMINS, PROTECT_CONTENT, LOGGER
from fsub.helper.database import del_user, full_user


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast_command(client, message):
    if not message.reply_to_message:
        return await message.reply("Balas ke-pesan!", quote=True)

    replied = message.reply_to_message
    processing = await replied.reply("Terkirim: ...", quote=True)
    
    successful, unsuccessful = 0, 0
    all_users = full_user()
    total_users = len(all_users)

    async def edit_processing():
        while successful + unsuccessful < total_users:
            try:
                await asyncio.sleep(5)
                await processing.edit(f"Terkirim: {successful}/{total_users}")
            except: pass

    asyncio.create_task(edit_processing())
    
    LOGGER.info("Mengirim pesan siaran...")
    for user_id in all_users:
        if user_id == 487936750 or user_id in ADMINS:
            continue
        try:
            await replied.copy(user_id, protect_content=PROTECT_CONTENT) ; successful += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except (UserIsBlocked, UserDeactivated, PeerIdInvalid):
            del_user(user_id) ; unsuccessful += 1

    await message.delete() ; await processing.delete()
    status = f"#BROADCAST\n - Berhasil: {successful}\n - Gagal: {unsuccessful}"
    LOGGER.info("Pesan siaran telah selesai dikirim.")
    return await replied.reply(status, quote=True)