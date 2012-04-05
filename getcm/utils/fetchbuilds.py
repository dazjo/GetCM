import os
import time
import sys
import urllib2
import json
from sqlalchemy import create_engine
from ConfigParser import ConfigParser
from datetime import datetime

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

        waituntil = datetime.fromtimestamp((data['timestamp'] + data['duration'])/1000 + 10*60)
        now = datetime.fromtimestamp(int(time.time()))
        if waituntil > now:
            print("Build %s: [%s > %s] Must wait 10 minutes before exposing build to fix hacky race condition" % (build['number'], waituntil, now))
            return None
        else:
            print("Build %s: Completed at %s, it is now %s.  Proceeding" % (build['number'], waituntil, now))

        for artifact in data['artifacts']:
            if artifact['displayPath'].endswith(".zip") and "NIGHTLY" in artifact['displayPath']:
                url = "http://jenkins.cyanogenmod.com/job/android/%s/artifact/archive/%s" % (build['number'], artifact['displayPath'])
                timestamp = (data['timestamp'] + data['duration'])/1000
                return (url, timestamp)

    def run(self):
        for build in self.get_builds():
            artifactdata = self.get_artifact(build)
            if artifactdata:
                artifact, timestamp = artifactdata
                full_path = artifact.replace("http://jenkins.cyanogenmod.com/job/android","artifacts")
                fileobj = File.get_by_fullpath(full_path)
                if not fileobj:
                    base = "artifacts/%s" % artifact.replace("http://jenkins.cyanogenmod.com/job/android/", "")
                    cmd = "getcm.addfile --timestamp %s --url %s --fullpath %s --type nightly --config %s" % (timestamp, artifact, base, self.configPath)
                    print "Running: %s" % cmd
                    os.system(cmd)


def main():
    print("==================================")
    print("Starting getcm.fetchbuilds at %s" % datetime.now())
    fb = FetchBuild()
    fb.run()
