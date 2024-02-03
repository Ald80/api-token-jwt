from pydantic import BaseModel

class PaisScheme(BaseModel):
    # id: int
    name: str
    acronym: str
    gentile: str

    class Config:
        orm_mode = True