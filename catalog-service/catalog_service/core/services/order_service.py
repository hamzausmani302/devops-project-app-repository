import json
import os 

from catalog_service.core.model.orders.order import Order
class OrderService():
    def __init__(self):
        path = "order.json"
        self.path = path
        self.orders = []
    def get_data(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                return json.loads(f.read())
        return []
    
    def Add(self, order: Order):
        orders = self.get_data()
        print(orders)
        orders.append(order.model_dump())
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.orders, f, indent=2)
    




