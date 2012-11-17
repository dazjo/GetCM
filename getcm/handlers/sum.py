from getcm.model.schema import File
from base import BaseHandler

class SumHandler(BaseHandler):
    def get(self, request):
        if request.endswith(".zip") and "/" not in request:
            fileobj = File.get_by_filename(request)
        elif request.endswith(".zip") and "/" in request:
            fileobj = File.get_by_fullpath(request)
        else:
            fileobj = File.get_by_base62(request)
            
        if fileobj is None:
            self.write("404 Not Found")
            return self.set_status(404)
            
        return self.write("%s  %s" % (fileobj.filename, fileobj.md5sum))

