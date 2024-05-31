from pydantic import BaseModel
from fastapi import APIRouter, Response, HTTPException
from database import name as database_name, create_connection_pool

READ_PRODUCTS_QUERY = """
SELECT product.id,product.name,product.price,product.width,product.height,product.depth,product.weight,inventory.quantity
FROM `product`
INNER JOIN `inventory` ON product.id=inventory.product_id
"""
READ_PRODUCT_BY_ID = """
SELECT product.id,product.name,product.price,product.width,product.height,product.depth,product.weight,inventory.quantity
FROM `product`
INNER JOIN `inventory` ON product.id=inventory.product_id
WHERE product.id=?
"""


class Product(BaseModel):
    id: int
    name: str
    price: float
    width: int
    height: int
    depth: int
    quantity: int


class DatabaseProductRepository:
    def __init__(self, pool):
        self.pool = pool

    def list(self):
        conn = self.pool.get_connection()
        conn.database = database_name
        cur = conn.cursor()
        cur.execute(READ_PRODUCTS_QUERY)
        products = []
        for id, name, price, width, height, depth, weight, quantity in cur:
            products.append(
                Product(
                    id=id,
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
        conn.close()
        return products

    def get(self, id):
        conn = self.pool.get_connection()
        conn.database = database_name
        cur = conn.cursor()
        cur.execute(READ_PRODUCT_BY_ID, (id,))
        for id, name, price, width, height, depth, weight, quantity in cur:
            return Product(
                id=id,
                name=name,
                price=price,
                width=width,
                height=height,
                depth=depth,
                weight=weight,
                quantity=quantity,
            )
        cur.close()
        conn.close()
        return None

product_repository = DatabaseProductRepository(create_connection_pool('products'))
router = APIRouter()


@router.get("/products")
def read_users():
    products = product_repository.list()
    return products


@router.get("/products/{id}")
def read_user(id: int, response: Response):
    product = product_repository.get(id)
    if product is None:
        raise HTTPException(status_code=404)
    else:
        return product
