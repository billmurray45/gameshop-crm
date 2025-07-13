from fastapi import FastAPI, Request, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.users.routes import router as user_router
from app.auth.routes import router as login_router
from app.auth.security import get_current_user
from app.dependencies.templates import templates
from jose import jwt, JWTError
from app.auth.security import (
    REFRESH_SECRET_KEY, ALGORITHM,
    create_access_token, create_refresh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
)
import uvicorn

app = FastAPI()


@app.middleware("http")
async def refresh_tokens_middleware(request: Request, call_next):
    response = await call_next(request)

    access = request.cookies.get("access_token")
    refresh = request.cookies.get("refresh_token")

    if not access and refresh:
        try:
            payload = jwt.decode(refresh, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("token_type") == "refresh" and payload.get("sub"):
                new_access = create_access_token({"sub": payload["sub"]})
                new_refresh = create_refresh_token({"sub": payload["sub"]})

                response.set_cookie(
                    "access_token", new_access, httponly=False,
                    max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    samesite="lax", secure=False, path="/"
                )
                response.set_cookie(
                    "refresh_token", new_refresh, httponly=False,
                    max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
                    samesite="lax", secure=False, path="/"
                )
        except JWTError:
            pass

    return response


@app.middleware("http")
async def redirect_401_to_login(request: Request, call_next):
    response = await call_next(request)
    if response.status_code == 401 and request.url.path != "/login":
        return RedirectResponse("/login", status_code=303)
    return response

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(user_router)
app.include_router(login_router)


@app.get("/", response_class=HTMLResponse)
async def get_home(
        request: Request,
        response: Response,
        current_user=Depends(get_current_user)
):
    return templates.TemplateResponse("base.html", {"request": request}, response=response)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, log_level="info")
