from fastapi import FastAPI, APIRouter, Depends, Response, HTTPException
# from session_database import
from fastapi.responses import JSONResponse
from .db.session_database import Base, engine, get_db
from sqlalchemy.orm import Session
from .db.migration_data import insert_initial_data
from .models.pais import Pais
from .models.usuario import Usuario
from .schemas.pais import PaisScheme
from .schemas.usuario_atenticado import UsuarioAtenticado
from .schemas.login import OAuth2Form
from typing_extensions import Annotated
from sqlalchemy import func, delete
import json
from passlib.context import CryptContext
from pydantic import BaseModel
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from secrets import token_bytes
from base64 import b64encode
from http import HTTPStatus
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from dataclasses import dataclass
from fastapi.security.http import HTTPAuthorizationCredentials

# router = APIRouter('')

class User(BaseModel):
    login: str
    password: str
    name: str | None = None
    administrator: bool | None = None
    
def generate_secret_key():
    return b64encode(token_bytes(64)).decode()

# global SECRET_KEY
SECRET_KEY = generate_secret_key()
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 5


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
oauth2_scheme = HTTPBearer()

app = FastAPI()

Base.metadata.create_all(bind=engine)

class Token(BaseModel):
    access_token: str
    token_type: str

@app.on_event("startup")
async def startup_event(db: Session = get_db()):
    db = next(db)
    insert_initial_data()

@app.get('/a')
def get_app():
    return {"msg": "Hello"}


def get_only_user(login: str, database: Session):
    user = database.query(Usuario) \
                .filter_by(login = Usuario.login).first()
    return user

def get_user_password(login: str, password: str, database: Session):
    login_user = database.query(Usuario) \
                    .filter_by(login = Usuario.login,
                               password = Usuario.password).first()
    return login_user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    # SECRET_KEY = generate_secret_key()
    print("SECRET_KEY ... ")
    print(SECRET_KEY)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print("encoded_jwt")
    print(encoded_jwt)
    return encoded_jwt

# def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], database: Session = Depends(get_db)):
def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme), database: Session = Depends(get_db)):
    print("inside here ... ")
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        print("token")
        print(token.credentials)
        print("SECRET_KEY")
        print(SECRET_KEY)
        print("ALGORITHM")
        print(ALGORITHM)
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        print("login")
        print(login)
        if login is None:
            raise credentials_exception
        # token_data = login
    except JWTError:
        raise credentials_exception
    user = get_only_user(login, database)
    if user is None:
        raise credentials_exception
    return user

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(password):
    hashed_password = get_password_hash(password)
    return pwd_context.verify(password, hashed_password)

def authenticate_user(login: str, password: str, database: Session):
    user = get_user_password(login, password, database)
    if not user:
        return False
    if not verify_password(password):
        return False
    return user

def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    print("inside get_current_active_user")
    if current_user is None:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post('/login')
def login_user(form_data: Annotated[OAuth2Form, Depends()]
               , database: Session = Depends(get_db)
               ):
    # login_user = database.query(Usuario) \
                # .filter_by(form_data.login == Usuario.login,
                        #    form_data.password == Usuario.password).first()
    user = authenticate_user(form_data.login, form_data.password, database)
    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Incorrect login or password",
                            headers={"WWW-Authenticate": "Bearer"})
    access_token_expire = timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.login}, expires_delta=access_token_expire)
    # return login_user
    # return JSONResponse(content={"access_token": access_token, "token_type": "bearer"}, headers={"Authorization": f"Bearer {access_token}"})
    return Token(access_token=access_token, token_type="bearer")

@app.get('/list-countries', response_model=list[PaisScheme])
def get_countries(
    _: Annotated[User, Depends(get_current_active_user)],
    database: Session = Depends(get_db)):
    print("iiiiiiiiiiiii")
    countries = database.query(Pais).all()
    print("wwwwwwwwwwwwwwwwwwwwwwwwwwww")
    print("countries")
    # countries = [countrie for countrie in countries]
    print(countries)
    countries = [
        {"id": countrie.id, 
         "name": countrie.name, 
         "acronym": countrie.acronym,
         "gentile": countrie.gentile
         } for countrie in countries ]
    return JSONResponse(content=countries, status_code=200)
    # return countries
    # return Response(content=countries, status_code=200)

@app.get('/search-contrie/{name}', response_model=list[PaisScheme])
def get_countrie(name: str, database: Session = Depends(get_db)):
    
    # countrie = database.query(Pais).filter(Pais.name.like(f"%{name}%")).all()
    countries = database.query(Pais).filter(func.lower(Pais.name).like(f"%{name.lower()}%")).all()
    # print(func.lower(Pais.name))
    # print(name.lower())
    # print("countrie")
    # print(countrie)
    return countries

@app.post('/save-contrie')
def save_contrie(paisScheme: PaisScheme, database: Session = Depends(get_db)):
    pais_db = Pais(
        name=paisScheme.name,
        acronym=paisScheme.acronym,
        gentile=paisScheme.gentile,
    )
    database.add(pais_db)
    database.commit()
    database.refresh(pais_db)
    database.close()
    return paisScheme

@app.delete('/delete-contrie/{pais_id}')
def delete_countrie(pais_id: int, database: Session = Depends(get_db)):
    pais_db = database.query(Pais).filter(Pais.id == pais_id).first()
    if not pais_db:
        raise HTTPException(status_code=404, detail="Pais not found.")
    # delete_stmt = delete(Pais).where(Pais.id == pais_id)
    # print(pais_id)
    # print(delete_stmt)
    
    # database.delete(Pais).where(Pais.id == pais_id)
    database.query(Pais).filter(Pais.id == pais_id).delete()
    database.commit()
    return pais_id
    # return None
    # https://docs.sqlalchemy.org/en/20/tutorial/data_update.html