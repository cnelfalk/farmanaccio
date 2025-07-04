# utils/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def is_hashed(value: str) -> bool:
    # devuelve None si no reconoce el esquema, o el nombre del esquema si es hash
    return pwd_context.identify(value) is not None
