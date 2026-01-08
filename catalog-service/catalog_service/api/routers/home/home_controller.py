from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from catalog_service.util.version_util import get_app_version

home_router: APIRouter = APIRouter()
app_version: str = get_app_version()

@home_router.get("/", response_class=HTMLResponse)
def Home():
    return f"""
        <html>
        <head> 
            <title>Catalog Service</title>
        </head>
        <body>
            <h1> Applcation =>  Catalog Service - Version : {app_version} </h1>
        </body>
        </html>
    """ 