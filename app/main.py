from app.utils import verify_header
from app.templates_config import templates
from fastapi.staticfiles import StaticFiles
from app.routers import router, admin_router
from fastapi import FastAPI, Depends, Request


app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(admin_router, dependencies=[Depends(verify_header)])
app.include_router(router)


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
