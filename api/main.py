from typing import Annotated
from fastapi import FastAPI, Response, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import os
import mariadb
import sys
import shipment
import user
import product
import order
from datetime import date, datetime, timedelta, timezone
import hashlib
from user import User, UserCredentials, DatabaseUserRepository
from jose import JWTError, jwt

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

user_repository = DatabaseUserRepository(conn)
product_repository = product.DatabaseProductRepository(conn)
shipments_repository = shipment.DatabaseShipmentRepository(conn)
order_repository = order.DatabaseOrderRepository(conn)

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

@app.get("/products")
def read_users():
    products = product_repository.list()
    return products

@app.get("/products/{id}")
def read_user(id: int, response: Response):
    product = product_repository.get(id)
    if product is None:
        raise HTTPException(status_code=404)
    else:
        return product

@app.get("/shipments")
def read_users():
    shipments = shipments_repository.list()
    return shipments

@app.get("/shipments/{id}")
def read_user(id: int, response: Response):
    shipment = shipments_repository.get(id)
    if shipment is None:
        raise HTTPException(status_code=404)
    else:
        return shipment


class ShipmentModel(BaseModel):
    id: int
@app.post("/shipments", status_code=status.HTTP_201_CREATED)
def create_shipment(model:ShipmentModel, response: Response, status_code=status.HTTP_201_CREATED):
    try:
        shipment = shipments_repository.create(model.id)
        return shipment
    except:
        return HTTPException(status_code=404)


@app.get("/orders")
def read_orders():
    orders = order_repository.list()
    return orders
  
@app.get("/orders/{id}")
def read_order(id:int):
    try:
        order = order_repository.get(id)
        return order
    except:
        raise HTTPException(status_code=404)

class OrderModel(BaseModel):
    product_id: int
    quantity: int
@app.post("/orders")
def create_order(model: OrderModel):
    order = order_repository.create(model.product_id, model.quantity)
    return order

@app.delete("/orders/{id}")
def delete_order(id:int):
    try:
        order_repository.delete(id)
    except:
        return HTTPException(status_code=204)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "f2b5a308e934de7c37a179e416ae075449694bf0ac7672c23598778d6f837b09"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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

def fake_current_user():
    return User(
        id=1,
        first_name='Gianluca',
        last_name='Recchia',
        mail='g.recchia@desolabs.com',
        birthdate=date(1997, 9, 16),
    )

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    # user = get_user(fake_users_db, username=token_data.username)
    user = fake_current_user()
    if user is None:
        raise credentials_exception
    return user

@app.get("/auth/me")
async def read_auth_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    username = form_data.username
    password = form_data.password

    user = user_repository.get_credentials(username)

    if user is None or not hashlib.sha256(bytes(password, 'utf-8')).hexdigest() == user.hashed_password:
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
