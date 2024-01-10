from fastapi import FastAPI, Response, HTTPException
import os
import mariadb
import sys

import user

db_host = os.environ['DATABASE_HOST']
db_name = os.environ['DATABASE_NAME']
db_user = os.environ['DATABASE_USER']
db_pass = os.environ['DATABASE_PASSWORD']

conn = None
try:
    conn = mariadb.connect(user=db_user, password=db_pass, host=db_host, database=db_name)
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

app = FastAPI()

user_repository = user.DatabaseUserRepository(conn)

@app.get("/users")
def read_users():
    users = user_repository.list()
    return users


@app.get("/users/{id}")
def read_user(id: int, response: Response):
    user = user_repository.get(id)
    if user is None:
        raise HTTPException(status_code=404)
    else:
        return user
