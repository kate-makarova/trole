import re

def translate_bb(bb_code):
    result = bb_code.replace('\n', '</p><p>')
    result = '<p>'+result+'</p>'
    result = result.replace('[b]', '<b>').replace('[/b]', '</b>')
    result = result.replace('[i]', '<i>').replace('[/i]', '</i>')
    result = result.replace('[u]', '<u>').replace('[/u]', '</u>')
    result = result.replace('[s]', '<s>').replace('[/s]', '</s>')
    result = result.replace('[code]', '<code>').replace('[/code]', '</code>')
    result = result.replace('[quote]', '<blockquote>').replace('[/quote]', '</blockquote>')
    result = re.sub(r'\[url=([^]]*)\]([^[]*)\[\/url\]', r'<a href="\1">\2</a>', result)
  #  result = result.replace('[img]', '<img src="').replace('[/img]', '">')
    # result = result.replace('[color=', '<span style="color:').replace('[/color]', '</span>')
    # result = result.replace('[size=', '<span style="font-size:').replace('[/size]', '</span>')
    return result