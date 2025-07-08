from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.users.models import User


async def create_user(session: AsyncSession, user: User) -> User:
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user_by_id(session: AsyncSession, user_id: int) -> User:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    return user


async def get_user_by_email(session: AsyncSession, email: str) -> User:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    return user


async def get_user_by_username(session: AsyncSession, username: str) -> User:
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    return user


async def update_user(session: AsyncSession, user: User) -> User:
    await session.commit()
    await session.refresh(user)
    return user
