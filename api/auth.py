from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from user import User, get_current_user, make_token

router = APIRouter()

@router.get("/auth/me")
async def read_auth_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.post("/auth/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    username = form_data.username
    password = form_data.password

    return make_token(username, password)
