import os
import time
import sys
import urllib2
import json
from sqlalchemy import create_engine
from ConfigParser import ConfigParser

from getcm.model import init_database, DBSession
from getcm.model.schema import File

class FetchBuild(object):
    def __init__(self):
        if len(sys.argv) == 2:
            self.configPath = sys.argv[1]
        else:
            self.configPath = "/etc/getcm.ini"

        config = ConfigParser() 
        config.readfp(open(self.configPath, 'r'))
        init_database(create_engine(config.get('database', 'uri')))

    def get_builds(self):
        url = "http://jenkins.cyanogenmod.com/job/android/api/json"
        data = urllib2.urlopen(url).read()
        data = json.loads(data)

        return data['builds']

    def get_artifact(self, build):
        url = build['url'] + "api/json"
        data = urllib2.urlopen(url).read()
        data = json.loads(data)

        if data['building'] or data['duration'] == 0:
            return None

        if (data['timestamp'] + data['duration'] + 10 * 60 * 1000) > (time.time() * 1000):
            print("Build %s: Must wait 10 minutes before exposing build to fix hacky race condition" % build['number'])
            return None

        for artifact in data['artifacts']:
            if artifact['displayPath'].endswith(".zip") and "NIGHTLY" in artifact['displayPath']:
                return "http://jenkins.cyanogenmod.com/job/android/%s/artifact/archive/%s" % (build['number'], artifact['displayPath'])

    def run(self):
        for build in self.get_builds():
            artifact = self.get_artifact(build)
            if artifact:
                fileobj = File.get_by_filename(os.path.basename(artifact))
                if not fileobj:
                    base = "artifacts/%s" % artifact.replace("http://jenkins.cyanogenmod.com/job/android/", "")
                    cmd = "getcm.addfile --url %s --fullpath %s --type nightly --config %s" % (artifact, base, self.configPath)
                    print "Running: %s" % cmd
                    os.system(cmd)


def main():
    fb = FetchBuild()
    fb.run()
