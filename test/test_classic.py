# coding=utf-8
from unittest import TestCase
import sys
import time
import os.path
from multiprocessing import Process
from test_classic_engine import app as dr_engine
import messages
from main import app, SESSIONS, CREDENTIALS
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


class TestClassic(TestCase):
    def setUp(self):
        self.engine = Process(target=httpserver.serve, args=(dr_engine, ),
                              kwargs={'host': "127.0.0.1", 'port': "5000"})
        self.engine.start()
        time.sleep(1)

    def tearDown(self):
        print CREDENTIALS
        self.send_message('/stop')
        self.send_message("/stop", chat_id=2)
        self.engine.terminate()
        time.sleep(1)

    def auth(self):
        return self.send_message("/set_dzzzr http://localhost:5000/ spb_Captain 123456 bot botpassword")

    def send_message(self, text, chat_id=1, empty=False):
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
                    u'type': u'group',
                    u'id': chat_id,
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

    def test_set_dzzzr_small_arguments(self):
        response = self.send_message("/set_dzzzr http://localhost:5000/ spb_Captain 123456 bot")
        self.assertIn("/set_dzzzr", response, "Accept not enough arguments")

    def test_set_dzzzr_broken_arguments(self):
        response = self.send_message("/set_dzzzr htt://localhost:5000/ spb_Captain 123456 bot botpassword")
        self.assertIn("Incorrect format", response)

    def test_set_dzzzr(self):
        response = self.send_message("/set_dzzzr http://localhost:5000/ spb_Captain 123456 bot botpassword 1D")
        self.assertNotIn("/set_dzzzr", response, "Arguments with prefix bad splitted")
        self.assertNotEqual("", SESSIONS[1].dozor.credentials)
        self.assertEqual("1D", SESSIONS[1].dozor.prefix)

    def test_set_dzzzr_custom_mask_with_prefix(self):
        self.send_message("/set_dzzzr http://localhost:5000/ spb_Captain 123456 bot botpassword 1D [0-9fbFB]+")
        self.assertEqual(True, bool(SESSIONS[1].dozor.dr_code.search("fb")))

    def test_set_dzzzr_custom_mask(self):
        self.send_message("/set_dzzzr http://localhost:5000/ spb_Captain 123456 bot botpassword [0-9fbFB]+")
        self.assertEqual("", SESSIONS[1].dozor.prefix)
        self.assertEqual(True, bool(SESSIONS[1].dozor.dr_code.search("fb")))
        self.assertEqual(True, bool(SESSIONS[1].dozor.dr_code.match("1f23b4")))

    def test_set_dzzzr_separate_chats(self):
        self.send_message("/set_dzzzr http://localhost:5000/ spb_Captain 123456 bot botpassword", chat_id=2)
        response = self.auth()
        self.assertNotIn("/set_dzzzr", response)
        self.assertIn("/stop", response)

    def test_set_dzzzr_stop_set_dzzzr(self):
        self.auth()
        self.send_message("/stop")
        response = self.auth()
        self.assertNotIn("/set_dzzzr", response)
        self.assertIn("bot", response)

    def test_set_dzzzr_stop_set_dzzzr_2(self):
        self.send_message("/set_dzzzr http://localhost:5000/ spb_Captain 123456 bot botpassword", chat_id=2)
        self.send_message("/stop", chat_id=2)
        response = self.auth()
        self.assertNotIn("/set_dzzzr", response)
        self.assertIn("bot", response)

    def test_set_dzzzr_bad_password(self):
        response = self.send_message("/set_dzzzr http://localhost:5000/ spb_Captain 123456 bot wrongpassword")
        self.assertIn(messages.DOZOR_AUTH_FAILED, response)

    def test_code(self):
        self.auth()
        self.assertIn(u"Код принят", self.send_message(u"1d23r4"))
        self.assertIn(u"Код не принят", self.send_message(u"2d23r4"))

    def test_empty_text(self):
        self.auth()
        self.send_message(u" ", empty=True)

    def test_pause(self):
        self.auth()
        self.assertIn(u"/resume", self.send_message(u"/pause"))
        self.send_message(u"1d23r4", empty=True)

    def test_broken_engine(self):
        self.auth()
        self.engine.terminate()
        response = self.send_message(u"/codes")
        self.assertIn(messages.DOZOR_NO_ANSWER, response)

    def test_remain_codes(self):
        self.auth()
        response = self.send_message(u"/codes")
        self.assertNotIn(u"/help", response)
        self.assertIn(u"Сектор 1 (осталось 7): 12 (1), 16 (1), 17 (1+), 18 (1), 22 (1), 23 (1+), 24 (1)", response)
        self.assertIn(u"Сектор 2 (осталось 0)", response)

    def test_codes_no_auth(self):
        response = self.send_message(u"/codes")
        self.assertIn(messages.DOZOR_NEED_AUTH, response)

    def test_time(self):
        self.auth()
        response = self.send_message(u"/time")
        self.assertNotIn(u"/help", response)
        self.assertIn("00:29:23", response)

    def test_time_no_auth(self):
        response = self.send_message(u"/time")
        self.assertIn(messages.DOZOR_NEED_AUTH, response)

    def test_time_bad_engine(self):
        self.auth()
        self.engine.terminate()
        response = self.send_message(u"/time")
        self.assertIn(messages.DOZOR_NO_ANSWER, response)
