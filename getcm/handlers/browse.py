import time
from tornado.web import asynchronous
from getcm.model.schema import File, Device
from getcm.model.devicemap import devicemap
from getcm.utils.string import base62_encode
from base import BaseHandler

class BrowseHandler(BaseHandler):
    @asynchronous
    def get(self):
        device = self.request.arguments.get('device', [None])[0]
        type = self.request.arguments.get('type', [None])[0]
        files = File.browse(device, type)

        for fileobj in files:
            fileobj.base62 = base62_encode(fileobj.id)

        devicelist = Device.get_all()

        if 'dtime' not in self.devicedict or self.devicedict['dtime'] < time.time() - 300:
            for codename in devicelist:
               if codename in devicemap:
                   self.devicedict[codename] = devicemap[codename]
               else:
                   self.devicedict[codename] = codename

            self.devicedict['dtime'] = time.time()

        def respond(builds):
            return self.render("browse.mako", {'request_type': type, 'request_device': device, 'devices': devicelist,  'devicenames': self.devicedict, 'files': files, 'builds': builds})

        return respond([])
