from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates
from app.users.models import User
from app.auth.security import get_current_user

templates = Jinja2Templates(directory="app/templates")


def get_template_context(request: Request, current_user: User = Depends(get_current_user)):
    return {"request": request, "current_user": current_user}
