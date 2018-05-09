# coding=utf-8
import logging
from base64 import b64decode, b64encode

import main
import messages
from dozor import DozoR

__author__ = 'm_messiah'


RUS = (1072, 1073, 1074, 1075, 1076, 1077, 1105, 1078, 1079, 1080, 1081, 1082,
       1083, 1084, 1085, 1086, 1087, 1088, 1089, 1090, 1091, 1092, 1093, 1094,
       1095, 1096, 1097, 1098, 1099, 1100, 1101, 1102, 1103)

ENG = (97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
       112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122)


class Bot(object):
    def __init__(self, sender):
        self.chat_id = sender['id']
        self.title = sender.get('title', sender.get('username', ''))
        self.dozor = DozoR(self.chat_id)
        self.name = messages.BOT_NAME

    def show_sessions(self, _):
        sessions = ["%s (%s)" % (v.title, k) for k, v in main.SESSIONS.items()]
        return messages.BOT_SESSIONS_TEMPL % u"\n".join(sessions)

    def not_found(self, _):
        return messages.BOT_COMMAND_NOT_FOUND

    def version(self, _):
        return messages.BOT_VERSION

    def help(self, _):
        return messages.BOT_HELP

    def start(self, _):
        return messages.BOT_START

    def stop(self, _):
        try:
            self.dozor.enabled = False
            del main.CREDENTIALS[self.dozor.credentials]
            del main.SESSIONS[self.chat_id]
        except Exception:
            pass
        return messages.BOT_STOP

    def about(self, _):
        return messages.BOT_ABOUT

    def base64(self, arguments):
        response = None
        try:
            response = b64decode(arguments.encode("utf8"))
            assert len(response)
            response.decode("utf8").encode("utf8")
        except Exception:
            response = b64encode(arguments.encode("utf8"))
        finally:
            return response

    def _construct_from_pos(self, positions, lang):
        return u"".join(map(lambda i: unichr(lang[(i - 1) % len(lang)]), positions))

    def pos(self, text):
        try:
            positions = list(map(int, text.split()))
        except ValueError:
            try:
                positions = list(map(int, text.split(",")))
            except Exception:
                return None

        return u"\n".join(self._construct_from_pos(positions, lang) for lang in (RUS, ENG))

    def _gps_dd(self, coords):
        return tuple(map(lambda x: round(float(x[0]), 6), coords))

    def _gps_dmr(self, coords):
        result = []
        for lat in coords:
            d, m = map(float, lat[:2])
            result.append(round(d + m / 60 * (-1 if d < 0 else 1), 6))
        return tuple(result)

    def _gps_dmsr(self, coords):
        result = []
        for lat in coords:
            d, m, s = map(float, lat[:3])
            result.append(round(d + (m * 60 + s) / 3600 * (-1 if d < 0 else 1), 6))
        return tuple(result)

    def _split_gps(self, text):
        raw_coords = text.split(",")
        coords = [0, [[], []]]
        for i, lat in enumerate(raw_coords):
            lat = lat.split()
            count = len(lat)
            if count > coords[0]:
                coords[0] = count
            coords[1][i] = lat
        return coords

    def gps(self, text):
        try:
            coords = self._split_gps(text)
            if coords[0] == 1:
                return self._gps_dd(coords[1])
            if coords[0] == 2:
                return self._gps_dmr(coords[1])
            if coords[0] == 3:
                return self._gps_dmsr(coords[1])
        except Exception:
            pass

    def handle_command(self, text):
        command, _, arguments = text.partition(" ")
        if self.name in command:
            command = command[:command.find(self.name)]
        if "@" in command:
            return None
        try:
            return getattr(self, command[1:], getattr(self.dozor, command[1:], self.not_found))(arguments)
        except UnicodeEncodeError as e:  # pragma: no cover
            return self.not_found(None)
        except Exception as e:  # pragma: no cover
            logging.error(e)

    def handle_text(self, text):
        if text.count(",") == 1:
            result = self.gps(text)
            if result:
                return result

        result = self.dozor.handle_text(text)
        if result:
            return result

        if u"привет" in text.lower() and u"бот" in text.lower():
            return messages.BOT_HELLO
