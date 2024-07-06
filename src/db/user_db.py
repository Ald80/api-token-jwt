from sqlalchemy.orm import Session
from models.usuario import Usuario
from token_functions import verify_password, get_password_hash

def get_only_user(login_user: str, database: Session):
    user = database.query(Usuario) \
                .filter_by(login = login_user).first()
    return user

def get_user_password(login_user: str, password_user: str, database: Session):
    return database.query(Usuario) \
                    .filter_by(login = login_user,
                               password = get_password_hash(password_user)).first()

def authenticate_user(login: str, password: str, database: Session):
    # user = get_user_password(login, password, database)
    user: Usuario | None = get_only_user(login_user=login, database=database)
    if not user:
        return False
    if not verify_password(password, user_passaword=user.password):
        return False
    return user