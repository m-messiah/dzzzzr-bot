# coding=utf-8
from unittest import TestCase
import sys
import os.path
from main import app, DozoR, SESSIONS
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
# mac os
google_cloud_sdk_path = '/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/platform/google_appengine'
sys.path.insert(0, google_cloud_sdk_path + '/lib/yaml/lib')
sys.path.insert(0, google_cloud_sdk_path)
# travis
sys.path.insert(1, 'google_appengine')
sys.path.insert(1, 'google_appengine/lib/yaml/lib')
import webapp2  # noqa E402
from webapp2_extras import json  # noqa E402


class TestApp(TestCase):
    def test_show_error(self):
        request = webapp2.Request.blank("/")
        response = request.get_response(app)
        self.assertEqual(response.status_int, 200)
        self.assertIn("application/json", response.headers['Content-Type'])
        self.assertDictEqual(
            json.decode(response.body),
            {"name": "I am DR bot (https://telegram.me/DzzzzR_bot)", "result": "Info"}
        )

    def test_get(self):
        request = webapp2.Request.blank("/")
        response = request.get_response(app)
        self.assertEqual(response.status_int, 200)
        self.assertIn("application/json", response.headers['Content-Type'])
        self.assertDictEqual(
            json.decode(response.body),
            {"name": "I am DR bot (https://telegram.me/DzzzzR_bot)", "result": "Info"}
        )

    def test_bad_post(self):
        request = webapp2.Request.blank("/")
        request.method = "POST"
        response = request.get_response(app)
        self.assertEqual(response.status_int, 200)
        self.assertIn("application/json", response.headers['Content-Type'])
        self.assertDictEqual(
            json.decode(response.body),
            {"name": "I am DR bot (https://telegram.me/DzzzzR_bot)", "result": "Info"}
        )

    def test_json_empty_post(self):
        request = webapp2.Request.blank("/")
        request.method = "POST"
        request.headers["Content-Type"] = "application/json"
        response = request.get_response(app)
        self.assertEqual(response.status_int, 200)
        self.assertIn("application/json", response.headers['Content-Type'])
        self.assertDictEqual(
            json.decode(response.body),
            {"name": "I am DR bot (https://telegram.me/DzzzzR_bot)", "result": "Info"}
        )

    def test_no_json_empty_post(self):
        request = webapp2.Request.blank("/")
        request.method = "POST"
        request.headers["Content-Type"] = "text/xml"
        response = request.get_response(app)
        self.assertEqual(response.status_int, 200)
        self.assertIn("application/json", response.headers['Content-Type'])
        self.assertDictEqual(
            json.decode(response.body),
            {"name": "I am DR bot (https://telegram.me/DzzzzR_bot)", "result": "Info"}
        )

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
                    u'id': 1
                },
                u'message_id': 1,
                u'chat': {
                    u'type': u'group',
                    u'id': -1,
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
                'chat_id': -1,
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
                    u'id': 1
                },
                u'message_id': 1,
                u'chat': {
                    u'type': u'group',
                    u'id': -1,
                    u'title': u'КС'
                }
            }
        })
        response = request.get_response(app)
        self.assertEqual(response.status_int, 200)
        self.assertIn("application/json", response.headers['Content-Type'])
        self.assertDictEqual(json.decode(response.body), {})

    def test_json_inline(self):
        request = webapp2.Request.blank("/")
        request.method = "POST"
        request.headers["Content-Type"] = "application/json"
        request.body = json.encode({
            'update': 1,
            'inline_query': {
                u'date': 1450696897,
                u'text': u'как дела?',
                u'from': {
                    u'username': u'm_messiah',
                    u'first_name': u'Maxim',
                    u'last_name': u'Muzafarov',
                    u'id': 1
                },
                u'id': 1,
                u'chat': {
                    u'type': u'group',
                    u'id': -1,
                    u'title': u'КС'
                }
            }
        })
        response = request.get_response(app)
        self.assertEqual(response.status_int, 200)
        self.assertIn("application/json", response.headers['Content-Type'])
        response = json.decode(response.body)
        self.assertIn('results', response)
        self.assertEqual('answerInlineQuery', response['method'])
        self.assertIn('Inline mode not implemented', response['results'])


    def test_json_empty(self):
        request = webapp2.Request.blank("/")
        request.method = "POST"
        request.headers["Content-Type"] = "application/json"
        request.body = json.encode({
            'update': 1,
        })
        response = request.get_response(app)
        self.assertEqual(response.status_int, 200)
        self.assertIn("application/json", response.headers['Content-Type'])
        self.assertDictEqual(
            json.decode(response.body),
            {"name": "I am DR bot (https://telegram.me/DzzzzR_bot)", "result": "Info"}
        )

    def test_json_contact(self):
        request = webapp2.Request.blank("/")
        request.method = "POST"
        request.headers["Content-Type"] = "application/json"
        request.body = json.encode({
            'update': 1,
            'message': {
                u'date': 1450696897,
                u'contact': {
                    'user_id': '123'
                },
                u'from': {
                    u'username': u'm_messiah',
                    u'first_name': u'Maxim',
                    u'last_name': u'Muzafarov',
                    u'id': 1
                },
                u'message_id': 1,
                u'chat': {
                    u'type': u'group',
                    u'id': -1,
                    u'title': u'КС'
                }
            }
        })
        response = request.get_response(app)
        self.assertEqual(response.status_int, 200)
        self.assertIn("application/json", response.headers['Content-Type'])
        response = json.decode(response.body)
        self.assertIn('text', response)
        self.assertIn('123', response['text'])

    def test_json_new_participant(self):
        request = webapp2.Request.blank("/")
        request.method = "POST"
        request.headers["Content-Type"] = "application/json"
        request.body = json.encode({
            'update': 1,
            'message': {
                u'date': 1450696897,
                u'new_chat_participant': {
                    'first_name': u'Дозорный'
                },
                u'from': {
                    u'username': u'm_messiah',
                    u'first_name': u'Maxim',
                    u'last_name': u'Muzafarov',
                    u'id': 1
                },
                u'message_id': 1,
                u'chat': {
                    u'type': u'group',
                    u'id': -1,
                    u'title': u'КС'
                }
            }
        })
        response = request.get_response(app)
        self.assertEqual(response.status_int, 200)
        self.assertIn("application/json", response.headers['Content-Type'])
        response = json.decode(response.body)
        self.assertIn('text', response)
        self.assertIn(u'Дозорный', response['text'])

    def test_json_left_participant(self):
        request = webapp2.Request.blank("/")
        request.method = "POST"
        request.headers["Content-Type"] = "application/json"
        request.body = json.encode({
            'update': 1,
            'message': {
                u'date': 1450696897,
                u'left_chat_participant': {
                    'first_name': u'Дозорный'
                },
                u'from': {
                    u'username': u'm_messiah',
                    u'first_name': u'Maxim',
                    u'last_name': u'Muzafarov',
                    u'id': 1
                },
                u'message_id': 1,
                u'chat': {
                    u'type': u'group',
                    u'id': -1,
                    u'title': u'КС'
                }
            }
        })
        response = request.get_response(app)
        self.assertEqual(response.status_int, 200)
        self.assertIn("application/json", response.headers['Content-Type'])
        response = json.decode(response.body)
        self.assertIn('text', response)
        self.assertEqual(u"А я буду скучать...", response['text'])

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
                    u'id': 1
                },
                u'message_id': 1,
                u'chat': {
                    u'type': u'group',
                    u'id': -1,
                    u'title': u'КС'
                }
            }
        })
        request.get_response(app)
        self.assertIn(-1, SESSIONS)


class TestBot(TestCase):
    def send_message(self, text, empty=False):
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
                    u'id': 1
                },
                u'message_id': 1,
                u'chat': {
                    u'type': u'user',
                    u'id': 1,
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

        if empty:
            self.assertDictEqual(response, {})
            return {}

        self.assertIn('text', response)
        return response['text']



    def send_gps(self, gps, error=False, empty=False):
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
                    u'id': 1
                },
                u'message_id': 1,
                u'chat': {
                    u'type': u'user',
                    u'id': 1,
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

        if error:
            self.assertEqual('sendMessage', response['method'])
            return response['text']

        if empty:
            self.assertDictEqual(response, {})
            return {}

        self.assertEqual('sendLocation', response['method'])
        return response['latitude'], response['longitude']

    def test_not_found(self):
        self.assertIn(u"Команда не найдена. Используйте /help", self.send_message("/abracadabra"))

    def test_start(self):
        self.assertEqual(u"Внимательно слушаю!", self.send_message("/start"))

    def test_start_name(self):
        self.assertEqual(u"Внимательно слушаю!", self.send_message("/start@DzzzzR_bot"))

    def test_bad_command(self):
        self.send_message("/start@", empty=True)

    def test_show_sessions(self):
        self.assertIn(u"Сейчас используют", self.send_message("/show_sessions"))

    def test_about(self):
        self.assertEqual(
            u"Привет!\n"
            u"Мой автор @m_messiah\n"
            u"Мой код: https://github.com/m-messiah/dzzzzr-bot\n"
            u"\nА еще принимаются пожертвования:\n"
            u"https://paypal.me/muzafarov\n"
            u"http://yasobe.ru/na/m_messiah",
            self.send_message("/about")
        )

    def test_base64(self):
        self.assertEqual(u"0J/RgNC40LLQtdGC", self.send_message(u"/base64 Привет"))
        self.assertEqual(u"Привет", self.send_message(u"/base64 0J/RgNC40LLQtdGC"))
        self.assertEqual(u"MTAxMQ==", self.send_message(u"/base64 1011"))

    def test_pos(self):
        self.assertIn(u"абвя", self.send_message(u"/pos 1 2 3 33"))
        self.assertIn(u"abcg", self.send_message(u"/pos 1 2 3 33"))
        self.assertIn(u"abcg", self.send_message(u"/pos 1,2,3,33"))
        self.send_message(u"/pos 1,2,3,x", empty=True)

    def test_gps(self):
        self.send_message('/resume')
        eta = (56.847222, 60.675)
        dd = u"56.847222, 60.675"
        dmr = u"56 50.8333, 60 40.5"
        dmsr = u"56 50 50, 60 40 30"
        self.assertEqual(eta, self.send_gps(dd))
        self.assertEqual(eta, self.send_gps(dmr))
        self.assertEqual(eta, self.send_gps(dmsr))
        self.send_gps(u"1 2 3 4, 1 2 3 4", error=True)
        self.send_gps(u"x y z, a b c", empty=True)

    def test_version(self):
        self.assertIn(u"Версия", self.send_message(u"/version"))

    def test_hello(self):
        self.assertEqual(u"Привет!", self.send_message(u"Привет бот!"))

    def test_help(self):
        self.assertIn(u"Я могу принимать следующие команды:\n", self.send_message(u"/help"))


class TestCodeParsing(TestCase):
    def setUp(self):
        self.d = DozoR({'id': 1, 'username': 'm_messiah'})
        self.d.enabled = True


def generator_codes(prefix, code):
    def test(self):
        self.d.prefix = prefix
        result = self.d.code({'text': code})
        self.assertIn(u"войти в движок", result)
    return test


for prefix in [u"", u"27D"]:
    for num, code in enumerate(
        [u"1D23R4", u"1д23р4", u"D23R4", u"1D234R", u"1D2D34R",
         u"1D23R4R", u"D234R", u"23R4", u"23R", u"123Р6",
         u"1 DстартR", u"123Р"]):
        setattr(TestCodeParsing, "test_code_parsing_%s_%s" % (prefix, num), generator_codes(prefix, code))
