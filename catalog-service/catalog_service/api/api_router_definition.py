
from fastapi import APIRouter,FastAPI
from catalog_service.api.routers.home.home_controller import home_router
from catalog_service.api.routers.product.product_controller import product_router
from catalog_service.api.routers.orders.order_controller import order_router


router = APIRouter()

router.include_router(home_router)
router.include_router(product_router)
router.include_router(order_router)