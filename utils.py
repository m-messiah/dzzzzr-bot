# coding=utf-8
from re import compile as re_compile
from zlib import MAX_WBITS, decompress

from bs4 import BeautifulSoup

import main
import messages

TIME_ON = re_compile(u"Время на уровне:")
LITE_MESSAGE = re_compile(ur'<!--errorText--><p><strong>(.*?)</strong></p><!--errorTextEnd-->')
LITE_TIME_ON = re_compile(ur'<!--timeOnLevelBegin (\d*?) timeOnLevelEnd-->')
LITE_TIME_TO = re_compile(ur'<!--timeToFinishBegin (\d*?) timeToFinishEnd-->')


def to_minutes(sec):
    return u"%s:%s" % (sec / 60, sec % 60)


def decode_page(page):
    page_content = page.raw.read()
    try:
        content = decompress(page_content, 16 + MAX_WBITS)
    except Exception:
        content = page_content
    return BeautifulSoup(content, 'html.parser', from_encoding="windows-1251")


def get_dup_session(chat_id, merged_credentials):
    if merged_credentials in main.CREDENTIALS and chat_id != main.CREDENTIALS[merged_credentials]:
        return messages.DOZOR_DUPLICATE_TEMPL % main.SESSIONS[main.CREDENTIALS[merged_credentials]].title


def parse_classic_time(answer):
    message = answer.find("p", string=TIME_ON)
    if message and message.get_text():
        return u" ".join(message.get_text().split()[:4])


def parse_lite_time(answer):
    on_level = LITE_TIME_ON.search(str(answer))
    to_finish = LITE_TIME_TO.search(str(answer))
    if on_level and to_finish:
        return messages.DOZOR_TIME_ON_TEMPL % (
            to_minutes(int(on_level.group(1))),
            to_minutes(int(to_finish.group(1))),
        )


def parse_time(answer, is_classic=True):
    if is_classic:
        return parse_classic_time(answer)
    return parse_lite_time(answer)


def parse_classic_result(code, answer):
    message = answer.find(class_="sysmsg")
    if message and message.get_text():
        message_answer = message.get_text()
    else:
        message_answer = messages.DOZOR_NO_ANSWER  # no cover until mocked tests
    return code + " - " + message_answer


def parse_lite_result(code, answer):
    message = LITE_MESSAGE.search(str(answer))
    if message:
        message_answer = message.group(1).decode("utf8")
    else:
        message_answer = messages.DOZOR_NO_ANSWER  # no cover until mocked tests
    return code + u" - " + message_answer


def parse_code_result(code, answer, is_classic=True):
    if is_classic:
        return parse_classic_result(code, answer)
    return parse_lite_result(code, answer)
