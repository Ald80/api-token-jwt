from typing import List
from sqlalchemy.orm import Session
from models.pais import Pais
from sqlalchemy import func, delete
from schemas.pais import PaisScheme

def search_countrie(database: Session) -> List[Pais]:
    return database.query(Pais).all()

def search_countrie_by_name(countrie_name: str, database: Session) -> List[Pais]:
    return database.query(Pais).filter(func.lower(Pais.name).like(f"%{countrie_name.lower()}%")).all()

def search_countrie_by_id(pais_id: int, database: Session):
    pais_db = database.query(Pais).filter(Pais.id == pais_id).first()
    return pais_db

def persist_countrie(paisScheme: PaisScheme, database: Session) -> PaisScheme:
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

def remove_countrie(pais_id: int, database: Session) -> int:
    database.query(Pais).filter(Pais.id == pais_id).delete()
    database.commit()
    return pais_id

def generate_list_of_dict_countries(countries: List):
    countries = [
        {"id": countrie.id, 
        "name": countrie.name, 
        "acronym": countrie.acronym,
        "gentile": countrie.gentile} 
        for countrie in countries]
    return countries
