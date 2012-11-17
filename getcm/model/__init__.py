from getcm.model.base import AbstractTable
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import sessionmaker

DBSession = scoped_session(sessionmaker())
Base = declarative_base(cls=AbstractTable)

def init_database(engine):
    DBSession.configure(bind=engine)
    __import__("getcm.model.schema", globals(), locals(), ["*"]) 
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
