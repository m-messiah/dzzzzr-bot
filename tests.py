# coding=utf-8
from unittest import TestCase
import sys
import os.path
sys.path.insert(1, '/usr/local/google_appengine')
sys.path.insert(1, '/usr/local/google_appengine/lib/yaml/lib')
sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'lib'))
import webapp2
from webapp2_extras import json
from paste import httpserver
from multiprocessing import Process
from main import app, DozoR, SESSIONS
from test_engine import app as dr_engine


class TestApp(TestCase):
    def test_show_error(self):
        request = webapp2.Request.blank("/")
        response = request.get_response(app)
        self.assertEqual(response.status_int, 200)
        self.assertIn("application/json", response.headers['Content-Type'])
        self.assertDictEqual(
                json.decode(response.body),
                {"name": "I am DR bot (https://telegram.me/DzzzzR_bot)",
                 "result": "Info"})

    def test_get(self):
        request = webapp2.Request.blank("/")
        response = request.get_response(app)
        self.assertEqual(response.status_int, 200)
        self.assertIn("application/json", response.headers['Content-Type'])
        self.assertDictEqual(
                json.decode(response.body),
                {"name": "I am DR bot (https://telegram.me/DzzzzR_bot)",
                 "result": "Info"})

    def test_bad_post(self):
        request = webapp2.Request.blank("/")
        request.method = "POST"
        response = request.get_response(app)
        self.assertEqual(response.status_int, 200)
        self.assertIn("application/json", response.headers['Content-Type'])
        self.assertDictEqual(
                json.decode(response.body),
                {"name": "I am DR bot (https://telegram.me/DzzzzR_bot)",
                 "result": "Info"})

    def test_json_empty_post(self):
        request = webapp2.Request.blank("/")
        request.method = "POST"
        request.headers["Content-Type"] = "application/json"
        response = request.get_response(app)
        self.assertEqual(response.status_int, 200)
        self.assertIn("application/json", response.headers['Content-Type'])
        self.assertDictEqual(
                json.decode(response.body),
                {"name": "I am DR bot (https://telegram.me/DzzzzR_bot)",
                 "result": "Info"})

    def test_json_start_post(self):
        request = webapp2.Request.blank("/")
        request.method = "POST"
        request.headers["Content-Type"] = "application/json"
        request.body = json.encode({
            'update': 1,
            'message': {
                u'date': 1450696897,
                u'text': u'/start',
                u'from': {
                    u'username': u'm_messiah',
                    u'first_name': u'Maxim',
                    u'last_name': u'Muzafarov',
                    u'id': 3798371
                },
                u'message_id': 1,
                u'chat': {
                    u'type': u'group',
                    u'id': -11812986,
                    u'title': u'КС'
                }
            }
        })
        response = request.get_response(app)
        self.assertEqual(response.status_int, 200)
        self.assertIn("application/json", response.headers['Content-Type'])
        self.assertDictEqual(
                json.decode(response.body),
                {
                    'method': 'sendMessage',
                    'text': u"Внимательно слушаю!",
                    'chat_id': -11812986,
                    'disable_web_page_preview': True,
                    'reply_to_message_id': 1,
                }
        )

    def test_json_text_post(self):
        request = webapp2.Request.blank("/")
        request.method = "POST"
        request.headers["Content-Type"] = "application/json"
        request.body = json.encode({
            'update': 1,
            'message': {
                u'date': 1450696897,
                u'text': u'как дела?',
                u'from': {
                    u'username': u'm_messiah',
                    u'first_name': u'Maxim',
                    u'last_name': u'Muzafarov',
                    u'id': 3798371
                },
                u'message_id': 1,
                u'chat': {
                    u'type': u'group',
                    u'id': -11812986,
                    u'title': u'КС'
                }
            }
        })
        response = request.get_response(app)
        self.assertEqual(response.status_int, 200)
        self.assertIn("application/json", response.headers['Content-Type'])
        self.assertDictEqual(json.decode(response.body), {})

    def test_sessions(self):
        request = webapp2.Request.blank("/")
        request.method = "POST"
        request.headers["Content-Type"] = "application/json"
        request.body = json.encode({
            'update': 1,
            'message': {
                u'date': 1450696897,
                u'text': u'Привет',
                u'from': {
                    u'username': u'm_messiah',
                    u'first_name': u'Maxim',
                    u'last_name': u'Muzafarov',
                    u'id': 3798371
                },
                u'message_id': 1,
                u'chat': {
                    u'type': u'group',
                    u'id': -11812986,
                    u'title': u'КС'
                }
            }
        })
        _ = request.get_response(app)
        self.assertIn(-11812986, SESSIONS)


class TestBot(TestCase):
    def setUp(self):
        self.engine = Process(target=httpserver.serve, args=(dr_engine, ),
                              kwargs={'host': "127.0.0.1", 'port': "5000"})
        self.engine.start()

    def tearDown(self):
        self.engine.terminate()

    def send_message(self, text):
        request = webapp2.Request.blank("/")
        request.method = "POST"
        request.headers["Content-Type"] = "application/json"
        request.body = json.encode({
            'update': 1,
            'message': {
                u'date': 1450696897,
                u'text': u'%s' % text,
                u'from': {
                    u'username': u'm_messiah',
                    u'first_name': u'Maxim',
                    u'last_name': u'Muzafarov',
                    u'id': 3798371
                },
                u'message_id': 1,
                u'chat': {
                    u'type': u'user',
                    u'id': 3798371,
                    u'username': u'm_messiah',
                    u'first_name': u'Maxim',
                    u'last_name': u'Muzafarov',
                }
            }
        })
        response = request.get_response(app)
        self.assertEqual(response.status_int, 200)
        self.assertIn("application/json", response.headers['Content-Type'])
        response = json.decode(response.body)
        self.assertIn('text', response)
        return response['text']

    def send_gps(self, gps):
        request = webapp2.Request.blank("/")
        request.method = "POST"
        request.headers["Content-Type"] = "application/json"
        request.body = json.encode({
            'update': 1,
            'message': {
                u'date': 1450696897,
                u'text': u'%s' % gps,
                u'from': {
                    u'username': u'm_messiah',
                    u'first_name': u'Maxim',
                    u'last_name': u'Muzafarov',
                    u'id': 3798371
                },
                u'message_id': 1,
                u'chat': {
                    u'type': u'user',
                    u'id': 3798371,
                    u'username': u'm_messiah',
                    u'first_name': u'Maxim',
                    u'last_name': u'Muzafarov',
                }
            }
        })
        response = request.get_response(app)
        self.assertEqual(response.status_int, 200)
        self.assertIn("application/json", response.headers['Content-Type'])
        response = json.decode(response.body)
        self.assertEqual('sendLocation', response['method'])
        return response['latitude'], response['longitude']

    def test_set_dzzzr(self):
        response = self.send_message(
            "/set_dzzzr http://localhost:5000/ spb_Captain 123456 bot"
        )

        self.assertIn("/set_dzzzr", response,
                      "Accept not enough arguments")

        response = self.send_message(
            "/set_dzzzr http://localhost:5000/ spb_Captain 123456 "
            "bot botpassword 1D"
        )
        self.assertNotIn("/set_dzzzr", response,
                         "Arguments with prefix bad splitted")
        self.assertNotEqual("", SESSIONS[3798371].credentials)
        self.assertEqual("1D", SESSIONS[3798371].prefix)

    def test_not_found(self):
        self.assertEqual(u"Команда не найдена. Используйте /help",
                         self.send_message("/abracadabra"))

    def test_start(self):
        self.assertEqual(u"Внимательно слушаю!", self.send_message("/start"))

    def test_show_sess(self):
        self.assertIn(u"Сейчас используют", self.send_message("/show_sess"))

    def test_about(self):
        self.assertEqual(
                u"Привет!\n"
                u"Мой автор @m_messiah\n"
                u"Сайт: https://m-messiah.ru\n"
                u"\nА еще принимаются пожертвования:\n"
                u"https://paypal.me/muzafarov\n"
                u"http://yasobe.ru/na/m_messiah",
                self.send_message("/about")
        )

    def test_base64(self):
        self.assertEqual(u"0J/RgNC40LLQtdGC",
                         self.send_message(u"/base64 Привет"))
        self.assertEqual(u"Привет",
                         self.send_message(u"/base64 0J/RgNC40LLQtdGC"))

    def test_pos(self):
        self.assertIn(u"абвя",
                      self.send_message(u"/pos 1 2 3 33"))
        self.assertIn(u"abcg",
                      self.send_message(u"/pos 1 2 3 33"))

    def test_gps(self):
        eta = (56.847222, 60.675)
        dd = u"56.847222, 60.675"
        dmr = u"56 50.8333, 60 40.5"
        dmsr = u"56 50 50, 60 40 30"
        self.assertEqual(eta, self.send_gps(dd))
        self.assertEqual(eta, self.send_gps(dmr))
        self.assertEqual(eta, self.send_gps(dmsr))

    def test_code(self):
        self.assertIn(u"войти в движок", self.send_message(u"1d23r4"))
        self.send_message(
            "/set_dzzzr http://127.0.0.1:5000/ spb_Captain 123456 bot password"
        )
        self.assertIn(u"Код принят", self.send_message(u"1d23r4"))
        self.assertIn(u"Код не принят", self.send_message(u"2d23r4"))

    def test_remain(self):
        response = self.send_message(u"/remain")
        self.assertNotIn(u"/help", response)
        self.assertIn(u"найдено кодов", response)

    def test_remain_codes(self):
        response = self.send_message(u"/codes")
        self.assertNotIn(u"/help", response)
        self.assertIn(u"Сектор 1 (осталось 7): 12 (1), 16 (1), 17 (1+), "
                      u"18 (1), 22 (1), 23 (1+), 24 (1)", response)

    def test_time(self):
        response = self.send_message(u"/time")
        self.assertNotIn(u"/help", response)
        self.assertIn("00:29:23", response)


class TestCodeParsing(TestCase):
    def test_code(self):
        d = DozoR({'id': 1, 'username': 'm_messiah'})
        d.enabled = True
        for prefix in [u"", u"27D"]:
            d.prefix = prefix

            for code in [u"1D23R4",
                         u"1д23р4",
                         u"D23R4",
                         u"1D234R",
                         u"1D2D34R",
                         u"1D23R4R",
                         u"D234R",
                         u"23R4",
                         u"23R",
                         u"123Р6",
                         u"123Р"]:
                result = d.code({'text': code})
                self.assertIn(u"войти в движок", result)
