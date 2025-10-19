# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import random
import requests
import humanize
import base64
import binascii  # Error handling ke liye import kiya gaya hai
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery
from info import LOG_CHANNEL, LINK_URL, ADMIN
from plugins.database import checkdb, db, get_count, get_withdraw, record_withdraw, record_visit
from urllib.parse import quote_plus, urlencode
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes

# Ek naya function jo direct stream URL banayega
async def get_stream_url(client, message_id):
    try:
        msg = await client.get_messages(LOG_CHANNEL, message_id)
        file_name = get_name(msg)
        file_hash = get_hash(msg)

        # Safety check for file_name
        if not file_name:
            return None
        
        return f"https://skill-neast.onrender.com/dl/{message_id}/{quote_plus(file_name)}?hash={file_hash}"
    except Exception as e:
        print(f"Error generating stream URL: {e}")
        return None

async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string

async def decode(base64_string):
    try:
        base64_string = base64_string.strip("=")
        base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
        string_bytes = base64.urlsafe_b64decode(base64_bytes)
        string = string_bytes.decode("ascii")
        return string
    except (binascii.Error, TypeError):
        return None

@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await checkdb.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        name = await client.ask(message.chat.id, "<b>Welcome To VJ Disk.\n\nIts Time To Create Account On VJ Disk\n\nNow Send Me Your Business Name Which Show On Website\nEx :- <code>Tech VJ</code></b>")
        if name.text:
            await db.set_name(message.from_user.id, name=name.text)
        else:
            return await message.reply("Wrong Input Start Your Process Again By Hitting /start")
        link = await client.ask(message.chat.id, "<b>Now Send Me Your Telegram Channel Link, Channel Link Will Show On Your Website.\n\nSend Like This <code>https://t.me/VJ_Bots</code> ✅\n\nDo not send like this @VJ_Bots ❌</b>")
        if link.text and link.text.startswith(('http://', 'https://')):
            await db.set_link(message.from_user.id, link=link.text)
        else:
            return await message.reply("Wrong Input Start Your Process Again By Hitting /start")
        await checkdb.add_user(message.from_user.id, message.from_user.first_name)
        return await message.reply("<b>Congratulations 🎉\n\nYour Account Created Successfully.\n\nFor Uploading File In Quality Option Use Command /quality\n\nMore Commands Are /account and /update and /withdraw\n\nFor Without Quality Option Direct Send File To Bot.</b>")
    else:
        rm = InlineKeyboardMarkup([[InlineKeyboardButton("✨ Update Channel", url="https://t.me/VJ_Disk")]])
        await client.send_message(
            chat_id=message.from_user.id,
            text=script.START_TXT.format(message.from_user.mention),
            reply_markup=rm,
            parse_mode=enums.ParseMode.HTML
        )
        return

@Client.on_message(filters.command("update") & filters.private)
async def update(client, message):
    vj = True
    if vj:
        name = await client.ask(message.chat.id, "<b>Now Send Me Your Business Name Which Show On Website\nEx :- <code>Tech VJ</code>\n\n/cancel - cancel the process</b>")
        if name.text == "/cancel":
            return await message.reply("Process Cancelled")
        if name.text:
            await db.set_name(message.from_user.id, name=name.text)
        else:
            return await message.reply("Wrong Input Start Your Process Again By Hitting /update")
        link = await client.ask(message.chat.id, "<b>Now Send Me Your Telegram Channel Link, Channel Link Will Show On Your Website.\n\nSend Like This <code>https://t.me/VJ_Bots</code> ✅\n\nDo not send like this @VJ_Bots ❌</b>")
        if link.text and link.text.startswith(('http://', 'https://')):
            await db.set_link(message.from_user.id, link=link.text)
        else:
            return await message.reply("Wrong Input Start Your Process Again By Hitting /update")
        return await message.reply("<b>Update Successfully.</b>")

@Client.on_message(filters.private & (filters.document | filters.video | filters.photo | filters.audio))
async def universal_handler(client, message):
    if not message.media:
        return await message.reply("Please send a file (video, document, audio, etc.).")

    file = getattr(message, message.media.value)
    file_type = message.media.value
    fileid = file.file_id

    log_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
    file_name = get_name(log_msg)

    # FIX: Yahan check kiya ja raha hai ki file_name None to nahi hai
    if not file_name:
        return await message.reply("Sorry, I couldn't get the name of this file. Please try sending it again or as a document.")

    is_video = file_type == 'video' or (file_type == 'document' and file.mime_type and file.mime_type.startswith('video/'))

    if is_video:
        # Ab ye line safe hai kyunki humne upar check kar liya hai
        is_ts_file = file_name.lower().endswith('.ts')
        
        if is_ts_file:
            direct_link = await get_stream_url(client, log_msg.id)
            if not direct_link:
                return await message.reply("Error generating stream link for this file.")
            
            response_message = (
                f"**🎥 Video:** `{file_name}`\n\n"
                f"**⬇️ Direct Download Link:**\n`{direct_link}`"
            )
            rm = InlineKeyboardMarkup([[InlineKeyboardButton("⬇️ Download Now", url=direct_link)]])
            await message.reply_text(text=response_message, reply_markup=rm, parse_mode=enums.ParseMode.MARKDOWN)
            
        else:
            params = {'u': message.from_user.id, 'w': str(log_msg.id), 's': str(0), 't': str(0)}
            url1 = f"{urlencode(params)}"
            link = await encode(url1)
            encoded_url = f"{LINK_URL}?Tech_VJ={link}"
            
            direct_stream_url = await get_stream_url(client, log_msg.id)
            if not direct_stream_url:
                direct_stream_url = "Could not generate direct stream URL."
            
            response_message = (
                f"**🎥 Video:** `{file_name}`\n\n"
                f"**🌐 Website Player URL:**\n`{encoded_url}`\n\n"
                f"**🔗 Direct Stream URL:**\n`{direct_stream_url}`"
            )
            rm = InlineKeyboardMarkup([[InlineKeyboardButton("🌐 Open Link", url=encoded_url)]])
            await message.reply_text(text=response_message, reply_markup=rm, parse_mode=enums.ParseMode.MARKDOWN)

    else:
        direct_link = await get_stream_url(client, log_msg.id)
        if not direct_link:
            return await message.reply("Error generating direct download link for this file.")
            
        response_message = (
            f"**📄 File:** `{file_name}`\n\n"
            f"**⬇️ Direct Download Link:**\n`{direct_link}`"
        )
        rm = InlineKeyboardMarkup([[InlineKeyboardButton("⬇️ Download Now", url=direct_link)]])
        await message.reply_text(text=response_message, reply_markup=rm, parse_mode=enums.ParseMode.MARKDOWN)

@Client.on_message(filters.private & filters.command("quality"))
async def quality_link(client, message):
    first_id = str(0)
    second_id = str(0)
    third_id = str(0)
    
    # Store quality chosen by user to prevent duplicates
    chosen_qualities = []

    first_q_msg = await client.ask(message.from_user.id, "<b>Now Send Me Your Quality In Which You Upload File. Only Below These Qualities Are Available Only.\n\n1. If your file quality is less than or equal to 480p then send <code>480</code>\n2. If your file quality is greater than 480p and less than or equal to 720p then send <code>720</code>\n3. If your file quality is greater than 720p then send <code>1080</code></b>")
    
    if first_q_msg.text == "480":
        f_id = await client.ask(message.from_user.id, "Now Send Me Your 480p Quality File.")
        if f_id.video or f_id.document:
            file = getattr(f_id, f_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            first_id = str(first_msg.id)
            chosen_qualities.append("480")
        else:
            return await message.reply("Wrong Input, Start Process Again By /quality")
    elif first_q_msg.text == "720":
        s_id = await client.ask(message.from_user.id, "Now Send Me Your 720p Quality File.")
        if s_id.video or s_id.document:
            file = getattr(s_id, s_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            second_id = str(first_msg.id)
            chosen_qualities.append("720")
        else:
            return await message.reply("Wrong Input, Start Process Again By /quality")
    elif first_q_msg.text == "1080":
        t_id = await client.ask(message.from_user.id, "Now Send Me Your 1080p Quality File.")
        if t_id.video or t_id.document:
            file = getattr(t_id, t_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            third_id = str(first_msg.id)
            chosen_qualities.append("1080")
        else:
            return await message.reply("Wrong Input, Start Process Again By /quality")
    else:
        return await message.reply("Choose Quality From Above Three Quality Only. Send /quality command again to start creating link.")

    second_q_msg = await client.ask(message.from_user.id, "<b>Now Send Me Your **Another** Quality In Which You Upload File. Only Below These Qualities Are Available Only.\n\n1. If your file quality is less than or equal to 480p then send <code>480</code>\n2. If your file quality is greater than 480p and less than or equal to 720p then send <code>720</code>\n3. If your file quality is greater than 720p then send <code>1080</code>\n\nNote: Do not use one quality 2 or more time.</b>")
    
    if second_q_msg.text == "/getlink":
        # Handle case where user wants only 1 quality
        pass # Will be handled by the final link generation
    elif second_q_msg.text not in chosen_qualities:
        if second_q_msg.text == "480":
            f_id = await client.ask(message.from_user.id, "Now Send Me Your 480p Quality File.")
            if f_id.video or f_id.document:
                file = getattr(f_id, f_id.media.value)
                fileid = file.file_id
                first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
                first_id = str(first_msg.id) if first_id == "0" else first_id # Update only if not set
                chosen_qualities.append("480")
            else:
                return await message.reply("Wrong Input, Start Process Again By /quality")
        elif second_q_msg.text == "720":
            s_id = await client.ask(message.from_user.id, "Now Send Me Your 720p Quality File.")
            if s_id.video or s_id.document:
                file = getattr(s_id, s_id.media.value)
                fileid = file.file_id
                first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
                second_id = str(first_msg.id) if second_id == "0" else second_id # Update only if not set
                chosen_qualities.append("720")
            else:
                return await message.reply("Wrong Input, Start Process Again By /quality")
        elif second_q_msg.text == "1080":
            t_id = await client.ask(message.from_user.id, "Now Send Me Your 1080p Quality File.")
            if t_id.video or t_id.document:
                file = getattr(t_id, t_id.media.value)
                fileid = file.file_id
                first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
                third_id = str(first_msg.id) if third_id == "0" else third_id # Update only if not set
                chosen_qualities.append("1080")
            else:
                return await message.reply("Wrong Input, Start Process Again By /quality")
        else:
            return await message.reply("Choose Quality From Above Three Quality Only and do not repeat. Send /quality command again to start creating link.")
    else:
        return await message.reply("You have already selected this quality. Please choose a different one or use /getlink to finish. Send /quality command again to start creating link.")
        
    if second_q_msg.text != "/getlink":
        third_q_msg = await client.ask(message.from_user.id, "<b>Now Send Me Your **Another** Quality In Which You Upload File. Only Below These Qualities Are Available Only.\n\n1. If your file quality is less than or equal to 480p then send <code>480</code>\n2. If your file quality is greater than 480p and less than or equal to 720p then send <code>720</code>\n3. If your file quality is greater than 720p then send <code>1080</code>\n\nNote: Do not use one quality 2 or more time.\n\nIf you want only 2 quality option then use <code>/getlink</code> command for stream link.</b>")
        
        if third_q_msg.text == "/getlink":
            # User wants to finish with 2 qualities
            pass
        elif third_q_msg.text not in chosen_qualities:
            if third_q_msg.text == "480":
                f_id = await client.ask(message.from_user.id, "Now Send Me Your 480p Quality File.")
                if f_id.video or f_id.document:
                    file = getattr(f_id, f_id.media.value)
                    fileid = file.file_id
                    first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
                    first_id = str(first_msg.id) if first_id == "0" else first_id
                    chosen_qualities.append("480")
                else:
                    return await message.reply("Wrong Input, Start Process Again By /quality")
            elif third_q_msg.text == "720":
                s_id = await client.ask(message.from_user.id, "Now Send Me Your 720p Quality File.")
                if s_id.video or s_id.document:
                    file = getattr(s_id, s_id.media.value)
                    fileid = file.file_id
                    first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
                    second_id = str(first_msg.id) if second_id == "0" else second_id
                    chosen_qualities.append("720")
                else:
                    return await message.reply("Wrong Input, Start Process Again By /quality")
            elif third_q_msg.text == "1080":
                t_id = await client.ask(message.from_user.id, "Now Send Me Your 1080p Quality File.")
                if t_id.video or t_id.document:
                    file = getattr(t_id, t_id.media.value)
                    fileid = file.file_id
                    first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
                    third_id = str(first_msg.id) if third_id == "0" else third_id
                    chosen_qualities.append("1080")
                else:
                    return await message.reply("Wrong Input, Start Process Again By /quality")
            else:
                return await message.reply("Choose Quality From Above Three Quality Only and do not repeat. Send /quality command again to start creating link.")
        else:
            return await message.reply("You have already selected this quality. Please choose a different one or use /getlink to finish. Send /quality command again to start creating link.")

    params = {'u': message.from_user.id, 'w': first_id, 's': second_id, 't': third_id}
    url1 = f"{urlencode(params)}"
    link = await encode(url1)

    encoded_url = f"{LINK_URL}?Tech_VJ={link}"

    video_title = "Multi-Quality Video" # Default title
    if first_id != "0":
        try:
            msg_480 = await client.get_messages(LOG_CHANNEL, int(first_id))
            video_title = get_name(msg_480)
        except Exception as e:
            print(f"Error getting title for 480p: {e}")
            video_title = "Video"
    elif second_id != "0":
        try:
            msg_720 = await client.get_messages(LOG_CHANNEL, int(second_id))
            video_title = get_name(msg_720)
        except Exception as e:
            print(f"Error getting title for 720p: {e}")
            video_title = "Video"
    elif third_id != "0":
        try:
            msg_1080 = await client.get_messages(LOG_CHANNEL, int(third_id))
            video_title = get_name(msg_1080)
        except Exception as e:
            print(f"Error getting title for 1080p: {e}")
            video_title = "Video"
            
    response_message = f"**🎥 Video:** `{video_title}`\n\n"
    response_message += f"**🌐 Website Player URL:**\n`{encoded_url}`\n\n"
    
    if first_id != "0":
        first_stream_url = await get_stream_url(client, int(first_id))
        if first_stream_url:
            response_message += f"**🔗 480p Direct URL:**\n`{first_stream_url}`\n\n"
    if second_id != "0":
        second_stream_url = await get_stream_url(client, int(second_id))
        if second_stream_url:
            response_message += f"**🔗 720p Direct URL:**\n`{second_stream_url}`\n\n"
    if third_id != "0":
        third_stream_url = await get_stream_url(client, int(third_id))
        if third_stream_url:
            response_message += f"**🔗 1080p Direct URL:**\n`{third_stream_url}`\n\n"

    rm=InlineKeyboardMarkup([[InlineKeyboardButton("🌐 Open Link", url=encoded_url)]])
    await message.reply_text(text=response_message, reply_markup=rm, parse_mode=enums.ParseMode.MARKDOWN)

@Client.on_message(filters.private & filters.text & ~filters.command(["account", "withdraw", "notify", "quality", "start", "update"]))
async def link_start(client, message):
    if not message.text.startswith(LINK_URL):
        return
    link_part = message.text[len(LINK_URL + "?Tech_VJ="):].strip()

    original = await decode(link_part)

    if original is None:
        return await message.reply("Link Invalid or Corrupted")

    try:
        # Assuming original is like 'u=USER_ID&w=ID&s=SEC&t=TH'
        params_dict = dict(param.split('=') for param in original.split('&'))
        user_id_from_link = params_dict.get('u')
        id_val = params_dict.get('w')
        sec_val = params_dict.get('s')
        th_val = params_dict.get('t')

    except ValueError:
        return await message.reply("Link Invalid")
        
    if user_id_from_link == str(message.from_user.id):
        rm=InlineKeyboardMarkup([[InlineKeyboardButton("🌐 Open Link", url=message.text)]])
        return await message.reply_text(text=f"<code>{message.text}</code>", reply_markup=rm)

    params = {'u': message.from_user.id, 'w': str(id_val), 's': str(sec_val), 't': str(th_val)}
    url1 = f"{urlencode(params)}"
    link = await encode(url1)
    encoded_url = f"{LINK_URL}?Tech_VJ={link}"
    rm=InlineKeyboardMarkup([[InlineKeyboardButton("🌐 Open Link", url=encoded_url)]])
    await message.reply_text(text=f"<code>{encoded_url}</code>", reply_markup=rm)

@Client.on_message(filters.private & filters.command("account"))
async def show_account(client, message):
    link_clicks = get_count(message.from_user.id)
    if link_clicks:
        balance = link_clicks / 1000.0
        formatted_balance = f"{balance:.2f}"
        response = f"<b>Your Api Key :- <code>{message.from_user.id}</code>\n\nVideo Plays :- {link_clicks} ( Delay To Show Data )\n\nBalance :- ${formatted_balance}</b>"
    else:
        response = f"<b>Your Api Key :- <code>{message.from_user.id}</code>\nVideo Plays :- 0 ( Delay To Show Data )\nBalance :- $0</b>"
    await message.reply(response)

@Client.on_message(filters.private & filters.command("withdraw"))
async def show_withdraw(client, message):
    w = get_withdraw(message.from_user.id)
    if w == True:
        return await message.reply("One Withdrawal Is In Process Wait For Complete It")
    link_clicks = get_count(message.from_user.id)
    if not link_clicks:
        return await message.reply("You Are Not Eligible For Withdrawal.\nMinimum Withraw Is 1000 Link Clicks or Video Plays.")
    if link_clicks >= 1000:
        confirm = await client.ask(message.from_user.id, "You Are Going To Withdraw All Your Link Clicks. Are You Sure You Want to Withdraw ?\nSend /yes or /no")
        if confirm.text.lower() == "/yes":
            record_withdraw(message.from_user.id, True)
            await message.reply("Your withdrawal request has been submitted. It will be processed shortly.")
        else:
            await message.reply("Withdrawal cancelled.")
    else:
        await message.reply(f"You need at least 1000 link clicks for withdrawal. You currently have {link_clicks}.")
