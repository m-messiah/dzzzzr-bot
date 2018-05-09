# coding=utf-8
from zlib import MAX_WBITS, decompress

from bs4 import BeautifulSoup

import main
import messages


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
