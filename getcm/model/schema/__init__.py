from getcm import cache
from getcm.model import Base, DBSession
from getcm.utils.string import convert_bytes, base62_decode
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.util import join
from sqlalchemy.sql.expression import func

class File(Base):
    __tablename__ = "files"

    id = Column('id', Integer, primary_key=True)
    filename = Column('filename', String(255))
    size = Column('size', Integer)
    full_path = Column('full_path', String(255))
    md5sum = Column('md5sum', String(32), unique=True)
    info_hash = Column('info_hash', String(50))

    device = Column('device', String(100), index=True)
    type = Column('type', String(20), index=True)

    date_created = Column(DateTime, default=func.now())
    date_updated = Column(DateTime, default=func.now(), onupdate=func.now())

    @property
    def human_size(self):
        return convert_bytes(self.size)

    @classmethod
    def get_by_filename(cls, filename):
        cache_key = "get_by_filename_%s" % filename
        def get_from_database():
            session = DBSession()
            try:
                file = session.query(cls).filter(cls.filename == filename).order_by(cls.id.desc()).first()
            except NoResultFound:
                file = None

            return file

        result = cache.get(cache_key)
        if result is None:
            result = cache.set(cache_key, get_from_database())

        return result

    @classmethod
    def get_by_fullpath(cls, filename):
        cache_key = "get_by_fullpath_%s" % filename

        def get_from_database():
            session = DBSession()
            try:
                file = session.query(cls).filter(cls.full_path == filename).order_by(cls.id.desc()).first()
            except NoResultFound:
                file = None

            return file

        result = cache.get(cache_key)
        if result is None:
            result = cache.set(cache_key, get_from_database())

        return result

    @classmethod
    def get_by_base62(cls, base62):
        cache_key = "get_by_base62_%s" % base62
        def get_from_database():
            session = DBSession()
            try:
                file = session.query(cls).filter(cls.id == base62_decode(base62)).one()
            except NoResultFound:
                file = None

            return file

        result = cache.get(cache_key)
        if result is None:
            result = cache.set(cache_key, get_from_database())

        return result

    @classmethod
    def get_by_md5sum(cls, md5hash):
        cache_key = "get_by_md5sum:%s" % md5hash
        def get_from_database():
            session = DBSession()
            try:
                file = session.query(cls).filter(cls.md5sum == md5hash).one()
            except NoResultFound:
                file = None

            return file

        result = cache.get(cache_key)
        if result is None:
            result = cache.set(cache_key, get_from_database())

        return result


    @classmethod
    def browse(cls, device, type, limit=50):
        cache_key = "%s_%s_%s" % (device or "null", type or "null", limit)

        def get_from_database():
            session = DBSession()
            query = session.query(cls)

            if device is not None:
                query = query.select_from(File).filter(File.device == device)

            if type is not None:
                query = query.filter(cls.type == type)

            # Limit the query and order it
            query = query.order_by(cls.id.desc())[:limit]

            return query

        result = cache.get(cache_key)
        if result is None:
            result = cache.set(cache_key, get_from_database())
        
        return result

class Device(object):
    @classmethod
    def get_all(cls):
        cache_key = "all_the_things"

        def get_from_database():
            devices = []

            session = DBSession()
            for device in session.query(File.device).distinct():
                devices.append(device[0])

            return sorted(devices)

        result = cache.get(cache_key)
        if result is None:
            result = cache.set(cache_key, get_from_database())

        return result
