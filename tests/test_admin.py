import pytest
from app.utils import decode_shortcode


@pytest.mark.asyncio
async def test_admin_all_links(client):
    response = await client.get("/api/admin/links")
    assert "links" in response.json()


@pytest.mark.asyncio
async def test_get_analytics(client):
    info = await client.post("/links/", data={"original_url": "https://devbrain.online"})
    short_code = info.text.split("http://test/")[1].split("<")[0]
    
    response = await client.get(f"/api/admin/links/{short_code}/analytics/")
    assert "analytics" in response.json()


@pytest.mark.asyncio
async def test_delete_link(client):
    info = await client.post("/links/", data={"original_url": "https://businessdashboard.shop"})
    short_code = info.text.split("http://test/")[1].split("<")[0]
    id = decode_shortcode(short_code)

    response = await client.delete(f"/api/admin/links/{id}")
    assert response.json()["message"] == "Link deleted"
