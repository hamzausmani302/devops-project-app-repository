from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse
from catalog_service.util.version_util import get_app_version
from catalog_service.telemetry import trace_function
import time 

product_router: APIRouter = APIRouter()
app_version: str = get_app_version()

@product_router.get("/products")
@trace_function("get_all_products")
def get_all_products() -> list[dict]:
    import json
    process_products()
    with open("data.json", "r",  encoding="utf-8") as f:
        data = json.loads(f.read())
    return data

@trace_function("sleeping for 5")
def process_products():
    time.sleep(5)
