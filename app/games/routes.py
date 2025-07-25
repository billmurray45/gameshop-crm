from fastapi import APIRouter

router = APIRouter()


@router.get("/games")
async def get_games():
    return {"message": "List of games will be here"}


@router.post("/games")
async def create_game():
    return {"message": "Game created successfully"}


@router.get("/games/{game_id}")
async def get_game(game_id: int):
    return {"message": f"Details of game with ID {game_id}"}
