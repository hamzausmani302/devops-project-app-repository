from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel
from typing import Any, Dict
import os
import json
import secrets
from datetime import datetime
# from catalog_service.core.services.messaging_service import get_publisher
from catalog_service.core.services.order_service import OrderService
from catalog_service.core.model.orders.order import Order
import logging
from catalog_service.api.deps import get_messaging_service 


order_router = APIRouter()


class OrderCreate(BaseModel):
    product: Dict[str, Any]
    quantity: int = 1


def _orders_file_path() -> str:
    return os.path.join(os.path.dirname(__file__), "../../../..", "orders.json")


@order_router.post("/order", status_code=201)
def create_order(request: Request, body: OrderCreate) -> Order:
    """Create an order and persist to orders.json (dummy storage)

    The endpoint will try to read the authenticated user from request.state.user
    if available.
    """
    """
    1. Create Order object from OrderCreate DTO
    2. Save the result to DB
    3. Send the object to RabbitMQ using a RabbitMQ DTO
    """
    user = getattr(request.state, "user", None)

    order = Order(
        id=secrets.token_hex(8),
        product_id=body.product.get("id"),
        metadata= {
            "price": body.product.get("price") 
        },
        user_id = "1"
    )
    order_service = OrderService()
    order_service.Add(order)
    get_messaging_service().publish(order.model_dump())
    return order

