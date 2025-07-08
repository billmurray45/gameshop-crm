from fastapi import APIRouter, Request, Depends, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.auth.security import create_access_token
from app.auth.schemas import LoginForm
from app.auth.service import auth_user_serivce
from app.dependencies.templates import templates

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
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
        await auth_user_serivce(session, login_form)
        access_token = create_access_token({"sub": login_form.username})

        response = RedirectResponse(url=f"/profile", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=60 * 30,
            samesite="lax"
        )
        return response
    except HTTPException as exc:
        return templates.TemplateResponse(
            "users/login.html",
            {
                "request": request,
                "error": exc.detail,
                "form": login_form.model_dump(),
            }
        )
