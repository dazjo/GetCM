import time
import logging
import socket
import pickle
import struct

from tornado.ioloop import IOLoop, PeriodicCallback

class Stats(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("bacon.cyanogenmod.com", 2004))
        self.store = {}

        # Register with the main IOLoop
        self.scheduler = PeriodicCallback(self.flush, 10000, IOLoop.instance())
        self.scheduler.start()

    def incr(self, key, value=1):
        ts = int(time.time())

        if self.store.get(key, None) is None:
            self.store[key] = {}

        if self.store[key].get(ts, None) is None:
            self.store[key][ts] = 0

        self.store[key][ts] += value
        logging.debug("Stats:incr %s %s", key, ts)

    def flush(self):
        data = []

        for k,v in self.store.iteritems():
            for ik,iv in v.iteritems():
                data.append(('test.getcm.%s' % k, (ik, iv)))

        if len(data) == 0:
            return

        logging.debug("Stats:flush %s", data)
        
        payload = pickle.dumps(data)
        message = struct.pack('!L', len(payload)) + payload
        
        try:
            self.sock.send(message)
        except Exception, e:
            print e

        self.store = {}
