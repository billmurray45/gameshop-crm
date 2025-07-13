from fastapi import HTTPException, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from app.core.database import get_session
from app.users.repository import UserRepository
from app.core.config import settings
from typing import Optional

SECRET_KEY = settings.SECRET_KEY
REFRESH_SECRET_KEY = settings.REFRESH_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    to_encode["token_type"] = "refresh"
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode["exp"] = int(expire.timestamp())
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")

    # нет Токенов → Ошибка
    if not access_token and not refresh_token:
        raise credentials_exception

    # только Refresh → Вернём пользователя (middleware создаст новые куки)
    if not access_token and refresh_token:
        try:
            payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("token_type") != "refresh" or not payload.get("sub"):
                raise credentials_exception
            user = await UserRepository.get_user_by_username(session, payload["sub"])
            if not user:
                raise credentials_exception
            return user
        except JWTError:
            raise credentials_exception

    # Access → проверим и вернём пользователя
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("sub"):
            raise credentials_exception
        user = await UserRepository.get_user_by_username(session, payload["sub"])
        if not user:
            raise credentials_exception
        return user
    except ExpiredSignatureError:
        # Access истек, проверим Refresh
        if not refresh_token:
            raise credentials_exception
        try:
            payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("token_type") != "refresh" or not payload.get("sub"):
                raise credentials_exception
            user = await UserRepository.get_user_by_username(session, payload["sub"])
            if not user:
                raise credentials_exception
            return user
        except JWTError:
            raise credentials_exception
    except JWTError:
        raise credentials_exception


async def get_current_user_optional(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        return await get_current_user(request, session)
    except HTTPException:
        return None
