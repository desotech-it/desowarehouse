from product import Product
READ_ORDERS_QUERY="""
select `order`.*, product.id AS product_id, product.name, product.price, product.width, product.height, product.depth, product.weight, order_product.quantity
from `order` inner join order_product on order.id = order_product.order_id inner join product on order_product.product_id=product.id
"""

class Order:
    def __init__(self, id, datetime, status, products: [Product]):
        self.id = id
        self.datetime = datetime
        self.status = status
        self.products = products

    def __str__(self):
        return f'Order({self.id},{self.user_id},{self.datetime},{self.status},{self.products})'

class DatabaseOrderRepository:
    def __init__(self,connection):
        self.connection = connection

    def list(self):
        cur = self.connection.cursor()
        cur.execute(READ_ORDERS_QUERY)
        products = {}
        orders = {}
        result = []
        #order ha una lista di prodotti . com s feisc
        for (id, date, status, product_id, name, price, width, height, depth, weight, quantity) in cur:
            if id not in products:
                products[id] = []
            products[id].append(Product(product_id, name, price, width, height, depth, weight, quantity))
            if id not in orders:
                orders[id] = Order(id, date, status, None)
        for id in products:
            order = orders[id]
            order.products = products[id]
            result.append(order)
        return result
