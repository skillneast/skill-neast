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

routes = web.RouteTableDef()

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neasthub - The Future of Learning</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Bebas+Neue&display=swap');

        :root {
            --bg-dark: #0a0a0f;
            --accent-blue: #00e6e6;
            --accent-pink: #ff5757;
            --text-light: #e0e0e0;
        }

        body {
            margin: 0;
            font-family: 'Poppins', sans-serif;
            background: var(--bg-dark);
            color: var(--text-light);
            line-height: 1.6;
            overflow-x: hidden;
            scroll-behavior: smooth;
        }

        #particles-js {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background-color: var(--bg-dark);
        }

        section {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 50px 20px;
            text-align: center;
            position: relative;
            z-index: 1;
            opacity: 0;
            transform: translateY(50px);
            transition: opacity 1s ease-out, transform 1s ease-out;
            margin-bottom: 20px;
        }

        section.is-visible {
            opacity: 1;
            transform: translateY(0);
        }

        #hero {
            background: radial-gradient(circle, rgba(0, 230, 230, 0.05) 0%, rgba(10, 10, 15, 0.8) 70%);
            padding: 100px 20px;
        }

        h1, h2 {
            font-family: 'Bebas Neue', sans-serif;
            font-size: clamp(3em, 8vw, 6em);
            text-transform: uppercase;
            letter-spacing: 5px;
            background: linear-gradient(45deg, var(--accent-blue), var(--accent-pink));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        h2 {
            font-size: clamp(2em, 5vw, 4em);
            letter-spacing: 3px;
            margin-bottom: 20px;
        }

        p {
            font-size: 1.2em;
            max-width: 700px;
            margin: 20px auto;
        }
        
        .button {
            margin-top: 30px;
            padding: 15px 40px;
            font-size: 1.5em;
            background: var(--accent-blue);
            border: none;
            border-radius: 50px;
            color: var(--bg-dark);
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
            text-transform: uppercase;
            font-weight: 600;
        }

        .button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.4), transparent);
            transition: left 0.5s;
            transform: skewX(-20deg);
        }

        .button:hover::before {
            left: 100%;
        }

        .button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 25px var(--accent-blue);
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 30px;
            margin-top: 50px;
            width: 100%;
        }
        
        .feature-card {
            background: rgba(4, 4, 15, 0.8);
            padding: 40px;
            border-radius: 20px;
            border: 1px solid var(--accent-blue);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 0 0 10px rgba(0, 230, 230, 0.2);
        }

        .feature-card:hover {
            transform: translateY(-10px) scale(1.03);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6), 0 0 20px var(--accent-pink);
        }

        .feature-card span {
            font-size: 3em;
            display: block;
            margin-bottom: 10px;
            color: var(--accent-pink);
        }

        /* Modal */
        .modal {
            display: none;
            position: fixed;
            z-index: 10;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            justify-content: center;
            align-items: center;
        }

        .modal-content {
            background: linear-gradient(135deg, #1a0026, #4a006f);
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 5px 25px rgba(0, 0, 0, 0.7);
            text-align: center;
            position: relative;
            animation: modal-pop 0.3s forwards;
            border: 2px solid var(--accent-blue);
        }

        .modal-content h2 {
            color: var(--accent-pink);
            font-size: 2em;
        }
        
        .close-button {
            position: absolute;
            top: 10px;
            right: 20px;
            color: var(--text-light);
            font-size: 2em;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }

        .close-button:hover {
            transform: rotate(90deg);
            color: var(--accent-blue);
        }

        @keyframes modal-pop {
            from { transform: scale(0.8); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
        
    </style>
</head>
<body>

    <div id="particles-js"></div>

    <section id="hero">
        <h1>Welcome To Neasthub!</h1>
        <p>Transforming your future, one skill at a time. This is more than a platform, it's a revolution.</p>
        <button class="button" onclick="openModal()">Get Started</button>
    </section>

    <section id="features">
        <h2>Unlock Your Potential</h2>
        <div class="features-grid">
            <div class="feature-card">
                <span>🚀</span>
                <h3>Skill Mastery</h3>
                <p>Learn cutting-edge skills from top industry leaders. Our curriculum is designed for the future.</p>
            </div>
            <div class="feature-card">
                <span>💰</span>
                <h3>Monetize Your Talent</h3>
                <p>Turn your skills into a profitable career. We provide the tools and guidance to help you earn.</p>
            </div>
            <div class="feature-card">
                <span>🎓</span>
                <h3>Premium Courses</h3>
                <p>Access exclusive, meticulously crafted courses that give you an edge over the competition.</p>
            </div>
            <div class="feature-card">
                <span>🆓</span>
                <h3>Free & Open</h3>
                <p>Explore a vast library of free resources to kickstart your journey into the world of new skills.</p>
            </div>
        </div>
    </section>

    <section id="cta">
        <h2>Your Future Starts Now</h2>
        <p>The best time to start was yesterday. The next best time is now. Join the elite who are shaping the future.</p>
        <button class="button" onclick="openModal()">Join The Revolution</button>
    </section>

    <div id="myModal" class="modal">
        <div class="modal-content">
            <span class="close-button" onclick="closeModal()">&times;</span>
            <h2 class="modal-title">Neasthub</h2>
            <p>Your journey awaits. Click the button below to connect with Neasthub and start your path to greatness.</p>
            <button class="button" onclick="window.open('https://neasthub.com', '_blank')">Visit Now</button>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/particles.js@2.0.0/particles.min.js"></script>
    <script>
        // Modal functions
        const modal = document.getElementById('myModal');
        function openModal() {
            modal.style.display = 'flex';
        }
        function closeModal() {
            modal.style.display = 'none';
        }
        window.onclick = function(event) {
            if (event.target == modal) {
                closeModal();
            }
        }

        // Particles.js configuration
        particlesJS("particles-js", {
            "particles": {
                "number": {
                    "value": 80,
                    "density": {
                        "enable": true,
                        "value_area": 800
                    }
                },
                "color": {
                    "value": ["#00e6e6", "#ff5757"]
                },
                "shape": {
                    "type": "circle",
                    "stroke": {
                        "width": 0,
                        "color": "#000000"
                    },
                },
                "opacity": {
                    "value": 0.5,
                    "random": true,
                    "anim": {
                        "enable": false,
                    }
                },
                "size": {
                    "value": 3,
                    "random": true,
                    "anim": {
                        "enable": false,
                    }
                },
                "line_linked": {
                    "enable": true,
                    "distance": 150,
                    "color": "#ffffff",
                    "opacity": 0.4,
                    "width": 1
                },
                "move": {
                    "enable": true,
                    "speed": 1,
                    "direction": "none",
                    "random": false,
                    "straight": false,
                    "out_mode": "out",
                    "bounce": false,
                }
            },
            "interactivity": {
                "detect_on": "canvas",
                "events": {
                    "onhover": {
                        "enable": true,
                        "mode": "repulse"
                    },
                    "onclick": {
                        "enable": true,
                        "mode": "push"
                    },
                    "resize": true
                },
                "modes": {
                    "repulse": {
                        "distance": 100,
                        "duration": 0.4
                    },
                    "push": {
                        "particles_nb": 4
                    },
                }
            },
            "retina_detect": true
        });

        // Scroll animations with IntersectionObserver
        const sections = document.querySelectorAll('section');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                } else {
                    entry.target.classList.remove('is-visible');
                }
            });
        }, { threshold: 0.1 });
        
        sections.forEach(section => {
            observer.observe(section);
        });
    </script>
</body>
</html>
"""

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.Response(text=html_content, content_type='text/html')

@routes.get(r"/{path}/{user_path}/{second}/{third}", allow_head=True)
async def stream_handler(request: web.Request):
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
        return web.Response(text=html_content, content_type='text/html')
    return 

@routes.post('/click-counter')
async def handle_click(request):
    data = await request.json()  # Get the JSON body
    user_id = int(data.get('user_id'))  # Extract user_id from the request
    today = datetime.now().strftime('%Y-%m-%d')

    user_agent = request.headers.get('User-Agent')
    is_chrome = "Chrome" in user_agent or "Google Inc" in user_agent

    if is_chrome:
        visited_cookie = request.cookies.get('visited')
    else:
        return

    if visited_cookie == today:
        return
    else:
        response = web.Response(text="Hello, World!")
        response.set_cookie('visited', today, max_age=24*60*60)
        u = get_count(user_id)
        if u:
            c = int(u + 1)
            record_visit(user_id, c)
        else:
            c = int(1)
            record_visit(user_id, c)
        return response

@routes.get('/{short_link}', allow_head=True)
async def get_original(request: web.Request):
    short_link = request.match_info["short_link"]
    original = await decode(short_link)
    if original:
        link = f"{STREAM_URL}link?{original}"
        raise web.HTTPFound(link)  # Redirect to the constructed link 
    else:
        return web.Response(text=html_content, content_type='text/html')

@routes.get('/link', allow_head=True)
async def visits(request: web.Request):
    user = request.query.get('u')
    watch = request.query.get('w')
    second = request.query.get('s')
    third = request.query.get('t')
    data = await encode(watch)
    user_id = await encode(user)
    sec_id = await encode(second)
    th_id = await encode(third)
    link = f"{STREAM_URL}{data}/{user_id}/{sec_id}/{th_id}"
    raise web.HTTPFound(link)  # Redirect to the constructed link

@routes.get(r"/dl/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        return await media_streamer(request, id, secure_hash)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))

class_cache = {}

async def media_streamer(request: web.Request, id: int, secure_hash: str):
    range_header = request.headers.get("Range", 0)
    
    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]
    
    if MULTI_CLIENT:
        logging.info(f"Client {index} is now serving {request.remote}")

    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
        logging.debug(f"Using cached ByteStreamer object for client {index}")
    else:
        logging.debug(f"Creating new ByteStreamer object for client {index}")
        tg_connect = ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect
    logging.debug("before calling get_file_properties")
    file_id = await tg_connect.get_file_properties(id)
    logging.debug("after calling get_file_properties")
    
    file_size = file_id.file_size

    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1

    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
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

