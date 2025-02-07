import re


def translate_bb(text):
    text = '<p>' + text.replace("\n", '</p><p>') + '</p>'
    patterns = [
        (r"\[url=(.*?)\](.*?)\[\/url\]", '<a href="{find1}">{find2}</a>', 2),
        (r"\[font=(.*?)\](.*?)\[\/font\]", '<span style="font-family:{find1}">{find2}</span>', 2),
        (r"\[color=(.*?)\](.*?)\[\/color\]", '<span style="color:{find1}">{find2}</span>', 2),
        (r"\[size=(.*?)\](.*?)\[\/size\]", '<span style="font-size:{find1}em">{find2}</span>', 2),
        (r"\[b\](.*?)\[\/b\]", '<b>{find1}</b>', 1),
        (r"\[i\](.*?)\[\/i\]", '<i>{find1}</i>', 1),
        (r"\[u\](.*?)\[\/u\]", '<u>{find1}</u>', 1),
        (r"\[s\](.*?)\[\/s\]", '<s>{find1}</s>', 1),
        (r"\[img\](.*?)\[\/img\]", '<img src="{find1}" />', 1),
        (r"\[left\](.*?)\[\/left\]", '<span style="display: block; text-align: left">{find1}</span>', 1),
        (r"\[right\](.*?)\[\/right\]", '<span display: block; text-align: right>{find1}</span>', 1),
        (r"\[center\](.*?)\[\/center\]", '<span style="display: block; text-align: center">{find1}</span>', 1),
        (r"\[justify\](.*?)\[\/justify\]", '<span style="display: block; text-align: left">{find1}</span>', 1),
        (r"\[sub\](.*?)\[\/sub\]", '<sub>{find1}</sub>', 1),
        (r"\[sup\](.*?)\[\/sup\]", '<sup>{find1}</sup>', 1),
        (r"\[ul\](.*?)\[\/ul\]", '<ul>{find1}</ul>', 1),
        (r"\[ol\](.*?)\[\/ol\]", '<ol>{find1}</ol>', 1),
        (r"\[li\](.*?)\[\/li\]", '<li>{find1}</li>', 1),
        (r"\[table\](.*?)\[\/table\]", '<table>{find1}</table>', 1),
        (r"\[tr\](.*?)\[\/tr\]", '<tr>{find1}</tr>', 1),
        (r"\[td\](.*?)\[\/td\]", '<td>{find1}</td>', 1),
        (r"\[code\](.*?)\[\/code\]", '<pre>{find1}</pre>', 1),
        (r"\[quote\](.*?)\[\/quote\]", '<blockquote>{find1}</blockquote>', 1),
        (r"\[hr\]", '<hr />', 0),
        (r":angel:", '<img src="https://www.sceditor.com/emoticons/angel.png" />', 0),
    ]

    for pattern in patterns:
        matches = re.finditer(pattern[0], text, re.DOTALL)

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

        if pattern[2] == 0:
            for match in matches:
                match_start = match.start(0)
                match_end = match.end(0)

                replacement = pattern[1]
                text = text[:match_start] + replacement + text[match_end:]

    return text


