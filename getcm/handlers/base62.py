from getcm.model.schema import File
from getcm.utils.string import base62_encode
from base import BaseHandler

class Base62Handler(BaseHandler):
    def get(self, request):
        # Some torrent clients are retarded and urlencode the querystring.
        # if that happens, they don't deserve to download.
        if request.endswith("?webseed=1"):
            self.write("403 Forbidden")
            return self.set_status(403)

        fileobj = File.get_by_base62(request)
        if fileobj is None:
            self.write("404 Not Found")
            return self.set_status(404)

        # Determine mirror to use
        url = self.mirrorpool.next() % fileobj.full_path

        webseed = self.request.arguments.get('webseed', [None])[0]
        if webseed:
            url = url + "?" + urllib.urlencode({'webseed': webseed})
            logging.warn("Webseeding for '%s'" % fileobj.filename)

        return self.redirect(url)

