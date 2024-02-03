from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from ..db.session_database import Base

class Token(Base):
    __tablename__="token"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String)
    login = Column(String)
    expiration = Column(DateTime(), server_default=func.now())
    administrator = Column(Boolean)
