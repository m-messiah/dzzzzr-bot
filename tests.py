# coding=utf-8
from unittest import TestCase
from main import DozoR

class TestDozoR(TestCase):
    def test_set_dzzzr(self):
        d = DozoR(1)
        result = d.set_dzzzr(
            "http://classic.dzzzr.ru/spb/go/ spb_Captain 123456 bot"
        )

        self.assertIn("/set_dzzzr", result['text'],
                      "Accept not enough arguments")
        result = d.set_dzzzr(
            "http://classic.dzzzr.ru/spb/go/ spb_Captain 123456 "
            "bot botpassword 1D"
        )
        self.assertNotIn("/set_dzzzr", result['text'],
                         "Arguments with prefix bad splitted")
        self.assertEqual("1D", d.prefix)

    def test_not_found(self):
        d = DozoR(1)
        self.assertEqual(1, d.not_found(0)['chat_id'],
                         "Chat ID not equals")

    def test_start(self):
        d = DozoR(1)
        self.assertEqual(1, d.start(0)['chat_id'],
                         "Chat ID not equals")

    def test_about(self):
        d = DozoR(1)
        self.assertEqual(1, d.about(0)['chat_id'],
                         "Chat ID not equals")
        self.assertIn("m_messiah", d.about(0)['text'],
                      "Author lost")

    def test_base64(self):
        d = DozoR(1)
        self.assertEqual("0J/RgNC40LLQtdGC",
                         d.base64(u"Привет")['text'])
        self.assertEqual("Привет",
                         d.base64(u"0J/RgNC40LLQtdGC")['text'])

    def test_code(self):
        d = DozoR(1)
        for prefix in [u"", u"27D"]:
            d.prefix = prefix

            for code in [u"1D23R4",
                         u"1д23р4",
                         u"D23R4",
                         u"1D234R",
                         u"D234R",
                         u"23R4",
                         u"23R",
                         u"123Р6",
                         u"123Р"]:
                result = d.code(code)['text']
                self.assertIn("войти в движок",
                              result,
                              u"Code %s not parsed" % code)
