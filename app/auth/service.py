from fastapi import HTTPException, status
from app.users.repository import UserRepository
from app.auth.security import verify_password
from app.auth.schemas import LoginForm


async def auth_user_service(session, login_form: LoginForm):
    user = await UserRepository.get_user_by_username(session, login_form.username)
    if not user or not verify_password(login_form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль"
        )
    return user
