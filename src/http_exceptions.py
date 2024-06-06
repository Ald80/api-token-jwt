from http import HTTPStatus
from fastapi import HTTPException

CREDENTIALS_EXCEPTION = HTTPException(
                            status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Could not validate credentials",
                            headers={"WWW-Authenticate": "Bearer"})


COUNTRIE_NOT_FOUND = HTTPException(
                        status_code=HTTPStatus.NOT_FOUND, 
                        detail="Pais not found.", 
                        headers={"WWW-Authenticate": "Bearer"})