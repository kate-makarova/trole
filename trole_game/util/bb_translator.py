import re


def translate_bb(text):
    patterns = [
        (r"\[url=(.*?)\](.*?)\[\/url\]", '<a href="{find1}">{find2}</a>', 2),
        (r"\[font=(.*?)\](.*?)\[\/font\]", '<span style="font-family:{find1}">{find2}</span>', 2),
        (r"\[color=(.*?)\](.*?)\[\/color\]", '<span style="color:{find1}">{find2}</span>', 2),
        (r"\[size=(.*?)\](.*?)\[\/size\]", '<span style="fond-size:{find1}em">{find2}</span>', 2),
        (r"\[b\](.*?)\[\/b\]", '<b>{find1}</b>', 1),
        (r"\[i\](.*?)\[\/i\]", '<i>{find1}</i>', 1),
        (r"\[u\](.*?)\[\/u\]", '<u>{find1}</u>', 1),
        (r"\[s\](.*?)\[\/s\]", '<s>{find1}</s>', 1),
        (r"\[img\](.*?)\[\/img\]", '<img src="{find1}" />', 1),
    ]

    for pattern in patterns:
        matches = re.finditer(pattern[0], text)

        if pattern[2] == 2:
            for match in matches:
                match_start = match.start(0)
                match_end = match.end(0)
                find1 = match.group(1)
                find2 = match.group(2)

                replacement = pattern[1].replace('{find1}', find1)
                replacement = replacement.replace('{find2}', translate_bb(find2))
                text = text[:match_start] + replacement + text[match_end:]

        if pattern[2] == 1:
            for match in matches:
                match_start = match.start(0)
                match_end = match.end(0)
                find1 = match.group(1)

                replacement = pattern[1].replace('{find1}', translate_bb(find1))
                text = text[:match_start] + replacement + text[match_end:]

    return text


