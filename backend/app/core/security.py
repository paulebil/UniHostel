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
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from sqlmodel import Session

from backend.app.database.database import get_session
from backend.app.core.config import get_settings
from backend.app.models.users import User, UserToken
from backend.app.utils.string import unique_string

settings = get_settings()

class Security:
    PASSWORD_REGEX = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

    @staticmethod
    def hash_password(password: str) -> str:
        return Security.pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return Security.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def is_password_strong_enough(password: str) -> bool:
        return bool(Security.PASSWORD_REGEX.match(password))

    @staticmethod
    def str_encode(plain_str: str) -> str:
        return base64.b85encode(plain_str.encode('utf-8')).decode('utf-8')

    @staticmethod
    def str_decode(encoded_str: str) -> str:
        return base64.b85decode(encoded_str.encode('utf-8')).decode('utf-8')

    @staticmethod
    def generate_token(payload: dict, expiry: timedelta) -> str:
        token_payload = payload.copy()
        token_payload.update({
            "exp": datetime.now(timezone.utc) + expiry,
            "iat": datetime.now(timezone.utc)
        })
        return jwt.encode(
            token_payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )

    def generate_token_pair(self, user: User, session: Session):
        refresh_key = unique_string(100)
        access_key = unique_string(50)
        rt_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

        user_token = UserToken()
        user_token.user_id = user.id
        user_token.refresh_key = refresh_key
        user_token.access_key = access_key
        user_token.expires_at = datetime.now() + rt_expires
        session.add(user_token)
        session.commit()
        session.refresh(user_token)

        at_payload = {
            "sub": self.str_encode(str(user.id)),
            "a": access_key,
            "r": self.str_encode(str(user_token.id)),
            "n": self.str_encode(f"{user.name}")
        }

        at_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.generate_token(at_payload, at_expires)

        rt_payload = {
            "sub": self.str_encode(str(user.id)),
            "t": refresh_key,
            "a": access_key
        }
        refresh_token = self.generate_token(rt_payload, rt_expires)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": at_expires.seconds
        }

    @staticmethod
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

    async def get_token_user(self, token: str, session: Session) -> Optional[User]:
        payload = self.get_token_payload(token)

        if not payload:
            return None

        try:
            user_token_id = self.str_decode(payload.get('r'))
            user_id = self.str_decode(payload.get('sub'))
            access_key = payload.get('a')

            stmt = select(UserToken).where(
                UserToken.id == user_token_id,
                UserToken.user_id == user_id,
                UserToken.access_key == access_key,
                UserToken.expires_at > datetime.now(timezone.utc)
            ).options(joinedload(UserToken.user))

            # Use session.execute() with .scalars().first() to fetch a single result
            user_token = session.execute(stmt).scalars().first()
            return user_token.user if user_token else None

        except Exception as e:
            logging.error(f"Token verification error: {str(e)}")
            return None

    @staticmethod
    async def load_user(email: str, session: Session) -> Optional[User]:
        try:
            stmt = select(User).where(User.email == email)
            # Use session.execute() with .scalars().first() to fetch a single result
            user = session.execute(stmt).scalars().first()
        except NoResultFound:
            logging.info(f"User not found: {email}")
            user = None
        except Exception as e:
            logging.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
        return user

    async def get_current_user(self, token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        user = await self.get_token_user(token=token, session=session)
        if user is None:
            raise credentials_exception
        return user
