from fastapi import FastAPI
from app.schemas import LinkCreate, LinkResponse

app = FastAPI()


@app.get("/shortcode")
async def load_link(url: LinkResponse.short_code):
    pass


@app.post("/links")
async def create_link(url: LinkCreate.original_url):
    pass

