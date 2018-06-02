import inkyphat

def print_width_limited(pos, text, color, font, width):
    truncated_text = truncate_by_width(text, font, width, None)
    inkyphat.text(pos, truncated_text, color, font)

def truncate_by_width(text, font, limit_width, search):
    if search:
        if abs(search[0] - search[1]) <= 1:
            return text[0:int(search[0])] + "…"
        pos = (search[0] + search[1])/2
        trim_text = text[0:int(pos)] + "…"
        fw, fh = font.getsize(trim_text)
        if fw <= limit_width:
            return truncate_by_width(text, font, limit_width, (pos, search[1]))
        else:
            return truncate_by_width(text, font, limit_width, (search[0], pos))
    else:
        fw, fh = font.getsize(text)
        if fw <= limit_width:
            return text
        else:
            return truncate_by_width(text, font, limit_width, (0, len(text)))
