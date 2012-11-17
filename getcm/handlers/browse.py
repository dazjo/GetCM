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

        # Set default values for device names dictionary
        devicedict = {}
        for codename in devicelist:
           if codename in devicemap:
               devicedict[codename] = devicemap[codename]
           else:
               devicedict[codename] = codename

        return self.render("browse.mako", {'request_type': type, 'request_device': device, 'devices': devicelist, 'devicenames': devicedict, 'files': files})
