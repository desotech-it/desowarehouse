READ_SHIPMENTS_QUERY="""
SELECT id, order_id, datetime
FROM `shipment` 
"""
READ_SHIPMENT_BY_ID="""
SELECT id, order_id, datetime
FROM `shipment`
WHERE id=?
"""
CREATE_SHIPMENT_BY_ORDER_ID="""
INSERT INTO shipment(order_id) VALUES (?)
"""
class Shipment:
    def __init__(self, id, order_id, datetime):
        self.id = id
        self.order_id = order_id
        self.datetime = datetime

    def __str__(self):
        return f'Shipment({self.id},{self.order_id},{self.datetime})'

class DatabaseShipmentRepository:
    def __init__(self,connection):
        self.connection = connection
    
    def list(self):
        cur = self.connection.cursor()
        cur.execute(READ_SHIPMENTS_QUERY)
        shipments = []
        for (id, order_id, datetime) in cur:
            shipments.append(Shipment(id, order_id, datetime))
        return shipments
    
    def get(self, id):
        cur = self.connection.cursor()
        cur.execute(READ_SHIPMENT_BY_ID, (id,))
        for (id, order_id, datetime) in cur:
            return Shipment(id, order_id, datetime)
        return None
    
    def create(self, order_id):
        try:
            cur = self.connection.cursor()
            cur.execute(CREATE_SHIPMENT_BY_ORDER_ID, (order_id,))
            print(f"{cur.rowcount} details inserted") 
            rows=cur.rowcount
            self.connection.commit()  
            #non ritorna ciò che crea
            #bisogna fare una join con prodotto per estrarre id_shipment, id_order, data
            # shipment=self.get(order_id)
            # return shipment
        except self.connection.Error:
            return self.connection.Error
