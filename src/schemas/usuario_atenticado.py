from pydantic import BaseModel

class UsuarioAtenticado(BaseModel):
    login: str
    nome: str
    token: str
    administrator: bool
    authenticated: bool
