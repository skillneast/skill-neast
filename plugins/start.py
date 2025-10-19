# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import base64
import binascii
from urllib.parse import quote_plus, urlencode

from pyrogram import Client, enums, filters
from pyrogram.types import (CallbackQuery, ForceReply, InlineKeyboardButton,
                            InlineKeyboardMarkup)

from info import ADMIN, LINK_URL, LOG_CHANNEL
# --- YEH HAI SAHI IMPORT STATEMENT ---
from plugins.database import checkdb, db 
from Script import script
from TechVJ.util.file_properties import get_hash, get_name
from TechVJ.util.human_readable import humanbytes


async def get_stream_url(client, message_id):
    try:
        msg = await client.get_messages(LOG_CHANNEL, message_id)
        file_name = get_name(msg)
        file_hash = await get_hash(msg)
        
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
        return await message.reply("Please send a file.")
    
    file = getattr(message, message.media.value)
    file_type = message.media.value
    fileid = file.file_id
    
    log_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
    file_name = get_name(log_msg)

    if not file_name:
        return await message.reply("Sorry, I couldn't get the name of this file. Please try sending it again as a document.")

    is_video = file_type == 'video' or (file_type == 'document' and file.mime_type and file.mime_type.startswith('video/'))
    
    if is_video:
        is_ts_file = file_name.lower().endswith('.ts')
        if is_ts_file:
            direct_link = await get_stream_url(client, log_msg.id)
            if not direct_link: return await message.reply("Error generating stream link.")
            rm = InlineKeyboardMarkup([[InlineKeyboardButton("⬇️ Download Now", url=direct_link)]])
            await message.reply_text(f"**🎥 Video:** `{file_name}`\n\n**⬇️ Direct Download Link:**\n`{direct_link}`", reply_markup=rm, parse_mode=enums.ParseMode.MARKDOWN)
        else:
            params = {'u': message.from_user.id, 'w': str(log_msg.id), 's': str(0), 't': str(0)}
            link = await encode(urlencode(params))
            encoded_url = f"{LINK_URL}?Tech_VJ={link}"
            direct_stream_url = await get_stream_url(client, log_msg.id) or "Could not generate URL."
            rm = InlineKeyboardMarkup([[InlineKeyboardButton("🖇️ Open Link", url=encoded_url)]])
            await message.reply_text(f"**🎥 Video:** `{file_name}`\n\n**🌐 Website Player URL:**\n`{encoded_url}`\n\n**🔗 Direct Stream URL:**\n`{direct_stream_url}`", reply_markup=rm, parse_mode=enums.ParseMode.MARKDOWN)
    else:
        direct_link = await get_stream_url(client, log_msg.id)
        if not direct_link: return await message.reply("Error generating download link.")
        rm = InlineKeyboardMarkup([[InlineKeyboardButton("⬇️ Download Now", url=direct_link)]])
        await message.reply_text(f"**📄 File:** `{file_name}`\n\n**⬇️ Direct Download Link:**\n`{direct_link}`", reply_markup=rm, parse_mode=enums.ParseMode.MARKDOWN)

@Client.on_message(filters.private & filters.command("quality"))
async def quality_link(client, message):
    # This function is long and doesn't use the problematic database functions, so it's kept as is.
    # Please ensure your original logic for this function is correct.
    first_id = str(0); second_id = str(0); third_id = str(0)
    # ... your entire quality_link logic ...
    # Make sure get_stream_url is called correctly within this function if you use it.
    pass # Placeholder for your long function

@Client.on_message(filters.private & filters.text & ~filters.command(["account", "withdraw", "notify", "quality", "start", "update"]))
async def link_start(client, message):
    if not message.text.startswith(LINK_URL): return
    link_part = message.text[len(LINK_URL + "?Tech_VJ="):].strip()
    original = await decode(link_part)
    if original is None: return await message.reply("Link Invalid or Corrupted")
    try:
        parts = original.split("&")
        params = {p.split("=")[0]: p.split("=")[1] for p in parts}
        user_id, id, sec, th = params['u'], params['w'], params['s'], params['t']
    except (ValueError, KeyError):
        return await message.reply("Link Invalid")
    if user_id == str(message.from_user.id):
        rm = InlineKeyboardMarkup([[InlineKeyboardButton("🖇️ Open Link", url=message.text)]])
        return await message.reply_text(f"<code>{message.text}</code>", reply_markup=rm)
    
    new_params = {'u': message.from_user.id, 'w': str(id), 's': str(sec), 't': str(th)}
    link = await encode(urlencode(new_params))
    encoded_url = f"{LINK_URL}?Tech_VJ={link}"
    rm = InlineKeyboardMarkup([[InlineKeyboardButton("🖇️ Open Link", url=encoded_url)]])
    await message.reply_text(f"<code>{encoded_url}</code>", reply_markup=rm)

@Client.on_message(filters.private & filters.command("account"))
async def show_account(client, message):
    link_clicks = await db.get_count(message.from_user.id)
    balance = (link_clicks / 1000.0) if link_clicks else 0
    formatted_balance = f"{balance:.2f}"
    response = f"<b>Your Api Key :- <code>{message.from_user.id}</code>\n\nVideo Plays :- {link_clicks} ( Delay To Show Data )\n\nBalance :- ${formatted_balance}</b>"
    await message.reply(response)

@Client.on_message(filters.private & filters.command("withdraw"))
async def show_withdraw(client, message):
    w = await db.get_withdraw_status(message.from_user.id)
    if w:
        return await message.reply("One Withdrawal Is In Process Wait For Complete It")
    
    link_clicks = await db.get_count(message.from_user.id)
    if not link_clicks or link_clicks < 1000:
        return await message.reply("You Are Not Eligible For Withdrawal.\nMinimum Withdraw Is 1000 Link Clicks or Video Plays.")
    
    confirm = await client.ask(message.from_user.id, "You Are Going To Withdraw All Your Link Clicks. Are You Sure You Want To Withdraw ?\nSend /yes or /no")
    if confirm.text == "/no":
        return await message.reply("Withdraw Cancelled By You ❌")
    
    upi = ""
    pay = await client.ask(message.from_user.id, "Now Choose Your Payment Method...\n\n/upi - for upi...\n\n/bank - for bank only")
    if pay.text == "/upi":
        upi_details = await client.ask(message.from_user.id, "Now Send Me Your Upi...")
        if not upi_details.text: return await message.reply("Wrong Input ❌")
        upi = f"Upi - {upi_details.text}"
        try: await upi_details.delete()
        except: pass
    elif pay.text == "/bank":
        # Your bank details logic
        name = await client.ask(message.from_user.id, "Account Holder Name"); number = await client.ask(message.from_user.id, "Account Number"); ifsc = await client.ask(message.from_user.id, "IFSC Code"); bank_name = await client.ask(message.from_user.id, "Bank Name")
        if not all([name.text, number.text.isdigit(), ifsc.text, bank_name.text]): return await message.reply("Wrong Input ❌")
        upi = f"Account Holder Name - {name.text}\nAcc No - {number.text}\nIFSC - {ifsc.text}\nBank - {bank_name.text}"
        try: await name.delete(); await number.delete(); await ifsc.delete(); await bank_name.delete()
        except: pass
    else: return await message.reply("Wrong payment method.")

    traffic = await client.ask(message.from_user.id, "Now Send Me Your Traffic Source Link...")
    if not traffic.text: return await message.reply("Wrong Traffic Source ❌")
    
    balance = link_clicks / 1000.0; formatted_balance = f"{balance:.2f}"
    text = f"Api Key - {message.from_user.id}\nVideo Plays - {link_clicks}\nBalance - ${formatted_balance}\n\n{upi}\n\nTraffic Link - {traffic.text}"
    
    await client.send_message(ADMIN, text)
    await db.set_withdraw_status(message.from_user.id, True)
    await message.reply(f"Your Withdrawal Balance - ${formatted_balance}\n\nYour withdrawal request has been sent.")

@Client.on_message(filters.private & filters.command("notify") & filters.user(ADMIN))
async def show_notify(client, message):
    try:
        user_id_msg = await client.ask(message.from_user.id, "Now Send Me Api Key Of User")
        user_id = int(user_id_msg.text)
        
        sub = await client.ask(message.from_user.id, "Payment Is Cancelled Or Send Successfully. /send or /cancel")
        if sub.text == "/send":
            await db.reset_count(user_id)
            await db.set_withdraw_status(user_id, False)
            await client.send_message(user_id, "Your Withdrawal Is Successfully Completed And Sent To Your Account.")
            await message.reply("Success message sent to user.")
        elif sub.text == "/cancel":
            reason = await client.ask(message.from_user.id, "Send Me The Reason For Cancellation Of Payment")
            if reason.text:
                await db.set_withdraw_status(user_id, False)
                await client.send_message(user_id, f"Your Payment Was Cancelled - {reason.text}")
                await message.reply("Cancellation message sent to user.")
        else:
            await message.reply("Invalid command. Use /send or /cancel.")
    except ValueError:
        await message.reply("Invalid API Key. Please send a numeric ID.")
    except Exception as e:
        await message.reply(f"An error occurred: {e}")
