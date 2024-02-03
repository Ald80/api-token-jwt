from sqlalchemy import create_engine, Column, Integer, String, DateTime
from ..db.session_database import Base

class Pais(Base):
    __tablename__="pais"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    acronym = Column(String, unique=True)
    gentile = Column(String, unique=True)