from pydantic import BaseModel
from datetime import datetime
from fastapi import APIRouter, Response, status, HTTPException, Depends
from database import name as database_name, create_connection_pool
from typing import Annotated
from order import get_current_user, User

READ_SHIPMENTS_QUERY = """
SELECT id, order_id, datetime
FROM `shipment`
"""
READ_SHIPMENT_BY_ID = """
SELECT id, order_id, datetime
FROM `shipment`
WHERE id=?
"""
CREATE_SHIPMENT_BY_ORDER_ID = """
INSERT INTO shipment(order_id) VALUES (?)
"""


class Shipment(BaseModel):
    id: int
    order_id: int
    datetime: datetime


class DatabaseShipmentRepository:
    def __init__(self, pool):
        self.pool = pool

    def list(self):
        conn = self.pool.get_connection()
        conn.database = database_name
        cur = conn.cursor()
        cur.execute(READ_SHIPMENTS_QUERY)
        shipments = []
        for id, order_id, datetime in cur:
            shipments.append(Shipment(id=id, order_id=order_id, datetime=datetime))
        cur.close()
        conn.close()
        return shipments

    def get(self, id):
        conn = self.pool.get_connection()
        conn.database = database_name
        cur = conn.cursor()
        cur.execute(READ_SHIPMENT_BY_ID, (id,))
        for id, order_id, datetime in cur:
            return Shipment(id=id, order_id=order_id, datetime=datetime)
        cur.close()
        conn.close()
        return None

    def create(self, order_id):
        conn = self.pool.get_connection()
        conn.database = database_name
        cur = conn.cursor()
        cur.execute(CREATE_SHIPMENT_BY_ORDER_ID, (order_id,))
        shipment = self.get(order_id)
        cur.close()
        conn.close()
        return shipment


shipments_repository = DatabaseShipmentRepository(create_connection_pool('shipments'))
router = APIRouter()


@router.get("/shipments")
def read_users(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role==None:
         raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    shipments = shipments_repository.list()
    return shipments


@router.get("/shipments/{id}")
def read_user(id: int, current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role==None:
         raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    shipment = shipments_repository.get(id)
    if shipment is None:
        raise HTTPException(status_code=404)
    else:
        return shipment


class ShipmentModel(BaseModel):
    id: int


@router.post("/shipments", status_code=status.HTTP_201_CREATED)
def create_shipment(model: ShipmentModel,status_code=status.HTTP_201_CREATED, ):
    try:
        shipment = shipments_repository.create(model.id)
        return shipment
    except:
        return HTTPException(status_code=404)
