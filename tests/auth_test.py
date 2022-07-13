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


@pytest.mark.parametrize(('username', 'password', 'message'), (
        ('', '', b'Username is required.'),
        ('a', '', b'Password is required.'),
        ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
            '/auth/register',
            data={'username': username, 'password': password}
    )
    assert message in response.data


def test_login_get(client, auth):
    response = client.get('/auth/login')
    assert response.status_code == 200


def test_successful_login_redirects(client, auth):
    response = auth.login()
    assert response.status_code == 302
    assert response.headers['Location'] == '/auth/index'


def test_credentials_persist(client, auth):
    auth.login()
    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'

