from datetime import date, datetime, timedelta, timezone
from fastapi import APIRouter, Response, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Annotated, Optional
import hashlib
import redis

from user import User, user_repository

# TODO: add error handling
r = redis.Redis(host='redis', decode_responses=True, protocol=3)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# TODO: replace this key with an environment variable
SECRET_KEY = "f2b5a308e934de7c37a179e416ae075449694bf0ac7672c23598778d6f837b09"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

DATE_FMT = '%Y-%m-%d'

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user(username: str) -> Optional[User]:
    user = r.hgetall('user:session:' + username)
    if len(user) == 0:
        user = user_repository.get_by_mail(username)
        mapping = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'mail': user.mail,
            'birthdate': user.birthdate.strftime(DATE_FMT),
        }
        r.hset('user:session:' + username, mapping=mapping)
    else:
        user = User(
            id=user['id'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            mail=user['mail'],
            birthdate=date.strptime(user['birthdate'], DATE_FMT).date(),
        )

    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return user


router = APIRouter()


@router.get("/auth/me")
async def read_auth_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    username = form_data.username
    password = form_data.password

    user = user_repository.get_credentials(username)

    if (
        user is None
        or not hashlib.sha256(bytes(password, 'utf-8')).hexdigest() == user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")
