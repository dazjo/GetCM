import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    @property
    def mirrorpool(self):
        return self.application.mirrorpool

    def render(self, template, params={}):
        tpl = self.application.lookup.get_template(template)
        self.write(tpl.render(**params))
        self.finish()
