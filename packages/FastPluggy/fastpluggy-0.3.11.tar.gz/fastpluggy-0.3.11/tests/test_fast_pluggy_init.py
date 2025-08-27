import pytest
from fastapi.testclient import TestClient

from .conftest import get_auth_headers


@pytest.mark.asyncio
async def test_root(app_with_db):
    """Test the health check endpoint."""
    app, fast_pluggy = app_with_db

    with TestClient(app=app, base_url="http://testserver") as client:
        response = client.get("/admin", headers=get_auth_headers())
    assert response.status_code == 200


def test_menu_manager_initialization(app_with_db):
    """Test if the menu manager is initialized correctly."""
    app, fast_pluggy = app_with_db

    menu_manager = app.state.menu_manager
    assert menu_manager is not None
    assert menu_manager.show_empty_menu_entries is True


def test_plugin_manager_initialization(app_with_db):
    """Test if the plugin manager is initialized correctly."""
    app, fast_pluggy = app_with_db

    plugin_manager = app.state.fastpluggy.get_manager()
    assert plugin_manager is not None
    assert isinstance(plugin_manager.modules, dict)


# @pytest.mark.asyncio
# async def test_custom_exception_handler(app_with_db: FastAPI):
#     """Test custom exception handler for unexpected errors."""
#     @app_with_db.get("/error")
#     async def raise_error():
#         raise ValueError("Test Error")
#
#     async with AsyncClient(app=app_with_db, base_url="http://testserver") as client:
#         response = await client.get("/error", headers=get_auth_headers())
#     assert response.status_code == 500
#     assert "Test Error" in response.text

# def test_admin_user_creation(app_with_db):
#     """Test if the default admin user is created when no users exist."""
#     app, fast_pluggy = app_with_db
#     db = fast_pluggy.db
#
#     all_user = db.query(BaseUser).all()
#     print(all_user)
#     user_count = db.query(BaseUser).count()
#     #assert user_count == 1
#     # admin_user = db.query(User).first()
#     # assert admin_user.username == "admin"
