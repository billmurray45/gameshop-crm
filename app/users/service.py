from urllib.request import Request

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate
from app.users.repository import UserRepository
from app.auth.security import get_password_hash
import os

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
}


async def create_user_service(session: AsyncSession, user_data: UserCreate) -> User:
    if await UserRepository.get_user_by_email(session, str(user_data.email)):
        raise HTTPException(409, "Email уже зарегистрирован")
    if await UserRepository.get_user_by_username(session, user_data.username):
        raise HTTPException(409, "Имя пользователя уже занято")
    if len(user_data.password) < 8:
        raise HTTPException(400, "Пароль должен содержать не менее 8 символов")

    user = User(
        email=str(user_data.email),
        hashed_password=get_password_hash(user_data.password),
        username=user_data.username,
        full_name=user_data.full_name
    )

    return await UserRepository.create_user(session, user)


async def update_user_service(
        session: AsyncSession,
        user_id: int,
        user_data: UserUpdate,
        current_user_id: int
) -> User:
    user = await UserRepository.get_user_by_id(session, user_id)

    if not user:
        raise HTTPException(404, "Пользователь не найден")
    if user_id != current_user_id:
        raise HTTPException(403, "Доступ запрещен!")

    update_data = user_data.model_dump(exclude_unset=True)

    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    avatar_file = getattr(user_data, "avatar", None)

    if avatar_file and avatar_file.filename:
        if avatar_file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(400, "Можно загружать только изображения (jpeg, png, gif, webp, bmp)!")
        contents = await avatar_file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(400, "Максимальный размер файла — 5 МБ!")

        upload_dir = "app/static/avatars"
        os.makedirs(upload_dir, exist_ok=True)
        ext = os.path.splitext(avatar_file.filename)[-1]
        file_name = f"{user.username}{ext}"
        file_location = os.path.join(upload_dir, file_name)
        with open(file_location, "wb") as buffer:
            buffer.write(contents)
        user.avatar = f"/static/avatars/{file_name}"

    update_data.pop("avatar", None)

    for field, value in update_data.items():
        setattr(user, field, value)

    await session.commit()
    await session.refresh(user)
    return user
