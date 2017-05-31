# coding=utf-8
from unittest import TestCase
import sys
import os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
sys.path.insert(
    0, '/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/platform/google_appengine/lib/yaml/lib')
sys.path.insert(0, '/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/platform/google_appengine')
import webapp2
from webapp2_extras import json
from multiprocessing import Process
from paste import httpserver
from test_lite_engine import app as lite_engine
from main import app, SESSIONS


class TestLite(TestCase):
    def setUp(self):
        self.engine = Process(target=httpserver.serve, args=(lite_engine, ),
                              kwargs={'host': "127.0.0.1", 'port': "5001"})
        self.engine.start()

    def tearDown(self):
        self.send_message('/stop')
        self.engine.terminate()

    def auth(self):
        return self.send_message("/set_lite http://localhost:5001/ 123456")

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
        self.assertIn('text', response)
        return response['text']

    def test_auth_without_pin(self):
        response = self.send_message("/set_lite http://localhost:5001/")
        self.assertIn("/set_lite", response, "Accept not enough arguments")

    def test_auth_bad_pin(self):
        response = self.send_message("/set_lite http://localhost:5001/ 12345")
        self.assertIn(u"Авторизация не удалась", response, "Bad password")

    def test_auth_good(self):
        response = self.auth()
        self.assertNotIn("/set_lite", response, "Bad parse set_lite")
        self.assertNotEqual("", SESSIONS[1].credentials)

    def test_code(self):
        self.auth()
        self.assertIn(u"Код принят", self.send_message(u"1d23l4"))
        self.assertIn(u"Код не принят", self.send_message(u"2d23l4"))

    def test_remain_codes(self):
        self.auth()
        response = self.send_message(u"/codes")
        self.assertNotIn(u"/help", response)
        self.assertIn(u"(Всего - 6, принято - 2)", response)

    def test_time(self):
        self.auth()
        response = self.send_message(u"/time")
        self.assertNotIn(u"/help", response)
        self.assertIn("18:50", response)
