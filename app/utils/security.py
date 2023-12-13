import os
import bcrypt
from jose import jwt

JWT_KEY = os.getenv("TO_JWT_KEY")
JWT_ALGORITM = "HS256"


def hash_password(plain):
    return bcrypt.hashpw(plain, bcrypt.gensalt(12))


def check_password(plain, hashed):
    return bcrypt.checkpw(plain, hashed)


def generate_jwt(data: dict):
    return jwt.encode(data, JWT_KEY, algorithm=JWT_ALGORITM)


def unpack_jwt(token: str):
    return jwt.decode(token, JWT_KEY, algorithms=[JWT_ALGORITM])
