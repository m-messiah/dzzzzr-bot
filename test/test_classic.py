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
from test_classic_engine import app as dr_engine
from main import app, SESSIONS


class TestClassic(TestCase):
    def setUp(self):
        self.engine = Process(target=httpserver.serve, args=(dr_engine, ),
                              kwargs={'host': "127.0.0.1", 'port': "5000"})
        self.engine.start()

    def tearDown(self):
        self.send_message('/stop')
        self.engine.terminate()

    def auth(self):
        self.send_message(
            "/set_dzzzr http://127.0.0.1:5000/ spb_Captain 123456 "
            "bot botpassword"
        )

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

    def test_set_dzzzr_small_arguments(self):
        response = self.send_message(
            "/set_dzzzr http://localhost:5000/ spb_Captain 123456 bot"
        )

        self.assertIn("/set_dzzzr", response,
                      "Accept not enough arguments")

    def test_set_dzzzr(self):
        response = self.send_message(
            "/set_dzzzr http://localhost:5000/ spb_Captain 123456 "
            "bot botpassword 1D"
        )
        self.assertNotIn("/set_dzzzr", response,
                         "Arguments with prefix bad splitted")
        self.assertNotEqual("", SESSIONS[1].credentials)
        self.assertEqual("1D", SESSIONS[1].prefix)

    def test_set_dzzzr_custom_mask_with_prefix(self):
        self.send_message(
            "/set_dzzzr http://localhost:5000/ spb_Captain 123456 "
            "bot botpassword 1D [0-9fbFB]+"
        )
        self.assertEqual(True, bool(SESSIONS[1].dr_code.search("fb")))

    def test_set_dzzzr_custom_mask(self):
        self.send_message(
            "/set_dzzzr http://localhost:5000/ spb_Captain 123456 "
            "bot botpassword [0-9fbFB]+"
        )
        self.assertEqual("", SESSIONS[1].prefix)
        self.assertEqual(True, bool(SESSIONS[1].dr_code.search("fb")))
        self.assertEqual(True, bool(SESSIONS[1].dr_code.match("1f23b4")))

    def test_code(self):
        self.auth()
        self.assertIn(u"Код принят", self.send_message(u"1d23r4"))
        self.assertIn(u"Код не принят", self.send_message(u"2d23r4"))

    def test_remain_codes(self):
        self.auth()
        response = self.send_message(u"/codes")
        self.assertNotIn(u"/help", response)
        self.assertIn(u"Сектор 1 (осталось 7): 12 (1), 16 (1), 17 (1+), "
                      u"18 (1), 22 (1), 23 (1+), 24 (1)", response)
        self.assertIn(u"Сектор 2 (осталось 0)", response)

    def test_time(self):
        self.auth()
        response = self.send_message(u"/time")
        self.assertNotIn(u"/help", response)
        self.assertIn("00:29:23", response)
