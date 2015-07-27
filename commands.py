# coding=utf-8
from re import findall

__author__ = 'm_messiah'
from base64 import b64decode, b64encode
from requests import Session
from re import findall

def start(_, message):
    return {'chat_id': message['chat']['id'], 'text': "I am awake!"}


def about(_, message):
    return {'chat_id': message['chat']['id'],
            'text': "Hey, %s!\n"
                    "My author is @m_messiah."
                    "You can find this nickname at:"
                    "\t+ Telegram"
                    "\t+ Twitter"
                    "\t+ Instagram"
                    "\t+ VK"
                    "\t+ GitHub (m-messiah)"
                    % message['from']["first_name"]
            }


def base64_code(arguments, message):
    response = {'chat_id': message['chat']['id']}
    try:
        response['text'] = b64decode(arguments.encode("utf8"))
        assert len(response['text'])
    except:
        response['text'] = b64encode(arguments.encode("utf8"))
    finally:
        return response


def help_message(_, message):
    response = {'chat_id': message['chat']['id']}
    result = ["Hey, %s!" % message["from"].get("first_name"),
              "\rI can accept these commands:"]
    for command in CMD:
        result.append(command)
    response['text'] = "\n\t".join(result)
    return response


def parse_code(_, message, browser, url):
    response = {'chat_id': message['chat']['id'],
                'reply_to_message_id': message['message_id']}
    codes = findall(ur"[0-9]*[dDдД][0-9]*[rRрР][0-9]*", message["text"])
    result = []
    if len(codes):
        for code in codes:
            code = code.upper().translate({ord(u'Д'): u'D', ord(u'Р'): u'R'})
            result.append("%s - %s" % (code, send(browser, url, code)))
        response['text'] = u"\n".join(sorted(result)).encode("utf8")
        return response
    else:
        return None


def send(browser, url, code):
    answer = browser.post(url,
                          data={'action': "entcod",
                                'cod': code})
    message = findall(r"<div class=sysmsg style='text-align:center'>(.+?)<",
                      answer.text)
    return u"/n".join(message)


CMD = {
    "/whoisyourdaddy": about,
    "/base64": base64_code,
    "/help": help_message,
    "/start": start,
    "#code": parse_code,
}
