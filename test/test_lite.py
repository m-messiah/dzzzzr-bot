# coding=utf-8
from unittest import TestCase
import sys
import time
import os.path
from multiprocessing import Process
from test_lite_engine import app as lite_engine
import messages
from main import app, SESSIONS
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
from paste import httpserver  # noqa E402


class TestLite(TestCase):
    def setUp(self):
        self.engine = Process(target=httpserver.serve, args=(lite_engine, ),
                              kwargs={'host': "127.0.0.1", 'port': "5001"})
        self.engine.start()
        time.sleep(1)

    def tearDown(self):
        self.send_message('/stop')
        self.engine.terminate()
        time.sleep(1)

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
        self.assertIn(messages.DOZOR_AUTH_FAILED, response, "Bad password")

    def test_auth_good(self):
        response = self.auth()
        self.assertNotIn("/set_lite", response, "Bad parse set_lite")
        self.assertNotEqual("", SESSIONS[1].dozor.credentials)

    def test_code(self):
        self.auth()
        self.assertIn(u"Код принят", self.send_message(u"1d23l4"))
        self.assertIn(u"Код не принят", self.send_message(u"2d23l4"))

    def test_remain_codes(self):
        self.auth()
        response = self.send_message(u"/codes")
        self.assertNotIn(u"/help", response)
        self.assertIn(u"Сектор Город (осталось 0):", response)
        self.assertIn(u"Сектор Район (осталось 0):", response)
        self.assertIn(u"Сектор Улица (осталось 1): 1 (null)", response)
        self.assertIn(u"Сектор Дом (осталось 1): 1 (null)", response)
        self.assertIn(u"Сектор Пров.код (осталось 1): 1 (1)", response)
        self.assertIn(u"Сектор Локация (осталось 1): 1 (3+)", response)

    def test_time(self):
        self.auth()
        response = self.send_message(u"/time")
        self.assertNotIn(u"/help", response)
        self.assertIn("18:50", response)
