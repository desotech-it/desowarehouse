from pydantic import BaseModel
from datetime import date
from fastapi import APIRouter, Response
from database import name as database_name, pool

READ_USERS_QUERY = 'SELECT `id`,`first_name`,`last_name`,`mail`,`birthdate` FROM `user`'
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

# TODO: implemented salted password


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    mail: str
    birthdate: date
    role: str


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
        for id, first_name, last_name, mail, birthdate in cur:
            users.append(
                User(
                    id=id,
                    first_name=first_name,
                    last_name=last_name,
                    mail=mail,
                    birthdate=birthdate,
                )
            )
        return users

    def get(self, id):
        cur = self.connection.cursor()
        cur.execute(READ_USER_BY_ID, (id,))
        for id, first_name, last_name, mail, birthdate, role in cur:
            return User(
                id=id, first_name=first_name, last_name=last_name, mail=mail, birthdate=birthdate, role='user' if role is None else role
            )
        return None

    def get_by_mail(self, mail):
        cur = self.connection.cursor()
        cur.execute(READ_USER_BY_MAIL, (mail,))
        for id, first_name, last_name, mail, birthdate, role in cur:
            return User(
                id=id, first_name=first_name, last_name=last_name, mail=mail, birthdate=birthdate, role='user' if role is None else role
            )
        return None

    def get_credentials(self, username) -> UserCredentials | None:
        cur = self.connection.cursor()
        cur.execute(READ_USER_CREDENTIALS, (username,))
        user = None
        for mail, password in cur:
            user = UserCredentials(username=mail, hashed_password=password)
        return user


connection = pool.get_connection()
connection.database = database_name
user_repository = DatabaseUserRepository(connection)
router = APIRouter()


@router.get("/users", tags=['users'])
def read_users():
    users = user_repository.list()
    return users


@router.get("/users/{id}", tags=['users'])
def read_user(id: int, response: Response):
    user = user_repository.get(id)
    if user is None:
        raise HTTPException(status_code=404)
    else:
        return user
