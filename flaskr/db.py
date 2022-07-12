import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
        )
    g.db.row_factory = sqlite3.Row
    return g.db


# app.teardown_appcontext(close_db) passes an unused parameter to this function
# which causes an error unless a parameter is defined.
# Underscore will do for an unused parameter
def close_db(_):
    db = g.pop('db', None)
    print('close db', str(db))
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('UTF-8'))


@click.command('init-db')
@with_appcontext
def init_db_command() -> None:
    """
    Drop and rebuild tables
    :return: None
    """
    init_db()
    click.echo('New Database initialised')


def init_app(app):
    """
    Registers function with the app (close_db and init_db_command)
    :param app: the application
    :return: None
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
