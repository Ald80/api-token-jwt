from typing import List, Literal
from fastapi import FastAPI, APIRouter, Depends, Response, HTTPException
from fastapi.responses import JSONResponse
from typing import Any
from models.usuario import Usuario
from db.session_database import Base, engine, get_db
from sqlalchemy.orm import Session
from db.migration_data import insert_initial_data
from schemas.pais import PaisScheme
from schemas.login import OAuth2Form
from typing_extensions import Annotated
from datetime import timedelta
from http import HTTPStatus
from fastapi.responses import JSONResponse
from fastapi.security.http import HTTPAuthorizationCredentials
from dataclasses import dataclass
# from src.db.user_db import authenticate_user
from db.user_db import authenticate_user, get_only_user
from db.countrie_db import (search_countrie, 
                             search_countrie_by_name, 
                             persist_countrie, 
                             remove_countrie,
                             search_countrie_by_id,
                             generate_list_of_dict_countries)
from schemas.user import User
from token_functions import (ACCESS_TOKEN_EXPIRE_MINUTES,
                             REFRESH_TOKEN_EXPIRE_MINUTES, 
                              create_access_token, 
                            #   verify_refresh_token,
                            create_refresh_token,
                            renew_token_user, 
                              oauth2_scheme)

from authentication import (get_current_active_user, 
                              is_admin,
                              get_current_user)
from jose import JWTError, jwt

from http_exceptions import COUNTRIE_NOT_FOUND

@dataclass
class Token:
    access_token: Any
    refresh_token :Any
    token_type: str

app = FastAPI()


Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup_event(db: Session = get_db()):
    db = next(db)
    insert_initial_data()


@app.post('/login')
def login_user(form_data: Annotated[OAuth2Form, Depends()]
               , database: Session = Depends(get_db)
               ):
    user: Usuario | Literal[False] = authenticate_user(form_data.login, form_data.password, database)
    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Incorrect login or password",
                            headers={"WWW-Authenticate": "Bearer"})
    access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expire = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token: str = create_access_token(data={"sub": user.login, "is_administrator": user.administrator}, expires_delta=access_token_expire)
    refresh_token = create_refresh_token(data={"sub": user.login, "is_administrator": user.administrator}, expires_delta=refresh_token_expire)
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@app.get('/renew_ticket')
# def refresh_token(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
# def refresh_token(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
def refresh_token(refresh_token: HTTPAuthorizationCredentials = Depends(oauth2_scheme), database: Session = Depends(get_db)):

    # print("token")
    # print(token)
    # token_data = create_refresh_token(token)
    access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # data = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    # access_token = create_refresh_token(data={"sub": token_data}, expires_delta=access_token_expire)
    token_data = renew_token_user(refresh_token)
    user: Usuario | Literal[False] = get_only_user(token_data["sub"], database)
    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Incorrect login",
                            headers={"WWW-Authenticate": "Bearer"})
    new_access_token: str = create_access_token(data=token_data, expires_delta=access_token_expire)
    print("renew token")
    print(token_data)
    
    return Token(access_token=new_access_token, refresh_token=refresh_token.credentials, token_type="bearer")
    # return access_token
    # print("Token(access_token=access_token, token_type='bearer'')")
    # print(Token(access_token=access_token, token_type="bearer"))
    # return Token(access_token=access_token, token_type="bearer")

@app.get('/list-countries', response_model=list[PaisScheme])
def get_countries(
    _: Annotated[User, Depends(get_current_active_user)],
    database: Session = Depends(get_db)) -> JSONResponse:
    countries: List = search_countrie(database)
    countries = generate_list_of_dict_countries(countries)
    return JSONResponse(content=countries, status_code=200)

@app.get('/search-contrie/{name}', response_model=list[PaisScheme])
def get_countrie(_: Annotated[User, Depends(get_current_active_user)], name: str, database: Session = Depends(get_db)):
    countrie = search_countrie_by_name(name, database)
    if not countrie:
        raise HTTPException(status_code=404, detail="contrie not found")
    return countrie

@app.post('/save-contrie')
def save_contrie(_: Annotated[User, Depends(get_current_active_user)], paisScheme: PaisScheme, database: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    # token_data = verify_refresh_token(token)
    if is_admin(token):
        try:
            countrie_persited = persist_countrie(paisScheme, database)
            return countrie_persited
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.delete('/delete-contrie/{pais_id}')
def delete_countrie(_: Annotated[User, Depends(get_current_active_user)], pais_id: int, database: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    if is_admin(token):
        pais_db = search_countrie_by_id(pais_id, database)
        if not pais_db:
            raise HTTPException(status_code=404, detail="country not found.")
        try:
            pais_id = remove_countrie(pais_id, database)
            return pais_id
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

