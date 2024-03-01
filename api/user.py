from pydantic import BaseModel
from datetime import date

READ_USERS_QUERY = 'SELECT `id`,`first_name`,`last_name`,`mail`,`birthdate` FROM `user`'
READ_USER_BY_ID = """
SELECT `id`, `first_name`, `last_name`, `mail`, `birthdate`
FROM `user`
WHERE `id`=?
"""
READ_USER_BY_MAIL = """
SELECT `id`, `first_name`, `last_name`, `mail`, `birthdate`
FROM `user`
WHERE `mail`=?
"""
READ_USER_CREDENTIALS = 'SELECT `mail`,`password` FROM `user` WHERE `mail`=?'

# TODO: implemented salted password

class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    mail: str
    birthdate: date

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
        for (id, first_name, last_name, mail, birthdate) in cur:
            users.append(User(id=id, first_name=first_name, last_name=last_name, mail=mail, birthdate=birthdate))
        return users

    def get(self, id):
        cur = self.connection.cursor()
        cur.execute(READ_USER_BY_ID, (id,))
        for (id, first_name, last_name, mail, birthdate) in cur:
            return User(id=id, first_name=first_name, last_name=last_name, mail=mail, birthdate=birthdate)
        return None

    def get_by_mail(self, mail):
        cur = self.connection.cursor()
        cur.execute(READ_USER_BY_MAIL, (mail,))
        for (id, first_name, last_name, mail, birthdate) in cur:
            return User(id=id, first_name=first_name, last_name=last_name, mail=mail, birthdate=birthdate)
        return None

    def get_credentials(self, username) -> UserCredentials | None:
        cur = self.connection.cursor()
        cur.execute(READ_USER_CREDENTIALS, (username,))
        user = None
        for (mail, password) in cur:
            user = UserCredentials(username=mail, hashed_password=password)
        return user
