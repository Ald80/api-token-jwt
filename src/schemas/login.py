from fastapi.security import OAuth2PasswordRequestForm
from fastapi.param_functions import Form
from typing_extensions import Annotated
from dataclasses import dataclass

@dataclass
# class OAuth2Form(OAuth2PasswordRequestForm):
class OAuth2Form():
    login: Annotated[str, Form()]
    password: Annotated[str, Form()]