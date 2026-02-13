from sqlalchemy.orm import Session
from users.users_model import User
from core.security import bcrypt_context

def authuser(identifier: str, password: str, db: Session):
    """Busca usuario por username O email, y verifica contraseña."""
    user = db.query(User).filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()
    if not user:
        return None

    if not bcrypt_context.verify(password, user.password):
        return None

    return user