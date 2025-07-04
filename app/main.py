from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.users.routes import router as user_router
import uvicorn

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(user_router)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, log_level="info")
