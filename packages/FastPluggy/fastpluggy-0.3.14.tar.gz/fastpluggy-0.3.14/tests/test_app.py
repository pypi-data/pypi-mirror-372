# test_app.py

import pytest
from fastapi.testclient import TestClient

from .conftest import get_auth_headers


# @pytest.mark.asyncio
# async def test_list_users(app_with_db):
#     """
#     Test the endpoint for listing users.
#     """
#     app, fast_pluggy = app_with_db
#
#     with TestClient(app=app, base_url="http://testserver", follow_redirects=True) as client:
#         response = client.get("/admin/users", headers=get_auth_headers())
#     assert response.status_code == 200

@pytest.mark.parametrize("file_name", ["/static/css/styles.css", "/static/js/scripts.js",])  # Add your files
def test_static_files_serving(file_name, app_with_db):
    app, fast_pluggy = app_with_db

    with TestClient(app=app, base_url="http://testserver", follow_redirects=True) as client:
        response = client.get(file_name, headers=get_auth_headers())
    assert response.status_code == 200, f"File {file_name} not served properly"
    assert response.content, f"File {file_name} is empty"

# @pytest.mark.asyncio
# async def test_create_user(app_with_db, db_session):
#     """
#     Test the endpoint for creating a new user.
#     """
#     app, fast_pluggy = app_with_db
#     previous_user_count = db_session.query(BaseUser).count()
#
#     with TestClient(app=app, base_url="http://testserver", follow_redirects=True) as client:
#         response =  client.post(
#             "/admin/users/add", data={"username": "new_user", "password": "password_secure", "is_admin": False},
#             headers=get_auth_headers()
#         )
#     assert response.status_code == 200
#     user_count = db_session.query(BaseUser).count()
#     assert user_count == (previous_user_count + 1)
#
#     # TODO:Verify the new user in the database
