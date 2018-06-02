import inkyphatwidget
import inkyphat
import os
from PIL import Image

async def widget(loop, rect):
    left, top, right, bottom = rect
    icon = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img', 'ahiruyaki.png'))
    inkyphat.paste(icon, (left, top), inkyphat.create_mask(icon))
    inkyphatwidget.request()
