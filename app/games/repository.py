from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.games.models import Game
from typing import List, Optional


class GameRepository:
    @staticmethod
    async def create_game(session: AsyncSession, game: Game) -> Game:
        session.add(game)
        await session.commit()
        await session.refresh(game)
        return game

    @staticmethod
    async def get_game_by_id(session: AsyncSession, game_id: int) -> Optional[Game]:
        result = await session.execute(select(Game).where(Game.id == game_id))
        return result.scalars().first()

    @staticmethod
    async def get_all_games(session: AsyncSession) -> List[Game]:
        result = await session.execute(select(Game))
        return result.scalars().all()

    @staticmethod
    async def update_game(session: AsyncSession, game: Game) -> Game:
        await session.commit()
        await session.refresh(game)
        return game

    @staticmethod
    async def get_game_by_name(session: AsyncSession, name: str) -> Optional[Game]:
        result = await session.execute(select(Game).where(Game.name == name))
        return result.scalars().first()

    @staticmethod
    async def delete_game(session: AsyncSession, game: Game) -> None:
        await session.delete(game)
        await session.commit()
