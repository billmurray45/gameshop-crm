from fastapi import APIRouter, Request, Form, Depends, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.templates import templates
from app.core.database import get_session
from app.users.schemas import UserCreate, UserUpdate
from app.users.service import create_user_service, update_user_service
from app.users.repository import UserRepository
from datetime import date
from typing import Optional

router = APIRouter()


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    if request.state.user:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse("users/register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
    email: str = Form(...),
    username: str = Form(...),
    full_name: str = Form(None),
    password: str = Form(...)
):
    user_data = UserCreate(email=email, username=username, full_name=full_name, password=password)

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


@router.get("/user/{username}", response_class=HTMLResponse)
async def get_profile(
        request: Request,
        username: str,
        session: AsyncSession = Depends(get_session),
):
    user = await UserRepository.get_user_by_username(session, username)

    if not user:
        raise HTTPException(404, "Пользователь не найден!")

    return templates.TemplateResponse(
        "users/profile.html",
        {
            "request": request,
            "user": user,
        }
    )


@router.get("/user/{username}/edit", response_class=HTMLResponse)
async def edit_profile_page(
        request: Request,
        username: str,
        session: AsyncSession = Depends(get_session),
):
    user = await UserRepository.get_user_by_username(session, username)

    if not user:
        raise HTTPException(404, "Пользователь не найден!")
    if user.id != request.state.user.id:
        raise HTTPException(403, "Доступ запрещен!")

    return templates.TemplateResponse(
        "users/edit_profile.html",
        {
            "request": request,
            "user": user,
        }
    )


@router.post("/user/{username}/edit")
async def edit_profile(
    request: Request,
    username: str,
    session: AsyncSession = Depends(get_session),
    email: str = Form(None),
    full_name: str = Form(None),
    password: str = Form(None),
    birthday: date = Form(None),
    avatar: Optional[UploadFile] = File(None)
):
    user_data = UserUpdate(
        email=email,
        full_name=full_name,
        password=password if password else None,
        birthday=birthday,
        avatar=avatar
    )
    user = await UserRepository.get_user_by_username(session, username)

    try:
        await update_user_service(session, user_id=user.id, user_data=user_data, current_user_id=request.state.user.id)
        return RedirectResponse(f"/user/{username}", status_code=303)
    except HTTPException as exc:
        return templates.TemplateResponse(
            "users/edit_profile.html",
            {
                "request": request,
                "error": exc.detail,
                "form": {
                    "email": email,
                    "full_name": full_name,
                    "birthday": birthday,
                }
            }
        )
