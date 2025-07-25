from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.games.models import Game, Platform
from app.games.schemas import GameCreate, GameUpdate
from app.games.repository import GameRepository


async def create_game_service(session: AsyncSession, game_data: GameCreate) -> Game:
    if await GameRepository.get_game_by_name(session, game_data.name):
        raise HTTPException(409, "Игра с таким названием уже существует!")
    if len(game_data.name) < 3:
        raise HTTPException(400, "Название игры должно содержать не менее 3 символов!")

    game = Game(
        name=game_data.name,
        description=game_data.description,
        release_date=game_data.release_date,
        platforms=[Platform(name=platform) for platform in game_data.platforms]
    )

    return await GameRepository.create_game(session, game)


async def update_game_service(session: AsyncSession, game_id: int, game_data: GameUpdate) -> Game:
    game = await GameRepository.get_game_by_id(session, game_id)

    if not game:
        raise HTTPException(404, "Игра не найдена!")

    update_data = game_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(game, field, value)
    if "platforms" in update_data:
        game.platforms = [Platform(name=platform) for platform in update_data["platforms"]]

    return await GameRepository.update_game(session, game)
