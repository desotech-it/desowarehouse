from pydantic import BaseModel
from datetime import date

READ_USERS_QUERY = 'SELECT `id`,`first_name`,`last_name`,`mail`,`birthdate` FROM `user`'
READ_USER_BY_ID = """
SELECT `id`, `first_name`, `last_name`, `mail`, `birthdate`
FROM `user`
WHERE `id`=?
"""

class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    mail: str
    birthdate: date

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
