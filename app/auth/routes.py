from fastapi import APIRouter, Request, Depends, Form, status, HTTPException, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.auth.security import (
    create_access_token,
    create_refresh_token,
    get_current_user_optional,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)
from app.auth.schemas import LoginForm
from app.auth.service import auth_user_service
from app.dependencies.templates import templates

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(
        request: Request,
        response: Response,
        current_user=Depends(get_current_user_optional)
):
    if current_user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        "users/login.html", {"request": request}
    )


@router.post("/login")
async def login_post(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        session: AsyncSession = Depends(get_session)
):
    login_form = LoginForm(username=username, password=password)

    try:
        await auth_user_service(session, login_form)
        access_token = create_access_token({"sub": login_form.username})
        refresh_token = create_refresh_token({"sub": login_form.username})

        response = RedirectResponse(url=f"/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 30 минут
            samesite="lax",
            secure=False  # Изменить на True в продакшене
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # 7 дней
            samesite="lax",
            secure=False,  # Изменить на True в продакшене
        )
        return response
    except HTTPException as exc:
        return templates.TemplateResponse(
            "users/login.html",
            {
                "request": request,
                "error": exc.detail,
                "form": login_form.model_dump()
            }
        )
