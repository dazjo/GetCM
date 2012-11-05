import argparse
import logging
import time
import os
import tornado.web
import tornado.httpserver
import tornado.options

from ConfigParser import ConfigParser
from tornado.options import define, options
from tornado.ioloop import IOLoop
from sqlalchemy import create_engine
from mako.template import Template
from mako.lookup import TemplateLookup

from model import DBSession, init_database, ActiveBuilds
from handlers import BrowseHandler, RssHandler, SumHandler, ZipHandler, Base62Handler, ApiHandler, MirrorApplicationHandler
from getcm.utils import WeightedChoice
from getcm.stats import Stats

define('port', 6543)
define('debug', True)

logging.basicConfig(level=logging.DEBUG)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", BrowseHandler),
            (r"/get/(.*)\.md5sum", SumHandler),
            (r"/get/(.*)\.zip", ZipHandler),
            (r"/get/(.*/CHANGES.txt)", tornado.web.StaticFileHandler, {"path": "/opt/www/mirror"}),
            (r"/get/(.*)", Base62Handler),
            (r"/rss", RssHandler),
            (r"/api", ApiHandler),
            (r"/mirror", MirrorApplicationHandler),
        ]

        settings = dict(
            debug=options.debug
        )
        super(Application, self).__init__(handlers, **settings)

        config = ConfigParser()
        config.readfp(open(options.config))

        # One global connection
        init_database(create_engine(config.get('database', 'uri')))
        self.db = DBSession
        template_path = os.path.join(os.path.dirname(__file__), "templates")
        self.lookup = TemplateLookup(directories=[template_path])
        self.activebuilds = ActiveBuilds()
        self.devicedict = {}
        #self.stats = Stats()

        self.mirrorpool = WeightedChoice((
            ('http://oss.reflected.net/%s', 1000),
            ('http://mirror.sea.tdrevolution.net/%s', 500),
            ('http://cm.sponsored.cb-webhosting.de/%s', 50),
            ('http://mirror.netcologne.de/cyanogenmod/%s', 75),
        ))

def run_server():
    parser = argparse.ArgumentParser(description="get.cm server")
    parser.add_argument('--port', dest='port', type=int, help='Port')
    parser.add_argument('--config', dest='config', type=unicode, help="Path to configuration file", default="/etc/getcm.ini")
    parser.add_argument('--logging', dest='logging', type=unicode, help="Logging level", choices=['debug', 'info', 'warning', 'error', 'none'], default='debug')
    args = parser.parse_args()

    define('settings', '')
    options.logging = args.logging
    options.port = args.port
    options.config = args.config
    server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    server.listen(int(options.port))
    IOLoop.instance().start()

if __name__ == '__main__':
    run_server()
