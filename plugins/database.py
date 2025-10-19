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
# --- FIX 1: IMPORT STATEMENT THEEK KIYA GAYA HAI ---
from plugins.database import checkdb, db 
from Script import script
from TechVJ.util.file_properties import get_hash, get_name
from TechVJ.util.human_readable import humanbytes


# Ek naya function jo direct stream URL banayega
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
        # await checkdb.add_user(message.from_user.id, message.from_user.first_name) # This seems redundant, removed.
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

# ... (universal_handler and other functions remain the same as before) ...
# Paste your universal_handler, quality_link, update, link_start functions here...

# --- FIX 2: Sabhi Database Calls ko Update Kiya Gaya Hai ---

@Client.on_message(filters.private & filters.command("account"))
async def show_account(client, message):
    link_clicks = await db.get_count(message.from_user.id) # CHANGED
    if link_clicks and link_clicks > 0:
        balance = link_clicks / 1000.0
        formatted_balance = f"{balance:.2f}"
        response = f"<b>Your Api Key :- <code>{message.from_user.id}</code>\n\nVideo Plays :- {link_clicks} ( Delay To Show Data )\n\nBalance :- ${formatted_balance}</b>"
    else:
        response = f"<b>Your Api Key :- <code>{message.from_user.id}</code>\nVideo Plays :- 0 ( Delay To Show Data )\nBalance :- $0</b>"
    await message.reply(response)

@Client.on_message(filters.private & filters.command("withdraw"))
async def show_withdraw(client, message):
    w = await db.get_withdraw_status(message.from_user.id) # CHANGED
    if w: # Simplified check
        return await message.reply("One Withdrawal Is In Process Wait For Complete It")
    
    link_clicks = await db.get_count(message.from_user.id) # CHANGED
    if not link_clicks or link_clicks < 1000:
        return await message.reply("You Are Not Eligible For Withdrawal.\nMinimum Withdraw Is 1000 Link Clicks or Video Plays.")
    
    # Rest of the withdrawal logic
    confirm = await client.ask(message.from_user.id, "You Are Going To Withdraw All Your Link Clicks. Are You Sure You Want To Withdraw ?\nSend /yes or /no")
    if confirm.text == "/no":
        return await message.reply("Withdraw Cancelled By You ❌")
    
    # ... (Your pay, upi, bank logic remains here) ...
    pay = await client.ask(message.from_user.id, "Now Choose Your Payment Method, Click On In Which You Want Your Withdrawal.\n\n/upi - for upi, webmoney, airtm, capitalist\n\n/bank - for bank only")
    if pay.text == "/upi":
        # ... your upi logic
        pass
    elif pay.text == "/bank":
        # ... your bank logic
        pass
    else:
        return await message.reply("Wrong payment method selected.")
    # ... after getting upi/bank details ...

    traffic = await client.ask(message.from_user.id, "Now Send Me Your Traffic Source Link, If Your Link Click Are Fake Then You Will Not Receive Payment And Withdrawal Get Cancelled")
    if not traffic.text:
        return await message.reply("Wrong Traffic Source ❌")
        
    balance = link_clicks / 1000.0
    formatted_balance = f"{balance:.2f}"
    
    text = f"Api Key - {message.from_user.id}\n\n"
    # ... your message text logic...
    
    await client.send_message(ADMIN, text)
    await db.set_withdraw_status(message.from_user.id, True) # CHANGED
    await message.reply(f"Your Withdrawal Balance - ${formatted_balance}\n\nNow Your Withdrawal Send To Owner, If Everything Fullfill The Criteria Then You Will Get Your Payment Within 3 Working Days.")

@Client.on_message(filters.private & filters.command("notify") & filters.user(ADMIN))
async def show_notify(client, message):
    try:
        user_id_msg = await client.ask(message.from_user.id, "Now Send Me Api Key Of User")
        user_id = int(user_id_msg.text)
        
        sub = await client.ask(message.from_user.id, "Payment Is Cancelled Or Send Successfully. /send or /cancel")
        if sub.text == "/send":
            await db.reset_count(user_id)  # CHANGED (Resets count to 0)
            await db.set_withdraw_status(user_id, False) # CHANGED
            await client.send_message(user_id, "Your Withdrawal Is Successfully Completed And Sended To Your Bank Account.")
            await message.reply("Success message sent to user.")
        elif sub.text == "/cancel":
            reason = await client.ask(message.from_user.id, "Send Me The Reason For Cancellation Of Payment")
            if reason.text:
                await db.set_withdraw_status(user_id, False) # CHANGED
                await client.send_message(user_id, f"Your Payment Cancelled - {reason.text}")
                await message.reply("Cancellation message sent to user.")
        else:
            await message.reply("Invalid command. Use /send or /cancel.")
    except ValueError:
        await message.reply("Invalid API Key. Please send a numeric ID.")
    except Exception as e:
        await message.reply(f"An error occurred: {e}")
