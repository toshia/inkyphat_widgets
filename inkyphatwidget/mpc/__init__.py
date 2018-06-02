import inkyphatwidget
import inkyphatwidget.textutil
import inkyphat
import os
from PIL import Image, ImageFont
import asyncio

resource_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
status_icon = { 'play': Image.open(os.path.join(resource_dir, 'play.png')),
                'pause': Image.open(os.path.join(resource_dir, 'pause.png')),
                'stop': Image.open(os.path.join(resource_dir, 'stop.png'))}

async def widget(loop, rect, font=ImageFont.truetype(inkyphat.fonts.Koruri, 12), host='localhost', port=6600):
    error_wait = 1
    while True:
        try:
            reader, writer = await asyncio.open_connection(host, port)
            while True:
                line = await reader.readline()
                if line.startswith(b"OK"):
                    break
            print("mpc: connected.")
            error_wait = 1
            await observe(loop, rect, reader, writer, font=font)
        except Exception as exc:
            print("mpc: unexpected error: %s: %s" % (type(exc), exc))
            if error_wait < 60:
                error_wait *= 2
            draw_error(rect, exc, font=font)
            await asyncio.sleep(error_wait)

async def observe(loop, rect, reader, writer, font=None):
    left, top, right, bottom = rect
    rewind_buffer = None
    while True:
        song = await song_data(reader, writer, loop)
        state = await song_status(reader, writer, loop)
        if 'Title' in song:
            song_hash = "%s-%s" % (state['state'], song['Title'])
            if song_hash != rewind_buffer:
                rewind_buffer = song_hash
                draw(rect, state['state'], song['Title'], font)
        await observe_playing_data(reader, writer, loop)

def draw_error(rect, exc, font=None):
    left, top, right, bottom = rect
    inkyphat.rectangle(rect, fill=inkyphat.WHITE)
    icon = Image.open(os.path.join(resource_dir, 'error.png'))
    inkyphat.paste(icon, (left, top), inkyphat.create_mask(icon))
    inkyphatwidget.textutil.print_width_limited((left + 16, top), "%s (%s)" % (exc, type(exc).__name__), inkyphat.RED, font, right - left - 16)
    inkyphatwidget.request()

def draw(rect, state, title, font):
    left, top, right, bottom = rect
    inkyphat.rectangle(rect, fill=inkyphat.WHITE)
    text_left = left
    icon = status_icon.get(state, None)
    if icon:
        inkyphat.paste(icon, (left, top), inkyphat.create_mask(icon))
        text_left += 16
    inkyphatwidget.textutil.print_width_limited((text_left, top), title, inkyphat.BLACK, font, right - text_left)
    inkyphatwidget.request()


async def song_data(reader, writer, loop):
    writer.write(b"currentsong\n")
    result = {}
    while True:
        line = await reader.readline()
        line = line.decode('utf-8')
        if line == "OK\n":
            break
        k, v = line.split(':', maxsplit=1)
        result[k.strip()] = v.strip()
    return result

async def song_status(reader, writer, loop):
    writer.write(b"status\n")
    result = {}
    while True:
        line = await reader.readline()
        line = line.decode('utf-8')
        if line == "OK\n":
            break
        k, v = line.split(':', maxsplit=1)
        result[k.strip()] = v.strip()
    return result

async def observe_playing_data(reader, writer, loop):
    writer.write(b"idle player\n")
    while True:
        line = await reader.readline()
        if line == b"OK\n":
            break
