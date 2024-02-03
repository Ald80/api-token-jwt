from .session_database import get_db, get_session
from ..models.pais import Pais
from ..models.token import Token
from ..models.usuario import Usuario
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# from ..main import get_password_hash
def get_password_hash(password):
    return pwd_context.hash(password)


def insert_initial_data():
    database = get_session()
    try:
        pais_data = database.query(Pais).all()
        usuario_data = database.query(Usuario).all()
        print("usuario_data")
        print(usuario_data)
        print("eqeqeqeqweqweqweq")
        if not usuario_data:
            print("entrei no if usuario_data ... ")
            # usuario_data_one = Usuario(login='convidado', password='manager', name='Usuario convidado', administrator=False)
            # usuario_data_two = Usuario(login='admin', password='suporte', name='Gestor', administrator=True)
            usuario_data_one = Usuario(login='convidado', password=get_password_hash('manager'), name='Usuario convidado', administrator=False)
            usuario_data_two = Usuario(login='admin', password=get_password_hash('suporte'), name='Gestor', administrator=True)

            database.add(usuario_data_one)
            database.add(usuario_data_two)

        if not pais_data:
            pais_data_one = Pais(name='Brasil', acronym='BR', gentile='Brasileiro')
            pais_data_two = Pais(name='Argentina', acronym='AR', gentile='Argentino')
            pais_data_three = Pais(name='Alemanha', acronym='AL', gentile='Alemão')
            database.add(pais_data_one)
            database.add(pais_data_two)
            database.add(pais_data_three)
        
        if not pais_data or not usuario_data:
            database.commit()

    except Exception:
        database.rollback()
    finally:
        database.close()