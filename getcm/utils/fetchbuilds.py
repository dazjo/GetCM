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

        if data['result'] != 'SUCCESS':
            return None

        waituntil = datetime.fromtimestamp((data['timestamp'] + data['duration']) / 1000 + 10 * 60)
        now = datetime.fromtimestamp(int(time.time()))
        if waituntil > now:
            print("Build %s: [%s > %s] Must wait 10 minutes before exposing build to fix hacky race condition" % (build['number'], waituntil, now))
            return None
        else:
            print("Build %s: Completed at %s, it is now %s.  Proceeding" % (build['number'], waituntil, now))

        result = []
        for artifact in data['artifacts']:
            if artifact['displayPath'].endswith(".zip") or artifact['displayPath'].endswith("CHANGES.txt") or artifact['displayPath'].endswith("build.prop"):  # and "NIGHTLY" in artifact['displayPath'] or "SNAPSHOT" in artifact['displayPath'] or "EXPERIMENTAL" in artifact['displayPath']:
                url = "http://jenkins.cyanogenmod.com/job/android/%s/artifact/archive/%s" % (build['number'], artifact['displayPath'])
                timestamp = (data['timestamp'] + data['duration']) / 1000
                result.append((url, timestamp))
        return result

    def run(self):
        for build in self.get_builds():
            artifactlist = self.get_artifact(build)
            if artifactlist:
                if os.path.exists("/opt/www/mirror/jenkins/%s" % artifactlist[0][0].split("/")[5]):
                    print "Exists, skipping."
                    continue
                for artifactdata in artifactlist:
                    artifact, timestamp = artifactdata
                    full_path = "jenkins/%s/%s" % (artifact.split("/")[5], artifact.split("/")[-1])
                    fileobj = File.get_by_fullpath(full_path)
                    if not fileobj:
                        base = "artifacts/%s" % artifact.replace("http://jenkins.cyanogenmod.com/job/android/", "")
                        build_number = base.split("/")[1]
                        fname = base.split("/")[-1]
                        build_type = "stable"
                        if "NIGHTLY" in artifact:
                            build_type = "nightly"
                        if "SNAPSHOT" in artifact:
                            #build_type = "snapshot"
                            build_type = "nightly"
                        if "EXPERIMENTAL" in artifact:
                            if "-M" in artifact:
                                build_type = "snapshot"
                            else:
                                build_type = "test"
                        if "-RC" in artifact:
                            build_type = "RC"
                        try:
                            os.mkdir("/opt/www/mirror/jenkins/%s" % build_number)
                        except:
                            pass
                        download_cmd = "wget -O /opt/www/mirror/jenkins/%s/%s %s" % (build_number, fname, artifact)

                        # Only download CHANGES.txt and build.prop locally
                        if not fname.endswith(".zip"):
                            print "Running: %s" % download_cmd
                            os.system(download_cmd)

                        # Download all artifacts to the mirror
                        mirror_cmd = "ssh -p2200 root@mirror.sea.tdrevolution.net \"/root/add.sh /srv/mirror/jenkins/%s %s %s\"" % (build_number, artifact, fname)
                        print "Running: %s" % mirror_cmd
                        os.system(mirror_cmd)

                        # Run the build.prop through getcm.addfile
                        if fname.endswith(".zip"):
                            addfile_cmd = "/usr/local/bin/getcm.addfile --timestamp %s --file /opt/www/mirror/jenkins/%s/%s --fullpath jenkins/%s/%s --type %s --config %s" % (timestamp, build_number, fname, build_number, fname, build_type, self.configPath)
                            print "Running: %s" % addfile_cmd
                            os.system(addfile_cmd)
            #break


def main():
    print("==================================")
    print("Starting getcm.fetchbuilds at %s" % datetime.now())
    fb = FetchBuild()
    fb.run()
