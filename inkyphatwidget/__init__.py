import inkyphat
import asyncio

queue = asyncio.Queue()
current_request_id = 0

def request():
    queue.put_nowait(get_request_id())

def get_request_id():
    global current_request_id
    current_request_id += 1
    return current_request_id

async def widget(loop):
    while True:
        accept_id = get_request_id()
        request_id = await queue.get()
        if accept_id < request_id:
            print("inkyphat_redraw: redraw")
            inkyphat.show()
