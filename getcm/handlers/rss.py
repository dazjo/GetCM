from getcm.model.schema import File
from base import BaseHandler


class RssHandler(BaseHandler):
    def get(self):
        device = self.request.arguments.get('device', [None])[0]
        type = self.request.arguments.get('type', [None])[0]
        files = File.browse(device, type, 100)
        self.set_header('Content-Type', "application/xml; charset=utf-8")
        self.render("rss.mako", {'files': files})
