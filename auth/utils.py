import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY  = os.getenv("SECRET_KEY")
ALGORITHM   = os.getenv("ALGORITHM", "HS256")
EXPIRE_HRS  = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", 96))

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain.encode("utf-8"),
            hashed.encode("utf-8")
        )
    except ValueError:
        return False


def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire  = datetime.utcnow() + timedelta(hours=EXPIRE_HRS)
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
