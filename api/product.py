from pydantic import BaseModel

READ_PRODUCTS_QUERY="""
SELECT product.id,product.name,product.price,product.width,product.height,product.depth,product.weight,inventory.quantity
FROM `product`
INNER JOIN `inventory` ON product.id=inventory.product_id
"""
READ_PRODUCT_BY_ID="""
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
    def __init__(self,connection):
        self.connection = connection

    def list(self):
        cur = self.connection.cursor()
        cur.execute(READ_PRODUCTS_QUERY)
        products = []
        for (id, name, price, width, height, depth, weight, quantity) in cur:
            products.append(Product(id=id, name=name, price=price, width=width, height=height, depth=depth, weight=weight, quantity=quantity))
        return products

    def get(self, id):
        cur = self.connection.cursor()
        cur.execute(READ_PRODUCT_BY_ID, (id,))
        for (id, name, price, width, height, depth, weight, quantity) in cur:
            return Product(id=id, name=name, price=price, width=width, height=height, depth=depth, weight=weight, quantity=quantity)
        return None
