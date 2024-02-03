from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError

# Configuração do banco de dados
DATABASE_URL = "postgresql://postgres:123@localhost/postgres"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# https://chat.openai.com/c/7bdf2a4f-e30e-491f-9689-7cffa7c5fc17
# Modelo do banco de dados
Base = declarative_base()

app = FastAPI()

class Item(Base):
    __tablename__="items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

Base.metadata.create_all(bind=engine)

def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inserir dados iniciais no banco de dados
def insert_initial_data():
    database = SessionLocal()
    # database = get_databas()
    try:
        items = database.query(Item).all()
        print('items sql .... ')
        print(items)
        if not items:
            item1 = Item(name="Item 1", description="Description for Item 1")
            item2 = Item(name="Item 2", description="Description for Item 2")
            database.add(item1)
            database.add(item2)
            database.commit()
    except IntegrityError:
        database.rollback()
    finally:
        database.close()


@app.on_event("startup")
async def startup_event(db: Session = get_database()):
    # db_generator = get_database()
    db = next(db)
    insert_initial_data()
    # db_generator.close()

@app.get("/items/")
async def read_items(db: Session = Depends(get_database)):
    return db.query(Item).all()