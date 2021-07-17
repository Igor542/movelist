import sqlite3

import click
import flask


def get():
    if "db" not in flask.g:
        flask.g.db = sqlite3.connect(
            flask.current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        flask.g.db.row_factory = sqlite3.Row
    return flask.g.db


def close_db(e=None):
    db = flask.g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get()
    with flask.current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command('init-db')
@flask.cli.with_appcontext
def init_db_command():
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
