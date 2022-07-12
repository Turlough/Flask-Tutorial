import pytest
from flask import g, session
from flaskr.db import get_db


def test_register_get(client, app):
    assert client.get('/auth/register').status_code == 200


def test_register_redirects_to_login(client, app):
    response = client.post(
            '/auth/register',
            data={'username': 'a', 'password': 'a'}
    )
    assert response.headers['Location'] == '/auth/login'


def test_register_inserts_user_to_db(client, app):
    client.post(
            '/auth/register',
            data={'username': 'a', 'password': 'a'}
    )
    with app.app_context():
        assert get_db().execute(
                "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None


# # @pytest.mark.parametrize(('username', 'password', 'message'), (
# #     ('', '', b'Username is required.'),
# #     ('a', '', b'Password is required.'),
# #     ('test', 'test', b'already registered'),
# # ))
# def test_register_validate_input(client):
#     response = client.post(
#         '/auth/register',
#         # data={'username': username, 'password': password}
#         data={'username': '', 'password': 'b'}
#     )
#     print(response.status_code)
#     # assert 'Username is required' in response.data

