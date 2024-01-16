from fastapi import FastAPI, Response, HTTPException, status
from pydantic import BaseModel
import os
import mariadb
import sys
import shipment
import user
import product
import order

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
    if user is None:
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
    if user is None:
        raise HTTPException(status_code=404)
    else:
        return shipment

@app.get("/orders")
def read_orders():
    orders = order_repository.list()
    return orders

class Model(BaseModel):
    id: int
@app.post("/shipments", status_code=status.HTTP_201_CREATED)
def create_shipment(model:Model, response: Response, status_code=status.HTTP_201_CREATED):
    try:
        shipment = shipments_repository.create(model.id)
        return shipment
    except:
        return HTTPException(status_code=404)
