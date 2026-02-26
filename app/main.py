from app.utils import verify_header
from fastapi import FastAPI, Depends
from app.routers import router, admin_router


app = FastAPI()

app.include_router(admin_router, dependencies=[Depends(verify_header)])
app.include_router(router)


@app.get("/")
async def index():
    return {"name": "welcome here"}
