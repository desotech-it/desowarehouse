from pydantic import BaseModel
from datetime import datetime
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

class Shipment(BaseModel):
    id: int
    order_id: int
    datetime: datetime


class DatabaseShipmentRepository:
    def __init__(self,connection):
        self.connection = connection

    def list(self):
        cur = self.connection.cursor()
        cur.execute(READ_SHIPMENTS_QUERY)
        shipments = []
        for (id, order_id, datetime) in cur:
            shipments.append(Shipment(id=id, order_id=order_id, datetime=datetime))
        return shipments

    def get(self, id):
        cur = self.connection.cursor()
        cur.execute(READ_SHIPMENT_BY_ID, (id,))
        for (id, order_id, datetime) in cur:
            return Shipment(id=id, order_id=order_id, datetime=datetime)
        return None

    def create(self, order_id):
        cur = self.connection.cursor()
        cur.execute(CREATE_SHIPMENT_BY_ORDER_ID, (order_id,))
        print(f"{cur.rowcount} details inserted") 
        shipment=self.get(order_id)
        return shipment
      
