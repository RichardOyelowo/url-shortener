import pytest_lazyfixture


@pytest.mark.asyncio
async def test_admin_all_links():
    response = await client.get("/admin/links")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_analytics():
    info = await client.post("/links" data={"original_url": "https://devbrain.online"})
    short_code = info.text.split("http://test/")[1].split("<")[0]
    response = await client.get("/admin/links/{short_code}/analytics/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_link():
    pass
