from fastapi import APIRouter, Request, Form, Depends, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.templates import templates
from app.core.database import get_session
from app.users.schemas import UserCreate, UserUpdate
from app.users.service import create_user_service, update_user_service
from app.users.repository import UserRepository
from datetime import date
import os

router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
}


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
    avatar: str = Form(None),
):
    user_data = UserUpdate(
        email=email,
        full_name=full_name,
        password=password if password else None,
        birthday=birthday,
        avatar=avatar if avatar else None,
    )

    user = await UserRepository.get_user_by_username(session, username)

    if not user:
        raise HTTPException(404, "Пользователь не найден!")
    if user.id != request.state.user.id:
        raise HTTPException(403, "Доступ запрещен!")

    updated_user = await update_user_service(session, user.id, user_data)
    return RedirectResponse(f"/user/{updated_user.username}", status_code=303)


@router.post("/user/{username}/avatar")
async def upload_avatar(
    request: Request,
    username: str,
    session: AsyncSession = Depends(get_session),
    avatar: UploadFile = File(...),
):
    user = await UserRepository.get_user_by_username(session, username)

    if not user:
        raise HTTPException(404, "Пользователь не найден!")
    if user.id != request.state.user.id:
        raise HTTPException(403, "Доступ запрещен!")

    if avatar.content_type not in ALLOWED_MIME_TYPES:
        request.session["error"] = "Можно загружать только изображения (jpeg, png, gif, webp, bmp)!"
        return RedirectResponse(f"/user/{request.state.user.username}/edit", status_code=303)

    contents = await avatar.read()
    if len(contents) > MAX_FILE_SIZE:
        request.session["error"] = "Максимальный размер файла — 5 МБ!"
        return RedirectResponse(f"/user/{request.state.user.username}/edit", status_code=303)

    upload_dir = "app/static/avatars"
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(avatar.filename)[-1]
    file_name = f"{request.state.user.username}{ext}"
    file_location = os.path.join(upload_dir, file_name)

    with open(file_location, "wb") as buffer:
        buffer.write(contents)

    user.avatar = f"/static/avatars/{file_name}"
    await session.commit()
    await session.refresh(user)
    return RedirectResponse(f"/user/{request.state.user.username}", status_code=303)
