from base import BaseHandler


class MirrorApplicationHandler(BaseHandler):
    def get(self):
        return self.render("mirror.mako")
