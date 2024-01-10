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
class Product:
    def __init__(self, id, name, price, width, height, depth, weight, quantity):
        self.id = id
        self.name = name
        self.price = price
        self.width = width
        self.height = height
        self.depth = depth
        self.quantity = quantity

    def __str__(self):
        return f'Product({self.id},{self.name},{self.price},{self.width},{self.height},{self.depth},{self.weight},{self.quantity})'

class DatabaseProductRepository:
    def __init__(self,connection):
        self.connection = connection
    
    def list(self):
        cur = self.connection.cursor()
        cur.execute(READ_PRODUCTS_QUERY)
        products = []
        for (id, name, price, width, height, depth, weight, quantity) in cur:
            products.append(Product(id, name, price, width, height, depth, weight, quantity))
        return products
    
    def get(self, id):
        cur = self.connection.cursor()
        cur.execute(READ_PRODUCT_BY_ID, (id,))
        for (id, name, price, width, height, depth, weight, quantity) in cur:
            return Product(id, name, price, width, height, depth, weight, quantity)
        return None
