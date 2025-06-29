import asyncio
from app.core.database import engine


async def test_connection():
    async with engine.begin() as conn:
        print("Connection successful")

if __name__ == "__main__":
    asyncio.run(test_connection())
