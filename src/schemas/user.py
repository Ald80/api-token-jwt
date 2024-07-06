from pydantic import BaseModel

class User(BaseModel):
    login: str
    password: str
    name: str | None = None
    administrator: bool | None = None