# coding=utf-8
from random import choice
from re import compile as re_compile
from re import split as re_split
from zlib import MAX_WBITS, decompress

from bs4 import BeautifulSoup
from requests import Session

import main
import messages
from useragents import USERAGENTS

__author__ = 'm_messiah'

CODE_RANKS = re_compile(u"Коды сложности")
TIME_ON = re_compile(u"Время на уровне:")
LITE_MESSAGE = re_compile(ur'<!--errorText--><p><strong>(.*?)</strong></p><!--errorTextEnd-->')
LITE_TIME_ON = re_compile(ur'<!--timeOnLevelBegin (\d*?) timeOnLevelEnd-->')
LITE_TIME_TO = re_compile(ur'<!--timeToFinishBegin (\d*?) timeToFinishEnd-->')


def decode_page(page):
    page_content = page.raw.read()
    try:
        content = decompress(page_content, 16 + MAX_WBITS)
    except Exception:
        content = page_content
    return BeautifulSoup(content, 'html.parser', from_encoding="windows-1251")


class DozoR(object):
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.url = ""
        self.prefix = ""
        self.credentials = ""
        self.enabled = False
        self.classic = True
        self.browser = Session()
        self.dr_code = re_compile(ur"^[0-9dDдДrRlLzZрРлЛ]+$")

    def help(self):
        return messages.DOZOR_HELP

    def pause(self, _):
        self.enabled = False
        return messages.DOZOR_PAUSE

    def resume(self, _):
        self.enabled = True
        return messages.DOZOR_RESUME

    def get_dzzzr(self, code=None):
        try:
            if code:
                answer = self.browser.post(
                    self.url,
                    data={
                        'action': "entcod",
                        'cod': code.encode("cp1251")
                    },
                    stream=True
                )
            else:
                answer = self.browser.get(self.url, stream=True)
            if not answer:
                raise Exception()
            return decode_page(answer)
        except Exception:
            raise Exception(messages.DOZOR_NO_ANSWER)

    def _handle_set_dzzzr_arguments(self, arguments):
        arguments = arguments.split()
        if len(arguments) < 5:
            raise ValueError

        if len(arguments) > 5:
            if "[" not in arguments[5]:
                self.prefix = arguments[5].upper()
            else:
                self.dr_code = re_compile(ur"^%s$" % arguments[5])
        else:
            self.prefix = ""
        if len(arguments) > 6:
            self.dr_code = re_compile(ur"^%s$" % arguments[6])
        self.url = arguments[0]
        return arguments[1:5]

    def _get_dup_session(self, captain, login):
        merged = "|".join((self.url, captain, login))
        if merged in main.CREDENTIALS and self.chat_id != main.CREDENTIALS[merged]:
            return messages.DOZOR_DUPLICATE_TEMPL % main.SESSIONS[main.CREDENTIALS[merged]].title

    def _send_dzzzr_auth(self, captain, pin, login, password):
        self.browser.headers.update({
            'referer': self.url,
            'User-Agent': "Mozilla/5.0 " + choice(USERAGENTS)
        })
        self.browser.auth = (captain, pin)
        try:
            login_page = self.browser.post(
                self.url,
                data={
                    'login': login,
                    'password': password,
                    'action': "auth",
                    'notags': ''
                },
                stream=True
            )
        except Exception as e:
            return False, messages.DOZOR_INCORRECT_TEMPL % e

        if login_page.status_code != 200:
            return False, messages.DOZOR_AUTH_FAILED

        return True, login_page

    def _dzzzr_auth(self, captain, pin, login, password):
        is_authenticated, login_page = self._send_dzzzr_auth(captain, pin, login, password)
        if not is_authenticated:
            return False, login_page
        try:
            answer = decode_page(login_page)
            message = answer.find(class_="sysmsg")
            if not (message and message.get_text()):
                return False, messages.DOZOR_AUTH_FAILED
            message = message.get_text()
            return messages.DOZOR_AUTH_PATTERN in message, message
        except Exception as e:
            return False, messages.DOZOR_BAD_PAGE_TEMPL % e

    def set_dzzzr(self, arguments):
        try:
            captain, pin, login, password = self._handle_set_dzzzr_arguments(arguments)
        except Exception:
            return messages.DOZOR_SET_DZZZR_HELP

        dup_message = self._get_dup_session(captain, login)
        if dup_message:
            return dup_message

        is_authenticated, message = self._dzzzr_auth(captain, pin, login, password)
        if not is_authenticated:
            return message

        self.enabled = True
        self.classic = True
        self.credentials = "|".join((self.url, captain, login))
        main.CREDENTIALS[self.credentials] = self.chat_id
        return messages.DOZOR_WELCOME_TEMPL % login

    def set_lite(self, arguments):
        try:
            arguments = arguments.split()
            if len(arguments) > 1:
                self.url, pin = arguments[:2]
            else:
                raise ValueError
        except ValueError:
            return messages.DOZOR_SET_LITE_HELP
        else:
            self.browser.headers.update({
                'referer': self.url,
                'User-Agent': "Mozilla/5.0 " + choice(USERAGENTS)
            })
            login_page = self.browser.get(self.url, params={'pin': pin}, stream=True)
            if login_page.status_code != 200:
                return messages.DOZOR_AUTH_FAILED
            else:
                answer = decode_page(login_page)
                message = LITE_MESSAGE.search(str(answer))
                if not message:
                    return messages.DOZOR_AUTH_FAILED

                message = message.group(1)
                self.enabled = True
                self.classic = False
                self.credentials = "|".join((self.url, pin))
                main.CREDENTIALS[self.credentials] = self.chat_id
                return message

    def time(self, _):
        answer, message = self._get_dzzzr_answer()
        if message:
            return message

        if self.classic:
            message = answer.find("p", string=TIME_ON)
            if message and message.get_text():
                return u" ".join(message.get_text().split()[:4])
        else:
            def to_minutes(sec):
                return u"%s:%s" % (sec / 60, sec % 60)

            on_level = LITE_TIME_ON.search(str(answer))
            to_finish = LITE_TIME_TO.search(str(answer))
            if on_level and to_finish:
                return messages.DOZOR_TIME_ON_TEMPL % (
                    to_minutes(int(on_level.group(1))),
                    to_minutes(int(to_finish.group(1))),
                )

        return messages.DOZOR_NO_ANSWER

    def _get_dzzzr_answer(self):
        try:
            if self.url == "":
                raise Exception(messages.DOZOR_NEED_AUTH)
            return self.get_dzzzr(), None
        except Exception as e:
            return None, unicode(e.message)

    def _parse_sector(self, sector):
        if not sector:
            return
        try:
            sector_name, _, codes = sector.partition(u":")
            _, __, codes = codes.partition(u":")
            if not codes:
                return
            codes = codes.strip().split(u", ")
            codes = [c for c in enumerate(codes, start=1) if u"span" not in c[1]]
            return (
                messages.DOZOR_SECTOR_CODES_TEMPL % (
                    sector_name,
                    len(codes),
                    u", ".join(messages.DOZOR_CODE_RANK_TEMPL % t for t in codes)
                ))
        except Exception:
            pass

    def codes(self, _):
        answer, message = self._get_dzzzr_answer()
        if message:
            return message
        try:
            message = answer.find("strong", string=CODE_RANKS).parent
        except Exception:
            return messages.DOZOR_NO_CODE_RANKS
        if not message:
            return messages.DOZOR_NO_ANSWER

        message = unicode(message).split(u"Коды сложности")[1]
        sectors = re_split("<br/?>", message)[:-1]
        result = filter(None, map(self._parse_sector, sectors))
        return u"\n".join(result)

    def _classic_result(self, code, answer):
        message = answer.find(class_="sysmsg")
        if message and message.get_text():
            message_answer = message.get_text()
        else:
            message_answer = messages.DOZOR_NO_ANSWER
        return code + " - " + message_answer

    def _lite_result(self, code, answer):
        message = LITE_MESSAGE.search(str(answer))
        if message:
            message_answer = message.group(1).decode("utf8")
        else:
            message_answer = messages.DOZOR_NO_ANSWER
        return code + u" - " + message_answer

    def _send_code(self, code):
        if self.url == "":
            return code + u" - " + messages.DOZOR_NEED_AUTH
        try:
            answer = self.get_dzzzr(code=code)
        except Exception as e:
            return e.message
        try:
            if self.classic:
                return self._classic_result(code, answer)
            else:
                return self._lite_result(code, answer)
        except Exception:
            return messages.DOZOR_NO_ANSWER

    def _handle_code(self, code):
        if not self.dr_code.match(code):
            return
        code = code.upper()
        if self.dr_code.search(u"D"):
            code = code.translate({ord(u'Д'): u'D',
                                   ord(u'Р'): u'R',
                                   ord(u'Л'): u'L'})
        if self.prefix and self.prefix not in code:
            code = self.prefix + code
        return self._send_code(code)

    def handle_text(self, text):
        if not self.enabled:
            return

        codes = text.split()
        if len(codes) < 1:
            return None

        result = filter(None, map(self._handle_code, codes))
        if result:
            return u"\n".join(result)
