import time
import re
import json
import logging
import functools
from tornado.httpclient import AsyncHTTPClient

class ActiveBuilds(object):
    def __init__(self):
        self.builds = []
        self.expire = 0

        self.fetching = False
        self.builds_tmp = []
        self.pool = []
        self.requests = 0

    def get(self, callback):
        if time.time() > self.expire and self.fetching is False:
            self.fetching = True
            return self.get_job(callback)
        else:
            return callback(self.builds)

    def get_job(self, callback):
        logging.info("Requesting jenkins/job/android")
        client = AsyncHTTPClient()
        return client.fetch("http://jenkins.cyanogenmod.com/job/android/api/json", functools.partial(self.get_job_cb, callback))

    def get_job_cb(self, callback, response):
        try:
            if response.error is not None:
                logging.error("Exception while fetching jenkins data")
                return callback(self.builds)
    
            data = json.loads(response.body)
    
            for build in data['builds']:
                build = (build['number'], build['url'])
                self.pool.append(build)
    
            self.pool = sorted(self.pool, key=lambda x: x[0], reverse=True)[:5]
            self.requests = len(self.pool)
    
            return self.process_pool(callback)
        except:
            return callback(self.builds)

    def process_pool(self, final_callback, response=None):
        try:
            if response:
                if response.error:
                    logging.error("Exception while fetching jenkins data")
                    return final_callback(self.builds)

                data = json.loads(response.body)
                if data['building'] is True:
                    build = {'number': data['number']}
                    for action in data['actions']:
                        if action.get('parameters'):
                            for param in action['parameters']:
                                if param['name'] == 'REPO_BRANCH':
                                    build['branch'] = param['value']
                                if param['name'] == 'RELEASE_TYPE':
                                    if param['value'] == 'CM_NIGHTLY':
                                        build['type'] = 'nightly'
                                    elif param['value'] == 'CM_SNAPSHOT':
                                        build['type'] = 'snapshot'
                                    else:
                                        build['type'] = param['value']
                                if param['name'] == 'LUNCH':
                                    match = re.match(r"(cm|cyanogen)_(.*)-(eng|userdebug)", param['value'])
                                    if match:
                                        build['lunch'] = match.groups()[1]
                                    else:
                                        build['lunch'] = param['value']
                    self.builds_tmp.append(build)

            if self.requests == 0:
                self.fetching = False
                self.builds = self.builds_tmp
                self.builds_tmp = []
                self.expire = time.time() + 300
                return final_callback(self.builds)

            build = self.pool.pop()
            self.requests -= 1
            url = build[1] + 'api/json'
            logging.info("Requesting %s", url)

            client = AsyncHTTPClient()
            client.fetch(url, functools.partial(self.process_pool, final_callback))
        except:
            return final_callback(self.builds)
