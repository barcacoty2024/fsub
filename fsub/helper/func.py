import re
import base64

from pyrogram.errors import FloodWait, UserNotParticipant

from fsub import ADMINS, FORCE_SUB_


def fsub_subscriber(filter, client, update):
    user_id = update.from_user.id
    if user_id in ADMINS:
        return True
    for key, chat_id in FORCE_SUB_.items():
        try: client.get_chat_member(chat_id, user_id)
        except UserNotParticipant: return False
    
    return True


def str_encoder(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string


def str_decoder(base64_string):
    base64_string = base64_string.strip("=")
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes) 
    string = string_bytes.decode("ascii")
    return string