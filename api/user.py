READ_USERS_QUERY = 'SELECT `id`,`first_name`,`last_name`,`mail`,`birthdate` FROM `user`'
READ_USER_BY_ID = """
SELECT `id`, `first_name`, `last_name`, `mail`, `birthdate`
FROM `user`
WHERE `id`=?
"""

class User:
    def __init__(self, id, first_name, last_name, mail, birthdate):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.mail = mail
        self.birthdate = birthdate

    def __str__(self):
        return f'User({self.id},{self.first_name},{self.last_name},{self.mail},{self.birthdate})'

class DatabaseUserRepository:
    def __init__(self, connection):
        self.connection = connection

    def list(self):
        cur = self.connection.cursor()
        cur.execute(READ_USERS_QUERY)
        users = []
        for (id, first_name, last_name, mail, birthdate) in cur:
            users.append(User(id, first_name, last_name, mail, birthdate))
        return users

    def get(self, id):
        cur = self.connection.cursor()
        cur.execute(READ_USER_BY_ID, (id,))
        for (id, first_name, last_name, mail, birthdate) in cur:
            return User(id, first_name, last_name, mail, birthdate)
        return None
