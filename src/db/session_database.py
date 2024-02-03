import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import make_url
from sqlalchemy_utils import database_exists, create_database


# engine1 = create_engine("postgresql://postgres:123@localhost/api_token")
# print('engine1')
# print(make_url("postgresql://postgres:123@localhost/api_token"))
# url = make_url("postgresql://postgres:123@localhost/")
# print(engine1.begin())
# engine1 = create_engine(url, )
# conn = engine1.begin()

# with engine1.begin() as conn:
#     text = "CREATE DATABASE api_token" 
    # text = "CREATE DATABASE {} ENCODING '{}' TEMPLATE {}".format(
        # quote(conn, 'api_token'),
        # 'api_token'
        # 'utf-8',
        # quote(conn, 'template1')
        # 'template1'
    # )
    # print('text')
    # print(text)
    # conn.execute(sa.text(text))
# conn = engine1.connect()

# conn.execute("create database api_token")
DATABASE_URL = "postgresql://postgres:123@localhost/api_token"
engine = create_engine(DATABASE_URL, echo=True)
print('adasdasdasdasdasdasd')
print(f"database_exists(engine.url) --> {database_exists(engine.url)}")
if not database_exists(engine.url):
    create_database(engine.url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_session():
    return SessionLocal()

def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()

