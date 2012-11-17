import os
import hashlib
from getcm import cache

def static_url(path):
    path = path.lstrip("/")
    cache_key = 'static_hash_%s' % path
    result = cache.get(cache_key)
    if result is not None:
        return "/static/%s?v=%s" % (path, result)
    else:
        try:
            static_path = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "static"))
            f = open(os.path.join(static_path, path))
            f_hash = hashlib.md5(f.read()).hexdigest()[:5]
            cache.set(cache_key, f_hash, expiry=3600)
            return "/static/%s?v=%s" % (path, f_hash)
        except:
            return "/static/%s" % path
