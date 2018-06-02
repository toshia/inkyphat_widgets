from PIL import Image
import asyncio
import inkyphat
import inkyphatwidget.textutil
import json
import os
import urllib.request

resource_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
status_icon = { 13: Image.open(os.path.join(resource_dir, 'inbox.png')),
                12: Image.open(os.path.join(resource_dir, 'merge.png')),
                9: Image.open(os.path.join(resource_dir, 'patch.png'))}

async def widget(loop, rect, url=None, line_count=5, col_width=(32, 48), font=None):
    draw_table_border(rect, line_count, col_width)
    inkyphatwidget.request()
    rewind_buffer = [None for i in range(line_count)]
    error_wait = 1
    while True:
        try:
            draw_once(loop, rect, rewind_buffer, url=url, line_count=line_count, col_width=col_width, font=font)
            print("redmine: connected.")
            error_wait = 1
            await asyncio.sleep(60)
        except urllib.error.URLError as exc:
            # Redmineサーバの問題。過負荷などの可能性があるため、リトライ間隔を多めに取る
            print("redmine: connection refused. try again in {0}s lator. (urllib.error.URLError: {1})".format(error_wait, exc))
            if error_wait < 60:
                error_wait *= 2
            await asyncio.sleep(error_wait)
        except (http.client.HTTPException, ConnectionError) as exc:
            # ネットワークエラー。サーバがビジーなわけではないので１秒ずつ間隔を開けながらリトライする
            print("redmine: connection closed by peer. try again in {0}s lator. ({1})".format(error_wait, exc))
            if error_wait < 60:
                error_wait += 1
            await asyncio.sleep(error_wait)

def draw_once(loop, rect, rewind_buffer, url=None, line_count=5, col_width=(32, 48), font=None):
    left, top, right, bottom = rect
    line_height = int((bottom - top) / line_count)
    rewind_flag = False
    parsed = get_tickets(url)
    for index, item in enumerate(parsed['issues']):
        if len(rewind_buffer) <= index:
            break
        ticket_hash = "%d-%d-%s" % (item['id'], item['status']['id'], item['subject'])
        if rewind_buffer[index] == ticket_hash:
            continue
        rewind_flag = True
        rewind_buffer[index] = ticket_hash
        y = top + index * line_height
        draw_row((left+1, y+1, right-1, y + line_height -1),
                 item['id'], item['status']['id'], item['subject'], font, col_width)
    if rewind_flag:
        inkyphatwidget.request()
        print("redmine: rewind!")


def draw_row(rect, ticket_id, status_id, subject, font, col_width):
    left, top, right, bottom = rect
    draw_ticket_id((left, top, left+col_width[0]-2, bottom),            str(ticket_id), font)
    draw_status((left+col_width[0], top, left+col_width[1]-2, bottom),  status_id)
    draw_subject((left+col_width[1], top, right, bottom),             subject, font)

def draw_ticket_id(rect, label, font):
    inkyphat.rectangle(rect, fill=inkyphat.WHITE)
    left, top, right, bottom = rect
    y_middle = (top + bottom)/2
    fw, fh = font.getsize(label)
    x = right - fw
    y = y_middle - fh/2
    inkyphat.text((x, y), label, inkyphat.BLACK, font)

def draw_status(rect, status_id):
    inkyphat.rectangle(rect, fill=inkyphat.WHITE)
    left, top, right, bottom = rect
    icon = status_icon.get(status_id)
    if icon:
        inkyphat.paste(icon, (left, top), inkyphat.create_mask(icon))

def draw_subject(rect, label, font):
    inkyphat.rectangle(rect, fill=inkyphat.WHITE)
    left, top, right, bottom = rect
    y_middle = (top + bottom)/2
    fw, fh = font.getsize(label)
    y = y_middle - fh/2
    inkyphatwidget.textutil.print_width_limited((left, y), label, inkyphat.BLACK, font, right - left - 1)

def draw_table_border(rect, line_count, col_width):
    left, top, right, bottom = rect
    line_height = int((bottom - top) / line_count)
    bottom = (line_height * line_count) + top
    inkyphat.line((left, top, left, bottom), inkyphat.BLACK)
    inkyphat.line((right, top, right, bottom), inkyphat.BLACK)
    # 横の罫線と上下の縁
    for i in range(line_count+1):
        height = top + i*line_height
        inkyphat.line((left, height, right, height), inkyphat.BLACK)
        # 縦の罫線
    for pos in col_width:
        inkyphat.line((left + pos, top, left + pos, bottom), inkyphat.BLACK)

def get_tickets(url):
    try:
        res = urllib.request.urlopen(url)
        return json.loads(res.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print('HTTPError: ', e)
    except json.JSONDecodeError as e:
        print('JSONDecodeError: ', e)
