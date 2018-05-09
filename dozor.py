# coding=utf-8
from random import choice
from re import compile as re_compile
from re import split as re_split

from requests import Session

import main
import messages
import utils
from useragents import USERAGENTS

__author__ = 'm_messiah'

CODE_RANKS = re_compile(u"Коды сложности")
TIME_ON = re_compile(u"Время на уровне:")
LITE_MESSAGE = re_compile(ur'<!--errorText--><p><strong>(.*?)</strong></p><!--errorTextEnd-->')
LITE_TIME_ON = re_compile(ur'<!--timeOnLevelBegin (\d*?) timeOnLevelEnd-->')
LITE_TIME_TO = re_compile(ur'<!--timeToFinishBegin (\d*?) timeToFinishEnd-->')


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
            if not answer:  # no cover until mocked tests
                raise Exception()
            return utils.decode_page(answer)
        except Exception:
            raise Exception(messages.DOZOR_NO_ANSWER)

    def set_dr_code(self, pattern):
        self.dr_code = re_compile(ur"^%s$" % pattern)

    def _handle_set_dzzzr_arguments(self, arguments):
        arguments = arguments.split()
        if len(arguments) < 5:
            raise ValueError

        self.url = arguments[0]
        self.prefix = ""
        if len(arguments) > 5:
            if "[" in arguments[5]:
                self.set_dr_code(arguments[5])
            else:
                self.prefix = arguments[5].upper()

        if len(arguments) > 6:
            self.set_dr_code(arguments[6])
        return dict(zip(('captain', 'pin', 'login', 'password'), arguments[1:5]))

    def _update_headers(self):
        self.browser.headers.update({
            'referer': self.url,
            'User-Agent': "Mozilla/5.0 " + choice(USERAGENTS)
        })

    def _send_dzzzr_auth(self, user_credentials):
        self._update_headers()
        self.browser.auth = (user_credentials['captain'], user_credentials['pin'])
        try:
            login_page = self.browser.post(
                self.url,
                data={
                    'login': user_credentials['login'],
                    'password': user_credentials['password'],
                    'action': "auth",
                    'notags': ''
                },
                stream=True
            )
        except Exception as e:
            return False, messages.DOZOR_INCORRECT_TEMPL % e

        if login_page.status_code != 200:  # no cover until mocked tests
            return False, messages.DOZOR_AUTH_FAILED

        return True, login_page

    def _dzzzr_auth(self, user_credentials):
        is_authenticated, login_page = self._send_dzzzr_auth(user_credentials)
        if not is_authenticated:
            return False, login_page
        try:
            answer = utils.decode_page(login_page)
            message = answer.find(class_="sysmsg")
            if not (message and message.get_text()):  # no cover until mocked tests
                return False, messages.DOZOR_AUTH_FAILED
            message = message.get_text()
            return messages.DOZOR_AUTH_PATTERN in message, message
        except Exception as e:  # no cover until mocked tests
            return False, messages.DOZOR_BAD_PAGE_TEMPL % e

    def set_dzzzr(self, arguments):
        try:
            user_credentials = self._handle_set_dzzzr_arguments(arguments)
        except Exception:
            return messages.DOZOR_SET_DZZZR_HELP

        merged_credentials = "|".join((self.url, user_credentials['captain'], user_credentials['login']))
        dup_message = utils.get_dup_session(self.chat_id, merged_credentials)
        if dup_message:
            return dup_message

        is_authenticated, message = self._dzzzr_auth(user_credentials)
        if not is_authenticated:
            return message

        self.enabled = True
        self.classic = True
        self.credentials = merged_credentials
        main.CREDENTIALS[self.credentials] = self.chat_id
        return messages.DOZOR_WELCOME_TEMPL % user_credentials['login']

    def set_lite(self, arguments):
        arguments = arguments.split()
        if len(arguments) < 2:
            return messages.DOZOR_SET_LITE_HELP
        self.url, pin = arguments[:2]
        self._update_headers()
        login_page = self.browser.get(self.url, params={'pin': pin}, stream=True)
        if login_page.status_code != 200:  # no cover until mocked tests
            return messages.DOZOR_AUTH_FAILED

        answer = utils.decode_page(login_page)
        message = LITE_MESSAGE.search(str(answer))
        if not message:  # no cover until mocked tests
            return messages.DOZOR_AUTH_FAILED

        self.enabled = True
        self.classic = False
        self.credentials = "|".join((self.url, pin))
        main.CREDENTIALS[self.credentials] = self.chat_id
        return message.group(1)

    def _parse_classic_time(self, answer):
        message = answer.find("p", string=TIME_ON)
        if message and message.get_text():
            return u" ".join(message.get_text().split()[:4])

    def _parse_lite_time(self, answer):
        on_level = LITE_TIME_ON.search(str(answer))
        to_finish = LITE_TIME_TO.search(str(answer))
        if on_level and to_finish:
            return messages.DOZOR_TIME_ON_TEMPL % (
                utils.to_minutes(int(on_level.group(1))),
                utils.to_minutes(int(to_finish.group(1))),
            )

    def time(self, _):
        answer, message = self._get_dzzzr_answer()
        if message:
            return message

        parser = self._parse_classic_time if self.classic else self._parse_lite_time
        return parser(answer) or messages.DOZOR_NO_ANSWER

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
        except Exception:  # no cover until mocked tests
            pass

    def codes(self, _):
        answer, message = self._get_dzzzr_answer()
        if message:
            return message
        try:
            message = answer.find("strong", string=CODE_RANKS).parent
        except Exception:  # no cover until mocked tests
            return messages.DOZOR_NO_CODE_RANKS
        if not message:  # no cover until mocked tests
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
            message_answer = messages.DOZOR_NO_ANSWER  # no cover until mocked tests
        return code + " - " + message_answer

    def _lite_result(self, code, answer):
        message = LITE_MESSAGE.search(str(answer))
        if message:
            message_answer = message.group(1).decode("utf8")
        else:
            message_answer = messages.DOZOR_NO_ANSWER  # no cover until mocked tests
        return code + u" - " + message_answer

    def _send_code(self, code):
        if self.url == "":
            return code + u" - " + messages.DOZOR_NEED_AUTH
        try:
            answer = self.get_dzzzr(code=code)
        except Exception as e:  # no cover until mocked tests
            return e.message

        result_handler = self._classic_result if self.classic else self._lite_result
        try:
            return result_handler(code, answer)
        except Exception:  # no cover until mocked tests
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
