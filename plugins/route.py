# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re, math, logging, secrets, mimetypes, time
from info import *
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine
from plugins.start import decode, encode 
from datetime import datetime
from plugins.database import record_visit, get_count
from TechVJ.bot import multi_clients, work_loads, TechVJBot
from TechVJ.server.exceptions import FIleNotFound, InvalidHash
from TechVJ import StartTime, __version__
from TechVJ.util.custom_dl import ByteStreamer
from TechVJ.util.time_format import get_readable_time
from TechVJ.util.render_template import render_page
from TechVJ.util.file_properties import get_file_ids

import asyncio # <<<<<<<<<<<<<<<< NAYA IMPORT

routes = web.RouteTableDef()

# <<<<<<<<<<<<<<<<<<<< NAYA LOCK OBJECT
# Global lock for Pyrogram client access to prevent concurrent database access issues
pyrogram_db_lock = asyncio.Lock() 

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to VJ Disk</title>
    <style>
        body {
            margin: 0;
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #ff7e5f, #feb47b);
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            text-align: center;
            perspective: 1000px;
        }
        
        .container {
            transform-style: preserve-3d;
            animation: rotate 10s infinite linear;
        }

        @keyframes rotate {
            from {
                transform: rotateY(0deg);
            }
            to {
                transform: rotateY(360deg);
            }
        }

        h1 {
            font-size: 4em;
            text-shadow: 2px 2px 10px rgba(0, 0, 0, 0.5);
        }

        p {
            font-size: 1.5em;
            margin-top: 20px;
            text-shadow: 1px 1px 5px rgba(0, 0, 0, 0.5);
        }

        .button {
            margin-top: 30px;
            padding: 15px 30px;
            font-size: 1.2em;
            background-color: #4CAF50; /* Green */
            border: none;
            border-radius: 5px;
            color: white;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        .button:hover {
            background-color: #45a049; /* Darker green */
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome To VJ Disk!</h1>
        <p>Your ultimate destination for streaming and sharing videos!</p>
        <p>Explore a world of entertainment at your fingertips.</p>
        <button class="button" onclick="alert('Explore Now!')">Get Started</button>
    </div>
</body>
</html>
"""

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.Response(text=html_content, content_type='text/html')

@routes.get(r"/{path}/{user_path}/{second}/{third}", allow_head=True)
async def stream_handler_player(request: web.Request): # Renamed to avoid conflict with /dl stream_handler
    try:
        path = request.match_info["path"]
        user_path = request.match_info["user_path"]
        sec = request.match_info["second"]
        th = request.match_info["third"]
        id = int(await decode(path))
        user_id = int(await decode(user_path))
        secid = int(await decode(sec))
        thid = int(await decode(th))
        return web.Response(text=await render_page(id, user_id, secid, thid), content_type='text/html')
    except Exception as e:
        logging.error(f"Error in stream_handler_player: {e}", exc_info=True)
        return web.Response(text=html_content, content_type='text/html')
    # No return None here, the except block returns a response or the try block does.

@routes.post('/click-counter')
async def handle_click(request):
    try:
        data = await request.json()  # Get the JSON body
        user_id = int(data.get('user_id'))  # Extract user_id from the request
        today = datetime.now().strftime('%Y-%m-%d')

        user_agent = request.headers.get('User-Agent')
        is_chrome = "Chrome" in user_agent or "Google Inc" in user_agent

        if is_chrome:
            visited_cookie = request.cookies.get('visited')
        else:
            # Not a Chrome browser, or user-agent not indicating it's Chrome.
            # You might want to log this or handle differently.
            # For now, we'll silently return.
            logging.info(f"Skipping click counter for non-Chrome user agent: {user_agent}")
            return web.Response(status=200, text="Not processed for this browser.")


        if visited_cookie == today:
            logging.info(f"User {user_id} already visited today. Skipping.")
            return web.Response(status=200, text="Already visited today.")
        else:
            response = web.Response(text="Click counter updated!")
            response.set_cookie('visited', today, max_age=24*60*60, httponly=True) # Added httponly for security
            u = get_count(user_id)
            if u:
                c = int(u + 1)
                record_visit(user_id, c)
                logging.info(f"User {user_id} click count updated to {c}.")
            else:
                c = int(1)
                record_visit(user_id, c)
                logging.info(f"User {user_id} first click recorded.")
            return response
    except Exception as e: # Catch specific exceptions or log the exception
        logging.error(f"Error in handle_click: {e}", exc_info=True)
        return web.Response(status=500, text="Internal Server Error") # Return a proper error response

@routes.get('/{short_link}', allow_head=True)
async def get_original(request: web.Request):
    short_link = request.match_info["short_link"]
    original = await decode(short_link)
    if original:
        link = f"{STREAM_URL}link?{original}"
        raise web.HTTPFound(link)  # Redirect to the constructed link 
    else:
        logging.warning(f"Invalid short link received: {short_link}")
        return web.Response(text=html_content, content_type='text/html', status=400) # Bad Request for invalid link

@routes.get('/link', allow_head=True)
async def visits(request: web.Request):
    user = request.query.get('u')
    watch = request.query.get('w')
    second = request.query.get('s')
    third = request.query.get('t')
    
    # Ensure all query params are present to avoid errors or incomplete links
    if not all([user, watch, second, third]):
        logging.warning(f"Missing query parameters in /link route. Received: u={user}, w={watch}, s={second}, t={third}")
        return web.Response(text="Missing link parameters.", status=400)

    data = await encode(watch)
    user_id_encoded = await encode(user) # Renamed to avoid confusion with actual user_id
    sec_id_encoded = await encode(second) # Renamed
    th_id_encoded = await encode(third) # Renamed
    link = f"{STREAM_URL}{data}/{user_id_encoded}/{sec_id_encoded}/{th_id_encoded}"
    raise web.HTTPFound(link)  # Redirect to the constructed link

@routes.get(r"/dl/{path:\S+}", allow_head=True)
async def stream_handler_dl(request: web.Request): # Renamed to avoid name conflict
    logging.info(f"Stream handler called for path: {request.match_info['path']}")
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")

        logging.info(f"Acquiring Pyrogram DB lock for ID: {id}, Hash: {secure_hash}")
        async with pyrogram_db_lock: # <<<<<<<<<<<<<<<< YAHAN LOCK USE HOGA
            logging.info(f"Pyrogram DB lock acquired for ID: {id}. Calling media_streamer.")
            response = await media_streamer(request, id, secure_hash)
            logging.info(f"media_streamer returned for ID: {id}. Releasing Pyrogram DB lock.")
            return response
            
    except InvalidHash as e:
        logging.error(f"InvalidHash error in stream_handler_dl: {e}", exc_info=True)
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        logging.error(f"FIleNotFound error in stream_handler_dl: {e}", exc_info=True)
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError) as e:
        logging.warning(f"Connection related error in stream_handler_dl: {type(e).__name__}", exc_info=True)
        pass # These are often transient network errors, just pass for now or log more specifically
    except Exception as e:
        logging.critical(f"Unhandled critical error in stream_handler_dl: {e}", exc_info=True)
        raise web.HTTPInternalServerError(text=str(e))

class_cache = {}

async def media_streamer(request: web.Request, id: int, secure_hash: str):
    logging.debug(f"media_streamer executing for ID: {id}")
    range_header = request.headers.get("Range", 0)
    
    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]
    
    if MULTI_CLIENT:
        logging.info(f"Client {index} is now serving {request.remote} for ID: {id}")

    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
        logging.debug(f"Using cached ByteStreamer object for client {index}, ID: {id}")
    else:
        logging.debug(f"Creating new ByteStreamer object for client {index}, ID: {id}")
        tg_connect = ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect
    
    logging.debug(f"Before calling get_file_properties for ID: {id}")
    file_id = await tg_connect.get_file_properties(id)
    logging.debug(f"After calling get_file_properties for ID: {id}")
    
    if not file_id:
        logging.error(f"File properties not found for ID: {id}. This might indicate an issue with get_file_properties or file not existing.")
        raise FIleNotFound(f"File with ID {id} not found.")

    # Hash check, if needed
    # if secure_hash and secure_hash != get_hash_of_file(file_id): # You'd need to implement get_hash_of_file
    #     raise InvalidHash("Invalid file hash.")

    file_size = file_id.file_size

    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
        logging.debug(f"Range header present: bytes {from_bytes}-{until_bytes}/{file_size}")
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1
        logging.debug(f"No Range header. Serving full file from {from_bytes} to {until_bytes}/{file_size}")


    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
        logging.warning(f"Range not satisfiable for ID: {id}. Requested range: {from_bytes}-{until_bytes}, File size: {file_size}")
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)
    
    logging.debug(f"Yielding file for ID: {id}, Offset: {offset}, Length: {req_length}")
    body = tg_connect.yield_file(
        file_id, index, offset, first_part_cut, last_part_cut, part_count, chunk_size
    )

    mime_type = file_id.mime_type
    file_name = file_id.file_name
    disposition = "attachment"

    if mime_type:
        if not file_name:
            try:
                file_name = f"{secrets.token_hex(2)}.{mime_type.split('/')[1]}"
            except (IndexError, AttributeError):
                file_name = f"{secrets.token_hex(2)}.unknown"
    else:
        if file_name:
            mime_type = mimetypes.guess_type(file_id.file_name)
        else:
            mime_type = "application/octet-stream"
            file_name = f"{secrets.token_hex(2)}.unknown"

    logging.debug(f"Serving response for ID: {id} with MIME: {mime_type}, Filename: {file_name}")
    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": f"{mime_type}",
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )
