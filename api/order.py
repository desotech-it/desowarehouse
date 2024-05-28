from product import Product
from pydantic import BaseModel
from datetime import datetime
from typing import List, Annotated
from fastapi import APIRouter, Response, Depends, HTTPException
from database import name as database_name, pool
from user import User, get_current_user
READ_ORDERS_QUERY = """
select `order`.*, product.id AS product_id, product.name, product.price, product.width, product.height, product.depth, product.weight, order_product.quantity
from `order` inner join order_product on order.id = order_product.order_id inner join product on order_product.product_id=product.id
"""
READ_ORDER_BY_ID = """
 select `order`.*, product.id AS product_id, product.name, product.price, product.width, product.height,
product.depth, product.weight, order_product.quantity from `order` inner join order_product on order.id = order_product.order_id inner join product on order_product.product_id=product.id where `order`.id=(?);
"""
CREATE_ORDER_BY_ORDER_ID = """
insert into `order` values ();
insert into order_product values ((select max(id) from `order`), ?, ?);
"""
DELETE_ORDER_BY_ID = """
DELETE FROM `order` where id=?
"""
READ_ORDERS_BY_USER="""
select order_id, product_id, name, quantity, datetime, status from `order` join `order_product` on order.id = order_product.order_id join user on user.id = order.user_id join product on order_product.product_id=product.id where user.id=(?)"""
READ_ORDER_BY_USERS_AND_ORDER_ID="""
select order_id, product_id, name, quantity, datetime, status from `order` join `order_product` on order.id = order_product.order_id join user on user.id = order.user_id join product on order.id=product.id where user.id=(?) and order_id=(?);"""

MODIFY_ORDER = """
UPDATE `order` SET status=? where id=?
"""

class Order(BaseModel):
    id: int
    user_id: int
    datetime: datetime
    status: str
    products: List[Product]


class DatabaseOrderRepository:
    def __init__(self, connection):
        self.connection = connection

    def list(self):
        cur = self.connection.cursor()
        cur.execute(READ_ORDERS_QUERY)
        orders = {}
        for (
            id,
            datetime,
            status,
            user_id,
            product_id,
            name,
            price,
            width,
            height,
            depth,
            weight,
            quantity,
        ) in cur:
            if id not in orders:
                orders[id] = Order(id=id, datetime=datetime, status=status, products=[], user_id=user_id)
            orders[id].products.append(
                Product(
                    id=product_id,
                    name=name,
                    price=price,
                    width=width,
                    height=height,
                    depth=depth,
                    weight=weight,
                    quantity=quantity,
                )
            )
        cur.close()
        return list(orders.values())

    def get(self, id):
        cur = self.connection.cursor()
        cur.execute(READ_ORDER_BY_ID, (id,))
        products = {}
        for (
            id,
            datetime,
            status,
            user_id,
            product_id,
            name,
            price,
            width,
            height,
            depth,
            weight,
            quantity,
        ) in cur:
            if id not in products:
                products[id] = []
                order = Order(id=id, datetime=datetime, status=status, products=[], user_id=user_id)
            products[id].append(
                Product(
                    id=product_id,
                    name=name,
                    price=price,
                    width=width,
                    height=height,
                    depth=depth,
                    weight=weight,
                    quantity=quantity,
                )
            )
        order.products = products[id]
        cur.close()
        return order

    def create(self, product_id, quantity):
        cur = self.connection.cursor()
        cur.execute(CREATE_ORDER_BY_ORDER_ID, (product_id, quantity))
        cur.execute("select max(id) from `order`")
        for id in cur:
            return {"order_id": id}
        self.connection.commit()
        cur.close()

    def delete(self, id):
        cur = self.connection.cursor()
        cur.execute(DELETE_ORDER_BY_ID, (id,))
        self.connection.commit()
        cur.close()

    def get_by_user(self, user_id):
        cur = self.connection.cursor()
        cur.execute(READ_ORDERS_BY_USER, (user_id,))
        orders={}
        total=[]
        for(order_id, product_id, name, quantity, datetime, status) in cur:
            if order_id not in orders:
                orders[order_id]={}
                orders[order_id]["products"]=[]
            orders[order_id]["products"].append({"product_id": product_id, "name":name, "quantity":quantity})
            orders[order_id]["datetime"]=datetime
            orders[order_id]["status"]=status
        for order_id in orders:
            total.append({"order_id":order_id, "products":orders[order_id]["products"], "datetime":orders[order_id]["datetime"], "status":orders[order_id]["status"]})
        cur.close()
        return total

    def get_by_user_order(self, user_id, order_id):
        cur = self.connection.cursor()
        cur.execute(READ_ORDER_BY_USERS_AND_ORDER_ID, (user_id,order_id))
        orders={}
        for(order_id, product_id, name, quantity, datetime, status) in cur:
            if order_id not in orders:
                orders[order_id]=[]
            orders[order_id].append({"product_id": product_id, "name":name,"quantiy":quantity})
            orders["datetime"]=datetime
            orders["status"]=status
        cur.close()
        return orders

    def modify(self, id, status):
        cur = self.connection.cursor()
        cur.execute(MODIFY_ORDER, (status, id))
        self.connection.commit()
        cur.close()
        return

connection = pool.get_connection()
connection.database = database_name
order_repository = DatabaseOrderRepository(connection)
router = APIRouter()

@router.get("/orders")
def read_orders(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role==None:
         raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    orders = order_repository.list()
    return orders


@router.get("/orders/{id}")
def read_order(id: int, current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role==None:
         raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        order = order_repository.get(id)
        return order
    except:
        raise HTTPException(status_code=404)


class OrderModel(BaseModel):
    product_id: int
    quantity: int

class StatusModel(BaseModel):
    status: str

@router.post("/orders")
def create_order(model: OrderModel, current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role==None:
         raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    order = order_repository.create(model.product_id, model.quantity)
    return order

@router.patch("/orders/{id}")
def modify_order(id:int, status: StatusModel):
    try:
        order_repository.modify(id, status.status)
    except:
         raise HTTPException(
        status_code=400,
        detail="Invalid request"
         )


@router.delete("/orders/{id}")
def delete_order(id: int, current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role==None:
         raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        order_repository.delete(id)
    except:
        return HTTPException(status_code=404)

@router.get("/users/{user_id}/orders")
def get_user_order(user_id: int, current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.id!=user_id:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        orders = order_repository.get_by_user(user_id)
        return orders
    except:
        HTTPException(status_code=404)

@router.get("/users/{user_id}/orders/{order_id}")
def get_user_order(user_id: int, order_id: int, current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.id!=user_id:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        order = order_repository.get_by_user_order(user_id)
        return order
    except:
        HTTPException(status_code=404)
