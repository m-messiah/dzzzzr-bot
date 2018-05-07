# coding=utf-8
import sys
import os.path
# mac os
google_cloud_sdk_path = '/usr/local/Caskroom/google-cloud-sdk/latest/google-cloud-sdk/platform/google_appengine'
sys.path.insert(1, google_cloud_sdk_path)
sys.path.insert(1, google_cloud_sdk_path + '/lib/yaml/lib')
# travis
sys.path.insert(1, 'google_appengine')
sys.path.insert(1, 'google_appengine/lib/yaml/lib')
CWD = os.path.dirname(__file__)
sys.path.insert(1, os.path.join(CWD, '../lib'))
import webapp2  # noqa E402


class Lite(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "text/html; charset=cp1251"
        if self.request.GET.get('pin') == '123456':
            self.response.write(
                open(os.path.join(CWD, 'test_lite_engine.html')).read()
                .replace("{{ MESSAGE }}", u"Добро пожаловать, тестер".encode("cp1251")))
        else:
            self.response.write(
                open(os.path.join(CWD, 'test_lite_engine.html')).read()
                .replace("{{ MESSAGE }}", u"Авторизация не удалась".encode("cp1251")))

    def post(self):
        self.response.headers['Content-Type'] = "text/html; charset=cp1251"
        if 'cod' in self.request.POST:
            if self.request.POST['cod'] == "1D23L4":
                message = u"Код принят"
            else:
                message = u"Код не принят"

        else:
            message = u"Произошла ошибка. Ищите дальше"

        self.response.write(
            open(os.path.join(CWD, 'test_lite_engine.html')).read()
            .replace("{{ MESSAGE }}", message.encode("cp1251")))


app = webapp2.WSGIApplication([('/', Lite), ], debug=True)

if __name__ == '__main__':
    from paste import httpserver
    httpserver.serve(app, host="127.0.0.1", port="5001")
