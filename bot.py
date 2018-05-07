# coding=utf-8
import logging
from base64 import b64decode, b64encode

import main
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
        self.name = "@DzzzzR_bot"

    def show_sessions(self, _):
        sessions = ["%s (%s)" % (v.title, k) for k, v in main.SESSIONS.items()]
        return u"Сейчас используют:\n" + u"\n".join(sessions)

    def not_found(self, _):
        return (u"Команда не найдена. Используйте /help \n"
                u"Или дайте денег автору, и он сделает такую команду")

    def version(self, _):
        return u"Версия: 3.2.3"

    def help(self, _):
        return (
            u"Я могу принимать следующие команды:\n"
            u"/help - эта справка\n"
            u"/about - информация об авторе\n"
            u"/start - команда заглушка, эмулирующая начало общения\n"
            u"/stop - команда удаляющая сессию общения с ботом\n"
            u"\n"
            u"/base64 <text> - Base64 кодирование/раскодирование\n"
            u"/gps <lat, long> - Карта по координатам\n"
            u"/pos <num1 num2 numN> - Слово из порядковых букв в алфавите\n"
            u"\nDozoR\n" + self.dozor.help()
        )

    def start(self, _):
        return u"Внимательно слушаю!"

    def stop(self, _):
        try:
            self.dozor.enabled = False
            del main.CREDENTIALS[self.dozor.credentials]
            del main.SESSIONS[self.chat_id]
        except Exception:
            pass
        return u"До новых встреч!"

    def about(self, _):
        return (u"Привет!\n"
                u"Мой автор @m_messiah\n"
                u"Мой код: https://github.com/m-messiah/dzzzzr-bot\n"
                u"\nА еще принимаются пожертвования:\n"
                u"https://paypal.me/muzafarov\n"
                u"http://yasobe.ru/na/m_messiah")

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
        if command == "/set_dzzzr":
            try:
                return self.dozor.set_dzzzr(arguments)
            except Exception as e:
                return "Incorrect format (%s)" % e
        else:
            try:
                return getattr(self, command[1:], getattr(self.dozor, command[1:], self.not_found))(arguments)
            except UnicodeEncodeError as e:
                return self.not_found(None)
            except Exception as e:
                logging.error(e)
                return None

    def handle_text(self, message):
        text = message['text']
        if text.count(",") == 1:
            result = self.gps(text)
            if result:
                return result

        result = self.dozor.handle_text(text)
        if result:
            return result

        if u"привет" in text.lower() and u"бот" in text.lower():
            return u"Привет!"
