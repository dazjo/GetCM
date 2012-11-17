from getcm.model.schema import File
from base import BaseHandler

class ZipHandler(BaseHandler):
    def get(self, request):
        request = request + ".zip"

        if "/" in request:
            fileobj = File.get_by_fullpath(request)
        elif "/" not in request:
            fileobj = File.get_by_filename(request)

        if fileobj is None and "/" not in request:
            self.write("404 Not Found")
            return self.set_status(404)
        elif fileobj is None:
            full_path = request
        else:
            full_path = fileobj.full_path

            url = self.mirrorpool.next() % full_path

        webseed = self.request.arguments.get('webseed', [None])[0]
        if webseed:
            url = url + "?" + urllib.urlencode({'webseed': webseed})
            logging.warn("Webseeding for '%s'" % fileobj.filename)

        return self.redirect(url)
