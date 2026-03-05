import pytest


@pytest.mark.asyncio
async def test_create_link(client):
    response = await client.post("/links/", data={"original_url": "https://example.com"})
    assert response.status_code == 200
    assert "http://test/" in response.text


@pytest.mark.asyncio
async def test_load_link_success(client):
    response = await client.post("/links/", data={"original_url": "https://devbrain.online"})
    short_code = response.text.split("http://test/")[1].split("<")[0]
    info = await client.get(f"/{short_code}", follow_redirects=False)
    assert info.status_code == 302
    assert info.headers["location"] == "https://devbrain.online/"


@pytest.mark.asyncio
async def test_load_link_not_found(client):
    response = await client.get("/unexisting-ke_ywork", follow_redirects=False)
    assert response.status_code == 200
    


@pytest.mark.asyncio
async def test_create_duplicate_link(client):
    response = await client.post("/links/", data={"original_url": "https://businessdashboard.shop"})
    info = await client.post("/links/", data={"original_url": "https://businessdashboard.shop"})
    assert response.status_code == 200
    assert info.status_code == 200
    assert response.text == info.text
