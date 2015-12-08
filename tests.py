# coding=utf-8
from unittest import TestCase
from main import DozoR


class TestDozoR(TestCase):
    def test_set_dzzzr(self):
        d = DozoR(1)
        result = d.set_dzzzr(
            "http://classic.dzzzr.ru/spb/go/ spb_Captain 123456 bot"
        )

        self.assertIn("/set_dzzzr", result,
                      "Accept not enough arguments")
        result = d.set_dzzzr(
            "http://classic.dzzzr.ru/spb/go/ spb_Captain 123456 "
            "bot botpassword 1D"
        )
        self.assertNotIn("/set_dzzzr", result,
                         "Arguments with prefix bad splitted")
        self.assertEqual("1D", d.prefix)

    def test_not_found(self):
        d = DozoR(1)
        self.assertIsNotNone(d.not_found("1"))

    def test_start(self):
        d = DozoR(1)
        self.assertIsNotNone(d.start("1"))

    def test_about(self):
        d = DozoR(1)
        self.assertIsNotNone(d.about("1"))
        self.assertIn("m_messiah", d.about("0"), "Author lost")

    def test_base64(self):
        d = DozoR(1)
        self.assertEqual("0J/RgNC40LLQtdGC", d.base64(u"Привет"))
        self.assertEqual("Привет", d.base64(u"0J/RgNC40LLQtdGC"))

    def test_pos(self):
        d = DozoR(1)
        self.assertIn(u"абвя", d.pos(u"1 2 3 33"))
        self.assertIn(u"abcg", d.pos(u"1 2 3 33"))

    def test_gps(self):
        d = DozoR(1)
        eta = (56.847222, 60.675)
        dd = u"56.847222, 60.675"
        dmr = u"56 50.8333, 60 40.5"
        dmsr = u"56 50 50, 60 40 30"
        self.assertEqual(d.gps(dd), eta)
        self.assertEqual(d.gps(dmr), eta)
        self.assertEqual(d.gps(dmsr), eta)


    def test_code(self):
        d = DozoR(1)
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
                result = d.code(code)
                self.assertIn(u"войти в движок",
                              result,
                              u"Code %s not parsed" % code)
