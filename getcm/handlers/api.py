import json
import time
import re
from tornado.web import asynchronous
from getcm import cache
from getcm.model.schema import File
from base import BaseHandler


class ApiHandler(BaseHandler):
    request_id = None

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
            return fn()

    def method_get_builds(self):
        channels = self.params.get('channels', None)
        device = self.params.get('device', None)
        after = int(self.params.get('after', 0))
        if not channels or not device:
            self.set_status(500)
            return self.fail("Invalid Parameters")

        cache_key = 'api_after_%s_%s' % (device, str(round(after, -4)))
        result = cache.get(cache_key)
        if result is not None:
            return self.success(result)

        result = []
        for channel in channels:
            file_obj = File.get_build(channel, device, after)
            if file_obj is not None:
                changesfile = re.sub(file_obj.filename, "CHANGES.txt", file_obj.full_path)
                result.append({
                    'channel': channel,
                    'filename': file_obj.filename,
                    'url': "http://getcm.thebronasium.com/get/%s" % file_obj.full_path,
                    'changes': "http://getcm.thebronasium.com/get/%s" % changesfile,
                    'md5sum': file_obj.md5sum,
                    'timestamp': file_obj.date_created.strftime('%s')
                })

        cache.set(cache_key, result)

        return self.success(result)

    def method_get_all_builds(self):
        channels = self.params.get('channels', None)
        device = self.params.get('device', None)
        limit = int(self.params.get('limit', 3))
        if not channels or not device:
            self.set_status(500)
            return self.fail("Invalid Parameters")

        cache_key = 'api_all_%s_%s' % (device, str(limit))
        result = cache.get(cache_key)
        if result is not None:
            return self.success(result)

        result = []
        for channel in channels:
            files = File.browse(device, channel, limit)
            for file_obj in files:
                if file_obj is not None:
                    changesfile = re.sub(file_obj.filename, "CHANGES.txt", file_obj.full_path)
                    result.append({
                        'channel': channel,
                        'filename': file_obj.filename,
                        'url': "http://getcm.thebronasium.com/get/%s" % file_obj.full_path,
                        'changes': "http://getcm.thebronasium.com/get/%s" % changesfile,
                        'md5sum': file_obj.md5sum,
                        'timestamp': file_obj.date_created.strftime('%s')
                    })

        cache.set(cache_key, result)

        return self.success(result)
