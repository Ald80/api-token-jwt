from sqlalchemy import create_engine, Column, Integer, String, DateTime
from ..db.session_database import Base

class Item(Base):
    __tablename__="item"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())