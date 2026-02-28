import os
from app.database import engine
from app.models import Link, Click
from app.utils import verify_header
from sqladmin import Admin, ModelView
from app.templates_config import templates
from fastapi.staticfiles import StaticFiles
from app.routers import router, admin_router
from fastapi import FastAPI, Depends, Request
from sqladmin.authentication import AuthenticationBackend

app = FastAPI()
app.mount("/assets", StaticFiles(directory="app/static"), name="static")


# Admin Dashboard
class LinkAdmin(ModelView, model=Link):
    column_list = [Link.id, Link.original_url, Link.short_code, Link.click_count, Link.created_at]

class ClickAdmin(ModelView, model=Click):
    column_list = [Click.id, Click.link_id, Click.created_at]


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        if form["username"] == "admin" and form["password"] == os.getenv("ADMIN_PASSWORD"):
            request.session["token"] = "authenticated"
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("token") == "authenticated"

authentication_backend = AdminAuth(secret_key=os.getenv("SECRET_KEY"))
admin = Admin(app, engine, authentication_backend=authentication_backend)


admin.add_view(LinkAdmin)
admin.add_view(ClickAdmin)


app.include_router(admin_router, dependencies=[Depends(verify_header)])
app.include_router(router)

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
