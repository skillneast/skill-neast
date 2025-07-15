import base64
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from urllib.parse import urlencode
from Script import script
from info import LOG_CHANNEL, LINK_URL, ADMIN
from plugins.database import checkdb, db, get_count


# ✅ Safe Encode Function
async def encode(string):
    string_bytes = string.encode("utf-8")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = base64_bytes.decode("utf-8").rstrip("=")
    return base64_string


# ✅ Final Decode Function with Padding Fix
async def decode(base64_string):
    base64_string = base64_string.strip().replace('\n', '').replace(' ', '')
    padding = 4 - len(base64_string) % 4
    if padding and padding != 4:
        base64_string += "=" * padding
    try:
        decoded_bytes = base64.urlsafe_b64decode(base64_string)
        return decoded_bytes.decode("utf-8")
    except Exception as e:
        print(f"[Decode Error] {e} -> {base64_string}")
        return None


# ✅ Start Command Handler
@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await checkdb.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        name = await client.ask(message.chat.id, "<b>Welcome to VJ Disk.\nSend Your Business Name:</b>")
        if not name.text:
            return await message.reply("❌ Invalid input. Use /start again.")
        await db.set_name(message.from_user.id, name=name.text)

        link = await client.ask(message.chat.id, "<b>Send your Telegram Channel link (https://t.me/...):</b>")
        if not link.text.startswith("http"):
            return await message.reply("❌ Invalid input. Use /start again.")
        await db.set_link(message.from_user.id, link=link.text)

        await checkdb.add_user(message.from_user.id, message.from_user.first_name)
        return await message.reply("✅ Account created! Now send me a file to get short link.")
    else:
        rm = InlineKeyboardMarkup([
            [InlineKeyboardButton("Update Channel", url="https://t.me/VJ_Disk")]
        ])
        await message.reply(
            script.START_TXT.format(message.from_user.mention),
            reply_markup=rm,
            parse_mode=enums.ParseMode.HTML
        )


# ✅ Handle Video/Document Upload
@Client.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
    file = getattr(message, message.media.value)
    fileid = file.file_id
    user_id = message.from_user.id

    log_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)

    params = {
        'u': user_id,
        'w': str(log_msg.id),
        's': str(0),
        't': str(0)
    }

    url1 = urlencode(params)
    link = await encode(url1)
    encoded_url = f"{LINK_URL}?Tech_VJ={link}"

    rm = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Open Link", url=encoded_url)]
    ])
    await message.reply_text(f"<code>{encoded_url}</code>", reply_markup=rm)


# ✅ Link decode and re-generate for new user
@Client.on_message(filters.private & filters.text & ~filters.command(["start"]))
async def link_start(client, message):
    if not message.text.startswith(LINK_URL):
        return

    link_part = message.text[len(LINK_URL + "?Tech_VJ="):].strip()
    original = await decode(link_part)
    if not original:
        return await message.reply("❌ Invalid or broken link.")

    try:
        u, user_id, w, s, t = original.split("=")
        user_id = user_id.replace("&w", "")
        w = w.replace("&s", "")
        s = s.replace("&t", "")
    except Exception:
        return await message.reply("❌ Link format error.")

    params = {
        'u': message.from_user.id,
        'w': str(w),
        's': str(s),
        't': str(t)
    }

    url1 = urlencode(params)
    link = await encode(url1)
    encoded_url = f"{LINK_URL}?Tech_VJ={link}"

    rm = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Open Link", url=encoded_url)]
    ])
    await message.reply_text(f"<code>{encoded_url}</code>", reply_markup=rm)


# ✅ Account Balance Show
@Client.on_message(filters.command("account") & filters.private)
async def show_account(client, message):
    link_clicks = get_count(message.from_user.id)
    if not link_clicks:
        link_clicks = 0
    balance = link_clicks / 1000.0
    balance = f"{balance:.2f}"
    text = f"<b>Your ID: <code>{message.from_user.id}</code>\nVideo Plays: {link_clicks}\nBalance: ${balance}</b>"
    await message.reply(text)
