from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from app.users.routes import router as user_router
from app.auth.routes import router as login_router
from app.dependencies.templates import templates
from app.core.middleware import AuthMiddleware
from app.core.database import settings
import uvicorn

app = FastAPI()

SESSION_SECRET_KEY = settings.SESSION_SECRET_KEY

app.add_middleware(SessionMiddleware, secret_key="SESSION_SECRET_KEY")
app.add_middleware(AuthMiddleware)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(user_router)
app.include_router(login_router)


@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, log_level="info")
