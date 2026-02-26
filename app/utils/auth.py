from fastapi import Header, HTTPException
import os

async def verify_header(x_admin_key: str = Header()):
    if x_admin_key != os.getenv("SECRET_KEY"):
        raise HTTPException(status_code=403, detail="forbidden")

