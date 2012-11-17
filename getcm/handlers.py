import tornado.web
import random
import urllib
import logging
import re
import json
import time
import sys

from model.schema import File, Device
from model.devicemap import devicemap
from getcm.utils.string import base62_encode
from tornado.web import asynchronous

class BaseHandler(tornado.web.RequestHandler):
    @property
    def activebuilds(self):
        return self.application.activebuilds

    @property
    def db(self):
        return self.application.db

    @property
    def mirrorpool(self):
        return self.application.mirrorpool

    @property
    def devicedict(self):
        return self.application.devicedict

    @property
    def apicache(self):
        return self.application.apicache

    def render(self, template, params={}):
        tpl = self.application.lookup.get_template(template)
        self.write(tpl.render(**params))
        self.finish()

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

class RssHandler(BaseHandler):
    def get(self):
        device = self.request.arguments.get('device', [None])[0]
        type = self.request.arguments.get('type', [None])[0]
        files = File.browse(device, type, 100)
        self.set_header('Content-Type', "application/xml; charset=utf-8")
        self.render("rss.mako", {'files': files})

class ApiHandler(BaseHandler):
    request_id = None

    def post(self):
        try:
            body = json.loads(self.request.body)
        except ValueError:
            self.set_status(500)
            return self.fail("Error decoding JSON")

        self.method = body.get('method', None)
        self.request_id = body.get('id', None)
        self.params = body.get('params', None)

        if not self.method:
            self.set_status(500)
            return self.fail("method must be specified")

        try:
            fn = getattr(self, "method_%s" % self.method)
        except AttributeError:
            self.set_status(405)
            return self.fail("Unknown method")
        else:
            fn()

    def fail(self, error_message):
        return self.write(json.dumps({
            'result': None,
            'error': error_message,
            'id': self.request_id
        }, indent=True))

    def success(self, result):
        return self.write(json.dumps({
            'result': result,
            'error': None,
            'id': self.request_id
        }, indent=True))

    def method_get_builds(self):
        channels = self.params.get('channels', None)
        device = self.params.get('device', None)
        after = int(self.params.get('after', 0))
        if not channels or not device:
            self.set_status(500)
            return self.fail("Invalid Parameters")

        cachekey = 'after_'+device+'_'+str(round(after,-4))
        if cachekey in self.apicache and self.apicache[cachekey]['dtime'] + 900 > time.time():
            return self.success(self.apicache[cachekey]['result'])

        result = []
        for channel in channels:
            file_obj = File.get_build(channel, device, after)
            if file_obj is not None:
                changesfile = re.sub(file_obj.filename,"CHANGES.txt",file_obj.full_path)
                result.append({
                    'channel': channel,
                    'filename': file_obj.filename,
                    'url': "http://get.cm/get/%s" % file_obj.full_path,
                    'changes': "http://get.cm/get/%s" % changesfile,
                    'md5sum': file_obj.md5sum,
                    'timestamp': file_obj.date_created.strftime('%s')
                })

        self.apicache[cachekey] = { 'dtime': time.time(),
                                    'result': result };

        return self.success(result)

    def method_get_all_builds(self):
        channels = self.params.get('channels', None)
        device = self.params.get('device', None)
        limit = int(self.params.get('limit', 3))
        if not channels or not device:
            self.set_status(500)
            return self.fail("Invalid Parameters")

        cachekey = 'all_'+device+'_'+str(limit)
        if cachekey in self.apicache and self.apicache[cachekey]['dtime'] + 900 > time.time():
            return self.success(self.apicache[cachekey]['result'])

        result = []
        for channel in channels:
            files = File.browse(device, channel, limit)
            for file_obj in files:
                if file_obj is not None:
                    changesfile = re.sub(file_obj.filename,"CHANGES.txt",file_obj.full_path)
                    result.append({
                        'channel': channel,
                        'filename': file_obj.filename,
                        'url': "http://get.cm/get/%s" % file_obj.full_path,
                        'changes': "http://get.cm/get/%s" % changesfile,
                        'md5sum': file_obj.md5sum,
                        'timestamp': file_obj.date_created.strftime('%s')
                    })

        self.apicache[cachekey] = { 'dtime': time.time(),
                                    'result': result };

        return self.success(result)

class MirrorApplicationHandler(BaseHandler):
    def get(self):
        return self.render("mirror.mako")
