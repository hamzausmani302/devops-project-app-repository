from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse
from catalog_service.util.version_util import get_app_version

product_router: APIRouter = APIRouter()
app_version: str = get_app_version()

@product_router.get("/products")
def get_all_products() -> list[dict]:
    import json
    with open("data.json", "r",  encoding="utf-8") as f:
        data = json.loads(f.read())
    return data

