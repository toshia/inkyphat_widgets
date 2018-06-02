#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import ImageFont
import asyncio
import inkyphat

# uncomment to rotate display
#inkyphat.set_rotation(180)

loop = asyncio.get_event_loop()

##
## Widgets
## それぞれのウィジェットは、不要ならコメントアウトすれば非表示にできます。
##

#
# Redmine
#

import inkyphatwidget.redmine
asyncio.ensure_future(inkyphatwidget.redmine.widget(
    loop,
    (4, 4, inkyphat.WIDTH - 58, 85),
    url="https://dev.mikutter.hachune.net/projects/mikutter/issues.json?query_id=14&limit=5&key=XXXXXXXX",
    font=ImageFont.truetype(inkyphat.fonts.Koruri, 12)
))

#
# ahiruyaki
#

import inkyphatwidget.ahiruyaki
ahiruyaki_x = inkyphat.WIDTH - 70
ahiruyaki_y = 15
asyncio.ensure_future(inkyphatwidget.ahiruyaki.widget(
    loop,
    (ahiruyaki_x, ahiruyaki_y, ahiruyaki_x + 65, ahiruyaki_y + 60)
))

#
# MPC
#

import inkyphatwidget.mpc
asyncio.ensure_future(inkyphatwidget.mpc.widget(
    loop,
    (4, 86, inkyphat.WIDTH - 4, inkyphat.HEIGHT - 4),
    font=ImageFont.truetype(inkyphat.fonts.Koruri, 12),
    host='localhost',
    port=6600
))

#
# Boot
#

asyncio.ensure_future(inkyphatwidget.widget(loop))
loop.run_forever()
