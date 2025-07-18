from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.database import async_session
from app.users.repository import UserRepository
from jose import jwt, JWTError
from app.auth.security import (
    REFRESH_SECRET_KEY, ALGORITHM,
    create_access_token, create_refresh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, SECRET_KEY
)


class AuthMiddleware(BaseHTTPMiddleware):
    ALLOWED_PATHS = ["/login", "/register", "/favicon.ico"]

    @staticmethod
    def is_allowed_path(path: str) -> bool:
        if path.startswith("/static/css/") or path.startswith("/static/js/"):
            return True
        return path in AuthMiddleware.ALLOWED_PATHS

    async def dispatch(self, request, call_next):
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        user = None
        new_access, new_refresh = None, None
        username = None

        if access_token:
            try:
                payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
                username = payload.get("sub")
            except JWTError:
                pass

        if username:
            async with async_session() as session:
                user = await UserRepository.get_user_by_username(session, username)

        if not user and refresh_token:
            try:
                payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
                if payload.get("token_type") == "refresh":
                    username = payload.get("sub")
                    if username:
                        async with async_session() as session:
                            user = await UserRepository.get_user_by_username(session, username)
                        if user:
                            new_access = create_access_token({"sub": username})
                            new_refresh = create_refresh_token({"sub": username})
            except JWTError:
                pass

        if not user and not self.is_allowed_path(request.url.path):
            return RedirectResponse("/login", status_code=303)

        request.state.user = user
        response = await call_next(request)

        if new_access and new_refresh:
            response.set_cookie(
                "access_token", new_access,
                max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                httponly=True, samesite="lax", secure=False
            )
            response.set_cookie(
                "refresh_token", new_refresh,
                max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
                httponly=True, samesite="lax", secure=False
            )

        return response
