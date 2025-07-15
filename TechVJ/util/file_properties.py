from pyrogram import Client
from typing import Any, Optional
from pyrogram.types import Message
from pyrogram.file_id import FileId
from pyrogram.raw.types.messages import Messages
from TechVJ.server.exceptions import FIleNotFound


async def parse_file_id(message: "Message") -> Optional[FileId]:
    media = get_media_from_message(message)
    if media:
        return FileId.decode(media.file_id)

async def parse_file_unique_id(message: "Messages") -> Optional[str]:
    media = get_media_from_message(message)
    if media:
        return media.file_unique_id

async def get_file_ids(message):
    if message.empty:
        raise FIleNotFound
    media = get_media_from_message(message)
    file_unique_id = await parse_file_unique_id(message)
    file_id = await parse_file_id(message)
    setattr(file_id, "file_size", getattr(media, "file_size", 0))
    setattr(file_id, "mime_type", getattr(media, "mime_type", ""))
    # get_name function ab iska khayal rakhega
    setattr(file_id, "file_name", get_name(message))
    setattr(file_id, "unique_id", file_unique_id)
    return file_id

def get_media_from_message(message: "Message") -> Any:
    """
    FORWARDED FILES KO HANDLE KARNE KE LIYE UPDATED
    """
    # Agar message forward kiya gaya hai, to original message ko check karo
    msg_to_check = message.forward_from_message or message
    
    media_types = (
        "audio",
        "document",
        "photo",
        "sticker",
        "animation",
        "video",
        "voice",
        "video_note",
    )
    # Ab yeh sahi message (original ya naya) se media nikalega
    for attr in media_types:
        media = getattr(msg_to_check, attr, None)
        if media:
            return media

def get_hash(media_msg: Message) -> str:
    media = get_media_from_message(media_msg)
    return getattr(media, "file_unique_id", "")[:6]

def get_name(media_msg: Message) -> str:
    """
    MISSING FILE NAME KO HANDLE KARNE KE LIYE UPDATED
    """
    media = get_media_from_message(media_msg)
    if not media:
        return ""

    # Pehle file ka asli naam lene ki koshish karo
    file_name = getattr(media, 'file_name', None)
    if file_name:
        return file_name
    
    # Agar asli naam na mile, to unique id istemal karo
    return getattr(media, 'file_unique_id', "")

def get_media_file_size(m):
    media = get_media_from_message(m)
    return getattr(media, "file_size", 0)
