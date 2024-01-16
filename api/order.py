from product import Product
READ_ORDERS_QUERY="""
select * from order inner join order_product on order.id = order_product.order_id inner join product on order_product.product_id=product.id
"""

class Order:
    def __init__(self, id, user_id, datetime, status, product: [Product], quantity):
        self.id = id
        self.user_id = user_id
        self.datetime = datetime
        self.status = status
        self.product = product
        self.quantity = quantity

    def __str__(self):
        return f'Order({self.id},{self.user_id},{self.datetime},{self.status},{self.product},{self.quantity})'

class DatabaseOrderRepository:
    def __init__(self,connection):
        self.connection = connection
    
    def list(self):
        cur = self.connection.cursor()
        cur.execute(READ_ORDERS_QUERY)
        orders = []
        #order ha una lista di prodotti . com s feisc
        for (id, date, status, order_id, quantity, weight, quantity, name, price, width, height, depth, weight) in enumerate(cur):                
            orders.append(Order(id, date, status, Product(order_id, name, price, width, height, depth, weight, quantity)))
        return orders

