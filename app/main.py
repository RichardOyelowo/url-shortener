from app.database import engine
from app.models import Link, Click
from app.utils import verify_header
from sqladmin import Admin, ModelView
from app.templates_config import templates
from fastapi.staticfiles import StaticFiles
from app.routers import router, admin_router
from fastapi import FastAPI, Depends, Request

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Admin Dashboard
admin = Admin(app, engine)
class LinkAdmin(ModelView, model=Link):
    column_list = [Link.id, Link.original_url, Link.short_code, Link.click_count, Link.created_at]

class ClickAdmin(ModelView, model=Click):
    column_list = [Click.id, Click.link_id, Click.created_at]

admin.add_view(LinkAdmin)
admin.add_view(ClickAdmin)


app.include_router(admin_router, dependencies=[Depends(verify_header)])
app.include_router(router)

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
