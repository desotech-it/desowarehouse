from datetime import date, datetime, timedelta, timezone
from fastapi import APIRouter, Response, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Annotated, Optional
import hashlib

from cache import r
from database import name as database_name, pool

READ_USERS_QUERY = """
SELECT u.id, u.first_name, u.last_name, u.mail, u.birthdate, r.name AS role
FROM user AS u LEFT JOIN
     user_role AS ur ON u.id = ur.user_id LEFT JOIN
     role AS r ON r.id = ur.role_id
"""

READ_USER_BY_ID = """
SELECT u.id, u.first_name, u.last_name, u.mail, u.birthdate, r.name AS role
FROM user AS u LEFT JOIN user_role AS ur ON u.id = ur.user_id LEFT JOIN role AS r ON ur.role_id = r.id
WHERE u.id = ?
"""

READ_USER_BY_MAIL = """
SELECT u.id, u.first_name, u.last_name, u.mail, u.birthdate, r.name AS role
FROM user AS u LEFT JOIN user_role AS ur ON u.id = ur.user_id LEFT JOIN role AS r ON ur.role_id = r.id
WHERE u.mail = ?
"""

READ_USER_CREDENTIALS = 'SELECT `mail`,`password` FROM `user` WHERE `mail`=?'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
connection = pool.get_connection()
connection.database = database_name

class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    mail: str
    birthdate: date
    role: Optional[str] = None


class UserCredentials(BaseModel):
    username: str
    hashed_password: str


class DatabaseUserRepository:
    def __init__(self, connection):
        self.connection = connection

    def list(self):
        cur = self.connection.cursor()
        cur.execute(READ_USERS_QUERY)
        users = []
        for id, first_name, last_name, mail, birthdate, role in cur:
            users.append(
                User(
                    id=id,
                    first_name=first_name,
                    last_name=last_name,
                    mail=mail,
                    birthdate=birthdate,
                    role=role
                )
            )
        return users

    def get(self, id):
        cur = self.connection.cursor()
        cur.execute(READ_USER_BY_ID, (id,))
        for id, first_name, last_name, mail, birthdate, role in cur:
            return User(
                id=id, first_name=first_name, last_name=last_name, mail=mail, birthdate=birthdate, role=role
            )
        return None

    def get_by_mail(self, mail):
        cur = self.connection.cursor()
        cur.execute(READ_USER_BY_MAIL, (mail,))
        for id, first_name, last_name, mail, birthdate, role in cur:
            return User(
                id=id, first_name=first_name, last_name=last_name, mail=mail, birthdate=birthdate, role=role
            )
        return None

    def get_credentials(self, username) -> UserCredentials | None:
        cur = self.connection.cursor()
        cur.execute(READ_USER_CREDENTIALS, (username,))
        user = None
        for mail, password in cur:
            user = UserCredentials(username=mail, hashed_password=password)
        return user

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

user_repository = DatabaseUserRepository(connection)

# TODO: replace this key with an environment variable
SECRET_KEY = "f2b5a308e934de7c37a179e416ae075449694bf0ac7672c23598778d6f837b09"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

DATE_FMT = '%Y-%m-%d'

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_from_cache_or_db(username: str) -> Optional[User]:
    user = r.hgetall('user:session:' + username)
    if len(user) == 0:
        user = user_repository.get_by_mail(username)
        mapping = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'mail': user.mail,
            'birthdate': user.birthdate.strftime(DATE_FMT),
            'role': 'none' if user.role is None else user.role,
        }
        r.hset('user:session:' + username, mapping=mapping)
    else:
        user = User(
            id=user['id'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            mail=user['mail'],
            birthdate=datetime.strptime(user['birthdate'], DATE_FMT).date(),
            role=None if user['role'] == 'none' else user['role'],
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
    user = get_user_from_cache_or_db(token_data.username)
    if user is None:
        raise credentials_exception
    return user


def make_token(username: str, password: str):
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

router = APIRouter()


@router.get("/users", tags=['users'])
def read_users(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    users = user_repository.list()
    return users


@router.get("/users/{id}", tags=['users'])
def read_user(id: int, current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role == None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    user = user_repository.get(id)
    if user is None:
        raise HTTPException(status_code=404)
    else:
        return user
