from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import FastAPI, APIRouter, Depends, Response, HTTPException
from http_exceptions import COUNTRIE_NOT_FOUND, CREDENTIALS_EXCEPTION
from db.session_database import Base, engine, get_db
from token_functions import SECRET_KEY, ALGORITHM
from jose import JWTError, jwt
from db.user_db import get_only_user
from typing_extensions import Annotated
from schemas.user import User

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = HTTPBearer()

def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme), database: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        login = payload.get("sub")
        print("login")
        print(login)
        if login is None:
            raise CREDENTIALS_EXCEPTION
        token_data = login
    except JWTError:
        raise CREDENTIALS_EXCEPTION
    user = get_only_user(login, database)
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user

def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user is None:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def is_admin(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    print("token.credentials")
    print(token)
    access_token = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    administrator = access_token.get("is_administrator")
    print("administrator")
    print(administrator)
    if not administrator:
        raise CREDENTIALS_EXCEPTION
    return administrator