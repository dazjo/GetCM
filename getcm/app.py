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

from model import DBSession, init_database
from handlers import BrowseHandler, RssHandler, SumHandler, ZipHandler, Base62Handler, ApiHandler, MirrorApplicationHandler
from getcm.utils import WeightedChoice

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
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "static")}),
        ]
        
        settings = dict(
            debug=options.debug,
        )
        super(Application, self).__init__(handlers, **settings)

        config = ConfigParser()
        config.readfp(open(options.config))

        # One global connection
        init_database(create_engine(config.get('database', 'uri')))
        self.db = DBSession
        template_path = os.path.join(os.path.dirname(__file__), "templates")
        self.lookup = TemplateLookup(directories=[template_path], filesystem_checks = False)

        self.mirrorpool = WeightedChoice((
            ('http://oss.reflected.net/%s', 1000),
            ('http://mirror.symnds.com/software/cm/%s', 1000),
            ('http://mirror.netcologne.de/cyanogenmod/%s', 200),
            #('http://mirror.sea.tdrevolution.net/%s', 50),
            ('http://cm.sponsored.cb-webhosting.de/%s', 25),
            ('http://mirror.i3d.net/pub/cyanogenmod/%s', 50),
        ))

def run_server():
    # Define command line options
    define('config', default='/etc/getcm.ini', type=unicode, help="Path to configuration file")
    tornado.options.parse_command_line()
    app = Application()

    server = tornado.httpserver.HTTPServer(app, xheaders=True)
    server.listen(int(options.port))
    IOLoop.instance().start()

if __name__ == '__main__':
    run_server()
