import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

import jwt
import base64
import re
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload

from backend.app.database.database import get_session
from backend.app.core.config import get_settings
from backend.app.models.users import User, UserToken

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Password validation regex
PASSWORD_REGEX = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def is_password_strong_enough(password: str) -> bool:
    return bool(PASSWORD_REGEX.match(password))


def str_encode(plain_str: str) -> str:
    return base64.b85encode(plain_str.encode('utf-8')).decode('utf-8')


def str_decode(encoded_str: str) -> str:
    return base64.b85decode(encoded_str.encode('utf-8')).decode('utf-8')


def generate_token(payload: dict, secret: str, algo: str, expiry: timedelta) -> str:
    token_payload = payload.copy()
    token_payload.update({
        "exp": datetime.now(timezone.utc) + expiry,
        "iat": datetime.now(timezone.utc)
    })
    return jwt.encode(token_payload, secret, algorithm=algo)


def get_token_payload(token: str) -> Optional[dict]:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": True}
        )
    except jwt.ExpiredSignatureError:
        logging.debug("Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError:
        logging.debug("Invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logging.error(f"Unexpected JWT error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


async def get_token_user(token: str, db: Session) -> Optional[User]:
    payload = get_token_payload(token)

    if not payload:
        return None

    try:
        user_token_id = str_decode(payload.get('r'))
        user_id = str_decode(payload.get('sub'))
        access_key = payload.get('a')

        stmt = select(UserToken).where(
            UserToken.id == user_token_id,
            UserToken.user_id == user_id,
            UserToken.access_key == access_key,
            UserToken.expires_at > datetime.now(timezone.utc)
        ).options(joinedload(UserToken.user))

        user_token = db.exec(stmt).first()
        return user_token.user if user_token else None

    except Exception as e:
        logging.error(f"Token verification error: {str(e)}")
        return None


async def load_user(email: str, db: Session) -> Optional[User]:
    try:
        stmt = select(User).where(User.email == email)
        return db.exec(stmt).one()
    except NoResultFound:
        logging.info(f"User not found: {email}")
        return None
    except Exception as e:
        logging.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = await get_token_user(token=token, db=db)
    if user is None:
        raise credentials_exception
    return user