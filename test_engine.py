# coding=utf-8
import webapp2


class Go(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "text/html; charset=cp1251"
        self.response.write(open("test_engine.html").read()
                            .replace("{{MESSAGE}}",
                                     u"Код не принят".encode("cp1251")))

    def post(self):
        self.response.headers['Content-Type'] = "text/html; charset=cp1251"
        if 'cod' in self.request.POST:
            if self.request.POST['cod'] == "1D23R4":
                message = u"Код принят"
            else:
                message = u"Код не принят"

        elif 'password' in self.request.POST:
            if self.request.POST['password'] == "botpassword":
                message = u"Авторизация пройдена успешно"
            else:
                message = u"Авторизация не удалась"

        else:
            message = u"Произошла ошибка. Ищите дальше"

        self.response.write(open("test_engine.html").read()
                            .replace("{{MESSAGE}}", message.encode("cp1251")))


app = webapp2.WSGIApplication([('/', Go), ], debug=True)
