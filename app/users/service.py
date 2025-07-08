from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate
from app.users.crud import (
    create_user,
    get_user_by_id,
    get_user_by_email,
    get_user_by_username,
    update_user
)
from app.auth.security import get_password_hash


async def create_user_service(session: AsyncSession, user_data: UserCreate) -> User:
    if await get_user_by_email(session, str(user_data.email)):
        raise HTTPException(409, "Email уже зарегистрирован")
    if await get_user_by_username(session, user_data.username):
        raise HTTPException(409, "Имя пользователя уже занято")
    if len(user_data.password) < 8:
        raise HTTPException(400, "Пароль должен содержать не менее 8 символов")

    user = User(
        email=str(user_data.email),
        hashed_password=get_password_hash(user_data.password),
        username=user_data.username,
        full_name=user_data.full_name
    )

    return await create_user(session, user)


async def update_user_service(session: AsyncSession, user_id: int, user_data: UserUpdate) -> User | None:
    user = await get_user_by_id(session, user_id)

    if not user:
        raise HTTPException(404, "Пользователь не найден")

    user_data = user_data.model_dump(exclude_unset=True)

    if "password" in user_data:
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))

    for field, value in user_data.items():
        setattr(user, field, value)

    return await update_user(session, user)
