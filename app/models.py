from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy.orm import mapped_column, Mapped
from app.auth.database import Base

metadata_obj = MetaData()

class User(Base):
    __tablename__ = "u"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)

