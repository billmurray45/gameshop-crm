from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.templates import templates
from app.core.database import get_session
from app.users.models import User
from app.users.schemas import UserCreate
from app.users.service import create_user_service
from app.users.repository import UserRepository
from app.auth.security import get_current_user_optional, get_current_user

router = APIRouter()


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, current_user=Depends(get_current_user_optional)):
    if current_user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        "users/register.html", {"request": request}
    )


@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
    email: str = Form(...),
    username: str = Form(...),
    full_name: str = Form(None),
    password: str = Form(...)
):
    user_data = UserCreate(
        email=email,
        username=username,
        full_name=full_name,
        password=password
    )

    try:
        await create_user_service(session, user_data)
        return templates.TemplateResponse(
            "users/register_success.html", {"request": request}
        )
    except HTTPException as exc:
        return templates.TemplateResponse(
            "users/register.html",
            {
                "request": request,
                "error": exc.detail,
                "form": user_data.model_dump()
            }
        )


@router.get("/user/{usernmae}", response_class=HTMLResponse)
async def get_profile(
        request: Request,
        username: str,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    user = await UserRepository.get_user_by_username(session, username)

    if not user:
        raise HTTPException(404, "Пользователь не найден!")

    return templates.TemplateResponse(
        "users/profile.html",
        {
            "request": request,
            "user": current_user
        }
    )
