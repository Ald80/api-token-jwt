from fastapi import FastAPI, APIRouter, Depends, Response, HTTPException
# from session_database import

from passlib.context import CryptContext
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
# from db.user_db import get_only_user

# from http_exceptions import COUNTRIE_NOT_FOUND, CREDENTIALS_EXCEPTION
import http_exceptions
def generate_secret_key():
    return b64encode(token_bytes(64)).decode()

SECRET_KEY = generate_secret_key()
SECRET_REFRESH_KEY = generate_secret_key()
print("SECRET_KEY")
print(SECRET_KEY)
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 0.5
REFRESH_TOKEN_EXPIRE_MINUTES = 30*60
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=5)
    print("expire")
    print(expire)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_REFRESH_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def renew_token_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    try:
        refresh_token = jwt.decode(token.credentials, SECRET_REFRESH_KEY, algorithms=[ALGORITHM])
        login = refresh_token.get("sub")
        is_administrator = refresh_token.get("is_administrator")
        if login is None:
            raise http_exceptions.CREDENTIALS_EXCEPTION
        token_data = {"sub": login, "is_administrator": is_administrator}
    except Exception as e:
        raise e
    return token_data

# def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], database: Session = Depends(get_db)):
# def verify_refresh_token(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
#     print("token")
#     print(token)

#     try:
#         print("inside try")
#         print("SECRET_KEY")
#         print(SECRET_KEY)
#         access_token = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
#         print('access_token')
#         print(access_token)
#         login = access_token.get("sub")
#         print("access_token")
#         print(access_token)
#         print("login")
#         print(login)
#         if login is None:
#             raise http_exceptions.CREDENTIALS_EXCEPTION
#         token_data = login
#     except Exception as e:
#         raise e
#         # raise http_exceptions.CREDENTIALS_EXCEPTION
    
#     return token_data

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(password, user_passaword):
    # hashed_password = get_password_hash(password)
    return pwd_context.verify(password, user_passaword)
