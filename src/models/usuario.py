from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from ..db.session_database import Base

class Usuario(Base):
    __tablename__="usuario"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True)
    password = Column(String)
    name = Column(String)
    administrator = Column(Boolean)