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
        link = await client.ask(message.chat.id, "<b>Now Send Me Your Telegram Channel Link, Channel Link Will Show On Your Website.\n\nSend Like This <code>https://t.me/VJ_Bots</code> âœ…\n\nDo not send like this @VJ_Bots âŒ</b>")
        if link.text and link.text.startswith(('http://', 'https://')):
            await db.set_link(message.from_user.id, link=link.text)
        else:
            return await message.reply("Wrong Input Start Your Process Again By Hitting /start")
        await checkdb.add_user(message.from_user.id, message.from_user.first_name)
        return await message.reply("<b>Congratulations ðŸŽ‰\n\nYour Account Created Successfully.\n\nFor Uploading File In Quality Option Use Command /quality\n\nMore Commands Are /account and /update and /withdraw\n\nFor Without Quality Option Direct Send File To Bot.</b>")
    else:
        rm = InlineKeyboardMarkup([[InlineKeyboardButton("âœ¨ Update Channel", url="https://t.me/VJ_Disk")]])
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
        link = await client.ask(message.chat.id, "<b>Now Send Me Your Telegram Channel Link, Channel Link Will Show On Your Website.\n\nSend Like This <code>https://t.me/VJ_Bots</code> âœ…\n\nDo not send like this @VJ_Bots âŒ</b>")
        if link.text and link.text.startswith(('http://', 'https://')):
            await db.set_link(message.from_user.id, link=link.text)
        else:
            return await message.reply("Wrong Input Start Your Process Again By Hitting /update")
        return await message.reply("<b>Update Successfully.</b>")

# ----------------- FIX YAHAN KIYA GAYA HAI -----------------
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
                f"**ðŸŽ¥ Video:** `{file_name}`\n\n"
                f"**â¬‡ï¸ Direct Download Link:**\n`{direct_link}`"
            )
            rm = InlineKeyboardMarkup([[InlineKeyboardButton("â¬‡ï¸ Download Now", url=direct_link)]])
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
                f"**ðŸŽ¥ Video:** `{file_name}`\n\n"
                f"**ðŸŒ Website Player URL:**\n`{encoded_url}`\n\n"
                f"**ðŸ”— Direct Stream URL:**\n`{direct_stream_url}`"
            )
            rm = InlineKeyboardMarkup([[InlineKeyboardButton("ðŸ–‡ï¸ Open Link", url=encoded_url)]])
            await message.reply_text(text=response_message, reply_markup=rm, parse_mode=enums.ParseMode.MARKDOWN)

    else:
        direct_link = await get_stream_url(client, log_msg.id)
        if not direct_link:
            return await message.reply("Error generating direct download link for this file.")
            
        response_message = (
            f"**ðŸ“„ File:** `{file_name}`\n\n"
            f"**â¬‡ï¸ Direct Download Link:**\n`{direct_link}`"
        )
        rm = InlineKeyboardMarkup([[InlineKeyboardButton("â¬‡ï¸ Download Now", url=direct_link)]])
        await message.reply_text(text=response_message, reply_markup=rm, parse_mode=enums.ParseMode.MARKDOWN)
# ----------------- FIX END -----------------


@Client.on_message(filters.private & filters.command("quality"))
async def quality_link(client, message):
    first_id = str(0)
    second_id = str(0)
    third_id = str(0)
    first = await client.ask(message.from_user.id, "<b>Now Send Me Your Quality In Which You Upload File. Only Below These Qualities Are Available Only.\n\n1. If your file quality is less than or equal to 480p then send <code>480</code>\n2. If your file quality is greater than 480p and less than or equal to 720p then send <code>720</code>\n3. If your file quality is greater than 720p then send <code>1080</code></b>")
    if first.text == "480":
        f_id = await client.ask(message.from_user.id, "Now Send Me Your 480p Quality File.")
        if f_id.video or f_id.document:
            file = getattr(f_id, f_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            first_id = str(first_msg.id)
        else:
            return await message.reply("Wrong Input, Start Process Again By /quality")
    elif first.text == "720":
        s_id = await client.ask(message.from_user.id, "Now Send Me Your 720p Quality File.")
        if s_id.video or s_id.document:
            file = getattr(s_id, s_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            second_id = str(first_msg.id)
        else:
            return await message.reply("Wrong Input, Start Process Again By /quality")
    elif first.text == "1080":
        t_id = await client.ask(message.from_user.id, "Now Send Me Your 1080p Quality File.")
        if t_id.video or t_id.document:
            file = getattr(t_id, t_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            third_id = str(first_msg.id)
        else:
            return await message.reply("Wrong Input, Start Process Again By /quality")
    else:
        return await message.reply("Choose Quality From Above Three Quality Only. Send /quality commamd again to start creating link.")

    second = await client.ask(message.from_user.id, "<b>Now Send Me Your **Another** Quality In Which You Upload File. Only Below These Qualities Are Available Only.\n\n1. If your file quality is less than or equal to 480p then send <code>480</code>\n2. If your file quality is greater than 480p and less than or equal to 720p then send <code>720</code>\n3. If your file quality is greater than 720p then send <code>1080</code>\n\nNote Don not use one quality 2 or more time.</b>")
    if second.text != first.text and second.text == "480":
        f_id = await client.ask(message.from_user.id, "Now Send Me Your 480p Quality File.")
        if f_id.video or f_id.document:
            file = getattr(f_id, f_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            first_id = str(first_msg.id)
        else:
            return await message.reply("Wrong Input, Start Process Again By /quality")
    elif second.text != first.text and second.text == "720":
        s_id = await client.ask(message.from_user.id, "Now Send Me Your 720p Quality File.")
        if s_id.video or s_id.document:
            file = getattr(s_id, s_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            second_id = str(first_msg.id)
        else:
            return await message.reply("Wrong Input, Start Process Again By /quality")
    elif second.text != first.text and second.text == "1080":
        t_id = await client.ask(message.from_user.id, "Now Send Me Your 1080p Quality File.")
        if t_id.video or t_id.document:
            file = getattr(t_id, t_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            third_id = str(first_msg.id)
        else:
            return await message.reply("Wrong Input, Start Process Again By /quality")
    else:
        return await message.reply("Choose Quality From Above Three Quality Only. Send /quality commamd again to start creating link.")
        
    third = await client.ask(message.from_user.id, "<b>Now Send Me Your **Another** Quality In Which You Upload File. Only Below These Qualities Are Available Only.\n\n1. If your file quality is less than or equal to 480p then send <code>480</code>\n2. If your file quality is greater than 480p and less than or equal to 720p then send <code>720</code>\n3. If your file quality is greater than 720p then send <code>1080</code>\n\nNote Don not use one quality 2 or more time.\n\nIf you want only 2 quality option then use <code>/getlink</code> command for stream link.</b>")
    if third.text != second.text and third.text != first.text and third.text == "480":
        f_id = await client.ask(message.from_user.id, "Now Send Me Your 480p Quality File.")
        if f_id.video or f_id.document:
            file = getattr(f_id, f_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            first_id = str(first_msg.id)
        else:
            return await message.reply("Wrong Input, Start Process Again By /quality")
    elif third.text != second.text and third.text != first.text and third.text == "720":
        s_id = await client.ask(message.from_user.id, "Now Send Me Your 720p Quality File.")
        if s_id.video or s_id.document:
            file = getattr(s_id, s_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            second_id = str(first_msg.id)
        else:
            return await message.reply("Wrong Input, Start Process Again By /quality")
    elif third.text != second.text and third.text != first.text and third.text == "1080":
        t_id = await client.ask(message.from_user.id, "Now Send Me Your 1080p Quality File.")
        if t_id.video or t_id.document:
            file = getattr(t_id, t_id.media.value)
            fileid = file.file_id
            first_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
            third_id = str(first_msg.id)
        else:
            return await message.reply("Wrong Input, Start Process Again By /quality")
    elif third.text == "/getlink":
        params = {'u': message.from_user.id, 'w': first_id, 's': second_id, 't': third_id}
        url1 = f"{urlencode(params)}"
        link = await encode(url1)
        
        encoded_url = f"{LINK_URL}?Tech_VJ={link}"
        
        first_stream_url = await get_stream_url(client, int(first_id)) if first_id != "0" else ""
        second_stream_url = await get_stream_url(client, int(second_id)) if second_id != "0" else ""
        third_stream_url = await get_stream_url(client, int(third_id)) if third_id != "0" else ""
        
        video_title = get_name(await client.get_messages(LOG_CHANNEL, int(first_id)))
        
        response_message = f"**ðŸŽ¥ Video:** `{video_title}`\n\n"
        response_message += f"**ðŸŒ Website Player URL:**\n`{encoded_url}`\n\n"
        if first_stream_url:
            response_message += f"**ðŸ”— 480p Direct URL:**\n`{first_stream_url}`\n\n"
        if second_stream_url:
            response_message += f"**ðŸ”— 720p Direct URL:**\n`{second_stream_url}`\n\n"
        if third_stream_url:
            response_message += f"**ðŸ”— 1080p Direct URL:**\n`{third_stream_url}`\n\n"
        
        rm=InlineKeyboardMarkup([[InlineKeyboardButton("ðŸ–‡ï¸ Open Link", url=encoded_url)]])
        return await message.reply_text(text=response_message, reply_markup=rm, parse_mode=enums.ParseMode.MARKDOWN)
    else:
        return await message.reply("Choose Quality From Above Three Quality Only. Send /quality commamd again to start creating link.")

    params = {'u': message.from_user.id, 'w': first_id, 's': second_id, 't': third_id}
    url1 = f"{urlencode(params)}"
    link = await encode(url1)
    
    encoded_url = f"{LINK_URL}?Tech_VJ={link}"
    
    first_stream_url = await get_stream_url(client, int(first_id)) if first_id != "0" else ""
    second_stream_url = await get_stream_url(client, int(second_id)) if second_id != "0" else ""
    third_stream_url = await get_stream_url(client, int(third_id)) if third_id != "0" else ""
    
    video_title = get_name(await client.get_messages(LOG_CHANNEL, int(first_id)))
        
    response_message = f"**ðŸŽ¥ Video:** `{video_title}`\n\n"
    response_message += f"**ðŸŒ Website Player URL:**\n`{encoded_url}`\n\n"
    if first_stream_url:
        response_message += f"**ðŸ”— 480p Direct URL:**\n`{first_stream_url}`\n\n"
    if second_stream_url:
        response_message += f"**ðŸ”— 720p Direct URL:**\n`{second_stream_url}`\n\n"
    if third_stream_url:
        response_message += f"**ðŸ”— 1080p Direct URL:**\n`{third_stream_url}`\n\n"
    
    rm=InlineKeyboardMarkup([[InlineKeyboardButton("ðŸ–‡ï¸ Open Link", url=encoded_url)]])
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
        u, user_id, id, sec, th = original.split("=")
    except ValueError:
        return await message.reply("Link Invalid")
        
    user_id = user_id.replace("&w", "")
    if user_id == str(message.from_user.id):
        rm=InlineKeyboardMarkup([[InlineKeyboardButton("ðŸ–‡ï¸ Open Link", url=message.text)]])
        return await message.reply_text(text=f"<code>{message.text}</code>", reply_markup=rm)
    
    id = id.replace("&s", "")
    sec = sec.replace("&t", "")
    params = {'u': message.from_user.id, 'w': str(id), 's': str(sec), 't': str(th)}
    url1 = f"{urlencode(params)}"
    link = await encode(url1)
    encoded_url = f"{LINK_URL}?Tech_VJ={link}"
    rm=InlineKeyboardMarkup([[InlineKeyboardButton("ðŸ–‡ï¸ Open Link", url=encoded_url)]])
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
        confirm = await client.ask(message.from_user.id, "You Are Going To Withdraw All Your Link Clicks. Are You Sure You Want To Withdraw ?\nSend /yes or /no")
        if confirm.text == "/no":
            return await message.reply("Withdraw Cancelled By You âŒ")
        else:
            pay = await client.ask(message.from_user.id, "Now Choose Your Payment Method, Click On In Which You Want Your Withdrawal.\n\n/upi - for upi, webmoney, airtm, capitalist\n\n/bank - for bank only")
            if pay.text == "/upi":
                upi_details = await client.ask(message.from_user.id, "Now Send Me Your Upi Or Upi Number With Your Name, Make Sure Name Matches With Your Upi Account")
                if not upi_details.text:
                    return await message.reply("Wrong Input âŒ")
                upi = f"Upi - {upi_details.text}"
                try:
                    await upi_details.delete()
                except:
                    pass
            elif pay.text == "/bank":
                name = await client.ask(message.from_user.id, "Now Send Me Your Account Holder Full Name")
                if not name.text:
                    return await message.reply("Wrong Input âŒ")
                number = await client.ask(message.from_user.id, "Now Send Me Your Account Number")
                if not number.text.isdigit():
                    return await message.reply("Wrong Input âŒ")
                ifsc = await client.ask(message.from_user.id, "Now Send Me Your IFSC Code.")
                if not ifsc.text:
                    return await message.reply("Wrong Input âŒ")
                bank_name = await client.ask(message.from_user.id, "Now You Can Send Necessary Thing In One Message, Like Send Bank Name, Or Contact Details.")
                if not bank_name.text:
                    return await message.reply("Wrong Input âŒ")
                upi = f"Account Holder Name - {name.text}\n\nAccount Number - {number.text}\n\nIFSC Code - {ifsc.text}\n\nBank Name - {bank_name.text}\n\n"
                try:
                    await name.delete()
                    await number.delete()
                    await ifsc.delete()
                    await bank_name.delete()
                except:
                    pass
            else:
                return await message.reply("Wrong payment method selected.")

            traffic = await client.ask(message.from_user.id, "Now Send Me Your Traffic Source Link, If Your Link Click Are Fake Then You Will Not Receive Payment And Withdrawal Get Cancelled")
            if not traffic.text:
                return await message.reply("Wrong Traffic Source âŒ")
            
            balance = link_clicks / 1000.0
            formatted_balance = f"{balance:.2f}"
            
            text = f"Api Key - {message.from_user.id}\n\n"
            text += f"Video Plays - {link_clicks}\n\n"
            text += f"Balance - ${formatted_balance}\n\n"
            text += upi
            text += f"\n\nTraffic Link - {traffic.text}"
            
            await client.send_message(ADMIN, text)
            record_withdraw(message.from_user.id, True)
            await message.reply(f"Your Withdrawal Balance - ${formatted_balance}\n\nNow Your Withdrawal Send To Owner, If Everything Fullfill The Criteria Then You Will Get Your Payment Within 3 Working Days.")
    else:
        await message.reply("Your Video Plays Smaller Than 1000 Plays, Minimum Payout Is 1000 Video Plays or Link Clicks.")

@Client.on_message(filters.private & filters.command("notify") & filters.user(ADMIN))
async def show_notify(client, message):
    try:
        user_id_msg = await client.ask(message.from_user.id, "Now Send Me Api Key Of User")
        user_id = int(user_id_msg.text)
        
        sub = await client.ask(message.from_user.id, "Payment Is Cancelled Or Send Successfully. /send or /cancel")
        if sub.text == "/send":
            record_visit(user_id, 0)
            record_withdraw(user_id, False)
            await client.send_message(user_id, "Your Withdrawal Is Successfully Completed And Sended To Your Bank Account.")
            await message.reply("Success message sent to user.")
        elif sub.text == "/cancel":
            reason = await client.ask(message.from_user.id, "Send Me The Reason For Cancellation Of Payment")
            if reason.text:
                record_withdraw(user_id, False)
                await client.send_message(user_id, f"Your Payment Cancelled - {reason.text}")
                await message.reply("Cancellation message sent to user.")
        else:
            await message.reply("Invalid command. Use /send or /cancel.")
    except ValueError:
        await message.reply("Invalid API Key. Please send a numeric ID.")
    except Exception as e:
        await message.reply(f"An error occurred: {e}")
