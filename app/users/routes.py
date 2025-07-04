from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.templates import templates
from app.core.database import get_session
from app.users.schemas import UserCreate
from app.users.service import create_user_service
from app.users.crud import get_user_by_username

router = APIRouter()


@router.get("/users", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        "users/users.html", {"request": request}
    )


@router.post("/users", response_class=HTMLResponse)
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
            "users/users.html",
            {
                "request": request,
                "error": exc.detail,
                "form": user_data.model_dump()
            }
        )


@router.get("/profile/{username}", response_class=HTMLResponse)
async def get_profile(request: Request, username: str, session: AsyncSession = Depends(get_session)):
    user = await get_user_by_username(session, username)

    if not user:
        raise HTTPException(404, "Пользователь не найден!")

    return templates.TemplateResponse(
        "users/profile.html",
        {
            "request": request,
            "user": user
        }
    )
