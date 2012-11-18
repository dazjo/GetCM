import binascii
import hashlib
import sys
import os
import re
import math
import time
import urllib
from xml.sax.saxutils import escape

verbose = False
generator = "DoucheTorrent 0.1"


class Metafile(object):
    def __init__(self):
        self.hashes = Hashes()
        self.reset()

    def scan_file(self, filename, use_chunks=True, max_chunks=255, chunk_size=256, progresslistener=None):
        if verbose:
            print "Scanning file..."
        # Filename and size
        self.filename = os.path.basename(filename)
        if not self.hashes.filename:
            self.hashes.filename = self.filename
        size = os.stat(filename).st_size
        self.size = str(size)

        # Force maximum size for piece checksums to 512 KiB:
        # http://en.wikipedia.org/wiki/BitTorrent_(protocol)#Creating_and_publishing_torrents
        maxlength = 524288
        # Calculate piece length
        if use_chunks:
            minlength = chunk_size * 1024
            self.hashes.piecelength = 1024
            while self.hashes.piecelength < maxlength and (size / self.hashes.piecelength > max_chunks or self.hashes.piecelength <= minlength):
                self.hashes.piecelength *= 2
            if verbose:
                print "Using piecelength", self.hashes.piecelength, "(" + str(self.hashes.piecelength / 1024) + " KiB)"
            numpieces = size / self.hashes.piecelength
            if numpieces < 2:
                use_chunks = False
        hashes = {}
        hashes['sha1'] = hashlib.sha1()
        sha1hash_copy = hashes['sha1'].copy()
        piecehash = sha1hash_copy.copy()
        piecenum = 0
        length = 0

        # TODO: Don't calculate pieces if already known
        self.hashes.pieces = []
        if not self.hashes.piecetype:
            self.hashes.piecetype = "sha1"

        num_reads = math.ceil(size / 4096.0)
        reads_per_progress = int(math.ceil(num_reads / 100.0))
        reads_left = reads_per_progress
        progress = 0
        fp = open(filename, "rb")
        while True:
            data = fp.read(4096)
            if data == "":
                break
            # Progress updating
            if progresslistener:
                reads_left -= 1
                if reads_left <= 0:
                    reads_left = reads_per_progress
                    progress += 1
                    result = progresslistener.Update(progress)
                    if get_first(result) is False:
                        if verbose:
                            print "Cancelling scan!"
                        return False
            # Process the data
            left = len(data)
            while use_chunks and left > 0:
                if length + left <= self.hashes.piecelength:
                    piecehash.update(data)
                    length += left
                    left = 0
                else:
                    numbytes = self.hashes.piecelength - length
                    piecehash.update(data[:numbytes])
                    length = self.hashes.piecelength
                    data = data[numbytes:]
                    left -= numbytes
                if length == self.hashes.piecelength:
                    if verbose:
                        print "Done with piece hash", len(self.hashes.pieces)
                    self.hashes.pieces.append(piecehash.hexdigest())
                    piecehash = sha1hash_copy.copy()
                    length = 0
        if use_chunks:
            if length > 0:
                if verbose:
                    print "Done with piece hash", len(self.hashes.pieces)
                self.hashes.pieces.append(piecehash.hexdigest())
            if verbose:
                print "Total number of pieces:", len(self.hashes.pieces)
        fp.close()

        # Convert to string
        self.hashes.piecelength = str(self.hashes.piecelength)
        if verbose:
            print "done"
        if progresslistener:
            progresslistener.Update(100)
        return True

    def reset(self):
        """Reset mutable attributes to allow object reuse"""
        self.changelog = ""
        self.description = ""
        self.filename = ""
        self.identity = ""
        self.language = ""
        self.logo = ""
        self.maxconn_total = ""
        self.mimetype = ""
        self.os = ""
        self.releasedate = ""
        self.screenshot = ""
        self.signature = ""
        self.signature_type = ""
        self.size = ""
        self.tags = []
        self.upgrade = ""
        self.version = ""
        self.resources = []
        self.urls = []
        self.errors = []

        self.hashes.reset()


class Hashes(object):
    def __init__(self, filename='', url=''):
        self.reset(filename, url)

    def init(self):
        self.pieces = []
        self.hashes = {}

    def reset(self, filename='', url=''):
        """Reset mutable attributes to allow object reuse"""
        self.filename = ''
        self.filename_absolute = ''
        self.url = url
        self.hashes = {}
        self.init()
        self.last_hash_file = ''
        self.pieces = []
        self.piecelength = 0
        self.piecetype = ''
        self.files = []


class Metalink(object):
    def __init__(self, overwrite_with_opts=True):
        self.hashes = Hashes()
        self.file = Metafile()

        self.reset(overwrite_with_opts)

    def create_torrent(self, torrent, full_path):
        t = Torrent(torrent)
        fn = os.path.basename(full_path)
        data = {'comment': encode_text(self.description), 'files': [[encode_text(fn), int(self.file.size)]], 'piece length': int(self.file.hashes.piecelength), 'pieces': self.file.hashes.pieces, 'created by': generator, 'encoding': 'UTF-8'}
        return t.create(data, full_path)

    def scan_file(self, filename, use_chunks=True, max_chunks=255, chunk_size=256, progresslistener=None):
        self.filename_absolute = filename
        return self.file.scan_file(filename, use_chunks, max_chunks, chunk_size, progresslistener)

    def reset(self, overwrite_with_opts=True):
        """Reset mutable attributes to allow object reuse"""
        self.changelog = ""
        self.copyright = ""
        self.description = ""
        self.filename_absolute = ""
        self.generator = ""
        self.identity = ""
        self.license_name = ""
        self.license_url = ""
        self.logo = ""
        self.origin = ""
        self.pubdate = ""
        self.publisher_name = ""
        self.publisher_url = ""
        self.refreshdate = ""
        self.releasedate = ""
        self.screenshot = ""
        self.tags = []
        self.type = ""
        self.upgrade = ""
        self.version = ""
        self.resources = []
        self.signature = ""
        self.signature_type = ""
        self.size = ""
        self.urls = []

        self.errors = []
        self.url_prefix = ''
        self._valid = True

        self.hashes.reset()
        self.file.reset()
        # For multi-file torrent data
        self.files = [self.file]


class Torrent(object):
    def __init__(self, filename='', url=''):
        self.filename = filename
        self.url = url
        self.comment = ''
        self.files = []
        self.infohash = ''
        self.piecelength = 0
        self.pieces = []

    def encode_pieces(self, pieces):
        if isinstance(pieces, list) and len(pieces):
            return "".join([binascii.unhexlify(piece) for piece in pieces])
        return ''

    def create(self, data, full_path):
        trackers = [["http://bacon.cyanogenmod.com:6969/announce"], ["udp://tracker.openbittorrent.com:80/announce"]]

        # Create torrent
        root = {}
        for key in 'created by,comment'.split(','):
            if key in data and len(data[key]) > 2:
                root[key] = encode_text(data[key])

        root['announce'] = trackers[0][0]
        if len(trackers) > 1 or len(trackers[0]) > 1:
            root['announce-list'] = trackers

        # At the moment only single-file torrents can be created because of missing pieces hashing for multi-file torrents
        # Multiple-file torrents may contain subdirectories (so no basename!)
        root['info'] = {}
        file = data['files'][0]
        root['info']['name'] = encode_text(os.path.basename(full_path))
        root['info']['length'] = file[1]
        root['info']['piece length'] = data['piece length']
        root['info']['pieces'] = self.encode_pieces(data['pieces'])

        root['creation date'] = int(time.time())
        root['url-list'] = ["http://getcm.thebronasium.com/get/%s?webseed=1" % full_path]

        self.data = self.bencode(root)
        self.pos = 0

        file = self.filename
        fp = open(file, "wb")
        fp.write(self.data)
        fp.close()

        self.bdecode()
        return self.infohash

    def bdecode(self):
        c = self.data[self.pos]
        if 'd' == c:
            d = {}
            self.pos += 1
            while not self._is_end():
                start = self.pos + 6
                key = self._process_string()
                d[key] = self.bdecode()
                if not self.infohash and 'info' == key:
                    self.infohash = hashlib.sha1(self.data[start:self.pos]).hexdigest().upper()
            self.pos += 1
            return d
        elif c == 'l':
            l = []
            self.pos += 1
            while not self._is_end():
                l.append(self.bdecode())
            self.pos += 1
            return l
        elif c == 'i':
            self.pos += 1
            pos = self.data.find('e', self.pos)
            i = int(self.data[self.pos:pos])
            self.pos = pos + 1
            return i
        if c.isdigit():
            return self._process_string()
        raise TypeError('Invalid bencoded string')

    def _process_string(self):
        pos = self.data.find(':', self.pos)
        length = int(self.data[self.pos:pos])
        self.pos = pos + 1
        text = self.data[self.pos:self.pos + length]
        self.pos += length
        return text

    def _is_end(self):
        return self.data[self.pos] == 'e'

    def bencode(self, x):
        from cStringIO import StringIO
        s = StringIO()
        self._bencode_value(x, s)
        return s.getvalue()

    def _bencode_value(self, x, s):
        t = type(x)
        if t in (int, long, bool):
            s.write('i%de' % x)
        elif isinstance(x, basestring):
            s.write('%d:%s' % (len(x), x))
        elif t in (list, tuple):
            s.write('l')
            for e in x:
                self._bencode_value(e, s)
            s.write('e')
        elif t is dict:
            s.write('d')
            keys = x.keys()
            keys.sort()
            for k in keys:
                self._bencode_value(k, s)
                self._bencode_value(x[k], s)
            s.write('e')
        else:
            raise TypeError('Unsupported data type to bencode: %s' % t.__name__)


def encode_text(text, encoding='utf-8'):
    return text.decode(sys.getfilesystemencoding()).encode(encoding)


def create_torrent(path, output, full_path):
    m = Metalink()
    m.scan_file(path)
    infohash = m.create_torrent(output, full_path)
    print "%s	%s" % (os.path.basename(path), infohash)
    return infohash

if __name__ == '__main__':
    create_torrent(sys.argv[1], sys.argv[2])
