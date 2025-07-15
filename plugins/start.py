import random
import requests
import humanize
import base64
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import LOG_CHANNEL, LINK_URL, ADMIN
from plugins.database import checkdb, db, get_count, get_withdraw, record_withdraw, record_visit
from urllib.parse import quote_plus, urlencode


# ✅ Fixed and safe base64 encode
async def encode(string):
    string_bytes = string.encode("utf-8")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = base64_bytes.decode("utf-8").rstrip("=")
    return base64_string

# ✅ Final and safe base64 decode with correct padding handling
async def decode(base64_string):
    base64_string = base64_string.strip().replace('\n', '').replace(' ', '')
    padding = 4 - len(base64_string) % 4
    if padding and padding != 4:
        base64_string += "=" * padding
    try:
        decoded_bytes = base64.urlsafe_b64decode(base64_string)
        return decoded_bytes.decode("utf-8")
    except Exception as e:
        print(f"[DECODE ERROR] {e} -> INPUT: {base64_string}")
        return None


@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await checkdb.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        name = await client.ask(message.chat.id, "<b>Welcome To VJ Disk.\n\nIts Time To Create Account On VJ Disk\n\nNow Send Me Your Business Name Which Show On Website\nEx :- <code>Tech VJ</code></b>")
        if name.text:
            await db.set_name(message.from_user.id, name=name.text)
        else:
            return await message.reply("**Wrong Input Start Your Process Again By Hitting /start**")
        link = await client.ask(message.chat.id, "<b>Now Send Me Your Telegram Channel Link, Channel Link Will Show On Your Website.\n\nSend Like This <code>https://t.me/VJ_Bots</code> ✅\n\nDo not send like this @VJ_Bots ❌</b>")
        if link.text and link.text.startswith(('http://', 'https://')):
            await db.set_link(message.from_user.id, link=link.text)
        else:
            return await message.reply("**Wrong Input Start Your Process Again By Hitting /start**")
        await checkdb.add_user(message.from_user.id, message.from_user.first_name)
        return await message.reply("<b>🎉 Congratulations\n\nYour Account Created Successfully.\n\nUse /quality to upload file with quality\nOther Commands: /account /update /withdraw\n\nOr just send file directly to bot.</b>")
    else:
        rm = InlineKeyboardMarkup([[InlineKeyboardButton("✨ Update Channel", url="https://t.me/VJ_Disk")]])
        await client.send_message(
            chat_id=message.from_user.id,
            text=script.START_TXT.format(message.from_user.mention),
            reply_markup=rm,
            parse_mode=enums.ParseMode.HTML
        )


@Client.on_message(filters.private & filters.text & ~filters.command(["account", "withdraw", "notify", "quality", "start", "update"]))
async def link_start(client, message):
    if not message.text.startswith(LINK_URL):
        return
    link_part = message.text[len(LINK_URL + "?Tech_VJ="):].strip()
    original = await decode(link_part)
    if not original:
        return await message.reply("❌ Invalid or broken link")
    try:
        u, user_id, id, sec, th = original.split("=")
        user_id = user_id.replace("&w", "")
        id = id.replace("&s", "")
        sec = sec.replace("&t", "")
    except Exception as e:
        print(f"[SPLIT ERROR] {e}")
        return await message.reply("❌ Invalid format in link")
    
    if user_id == str(message.from_user.id):
        rm = InlineKeyboardMarkup([[InlineKeyboardButton("🖇️ Open Link", url=message.text)]])
        return await message.reply_text(text=f"<code>{message.text}</code>", reply_markup=rm)

    # generate new link for this user
    params = {'u': message.from_user.id, 'w': str(id), 's': str(sec), 't': str(th)}
    url1 = f"{urlencode(params)}"
    link = await encode(url1)
    encoded_url = f"{LINK_URL}?Tech_VJ={link}"
    rm = InlineKeyboardMarkup([[InlineKeyboardButton("🖇️ Open Link", url=encoded_url)]])
    await message.reply_text(text=f"<code>{encoded_url}</code>", reply_markup=rm)
