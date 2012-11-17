import time
import logging

from getcm.model import DBSession


class Cache(object):
    def __init__(self):
        self.store = {}

    def get(self, key):
        value, expires = self.store.get(key, (None, None))
        if expires is not None and expires > time.time():
            logging.info("Cache Hit for '%s', expires in %s seconds" % (key, expires - time.time()))
            return value
        else:
            if value is not None:
                if isinstance(value, list):
                    for obj in value:
                        try:
                            DBSession().expunge(obj)
                            logging.info("Expunged %s", obj)
                        except:
                            pass

            logging.info("Cache Miss for '%s'" % (key))
            return None

    def set(self, key, value):
        expires = time.time() + 600
        self.store[key] = (value, expires)
        return value
