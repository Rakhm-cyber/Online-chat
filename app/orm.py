from sqlalchemy import text, insert
from app.models import User, metadata_obj
from app.auth.database import sync_engine, async_engine, session_factory, Base

def create_tables():
    sync_engine.echo = True
    Base.metadata.drop_all(sync_engine)
    Base.metadata.create_all(sync_engine)

def insert_data():
    with session_factory() as session:
        qwera = User(username="говно", password="123")
        session.add(qwera)
        session.commit()
