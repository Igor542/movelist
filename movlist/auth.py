import functools

import flask
import werkzeug.security

import movlist.db

bp = flask.Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if flask.g.user is None:
            return flask.redirect(flask.url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = flask.session.get("user_id")

    if user_id is None:
        flask.g.user = None
    else:
        flask.g.user = (
            movlist.db.get().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


@bp.route("/register", methods=("GET", "POST"))
def register():
    if flask.request.method == "POST":
        username = flask.request.form["username"]
        password = flask.request.form["password"]
        db = movlist.db.get()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif (
            db.execute("SELECT id FROM user WHERE username = ?", (username,)).fetchone()
            is not None
        ):
            error = f"User {username} is already registered."

        if error is None:
            db.execute(
                "INSERT INTO user (username, password) VALUES (?, ?)",
                (username, werkzeug.security.generate_password_hash(password)),
            )
            db.commit()
            return flask.redirect(flask.url_for("auth.login"))

        flask.flash(error)

    return flask.render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if flask.request.method == "POST":
        username = flask,request.form["username"]
        password = flask.request.form["password"]
        db = movlist.db.get()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not werkzeug.security.check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            flask.session.clear()
            flask.session["user_id"] = user["id"]
            return flask.redirect(flask.url_for("index"))

        flask.flash(error)

    return flask.render_template("auth/login.html")


@bp.route("/logout")
def logout():
    flask.session.clear()
    return flask.redirect(flask.url_for("index"))
