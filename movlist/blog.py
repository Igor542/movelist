from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

import movlist.auth
import movlist.db

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    db = movlist.db.get()
    user_id = g.user['id'] if g.user else -1
    entries = db.execute(
        "SELECT l.id as list_id, m.id as movie_id, m.title, u.username, COALESCE(r.rating, 0) as user_rating, l.avg_rating, l.date_added"
        " FROM movie_list l"
        " LEFT JOIN user u ON l.user_id = u.id"
        " LEFT JOIN movie m ON l.movie_id = m.id"
        f" LEFT JOIN bridge_movie_user_rating r on l.movie_id = r.movie_id and r.user_id = {user_id}"
        " ORDER BY date_added DESC"
    ).fetchall()
    return render_template("blog/index.html", entries=entries)


def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = (
        movlist.db.get()
        .execute(
            "SELECT l.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        ).fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@movlist.auth.login_required
def create():
    """Create a new film for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        error = None

        # TODO: Check title before passing it to the database
        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = movlist.db.get()
            # check if movie exists in the database
            movie_exist_entry = db.execute(
                f"SELECT id FROM movie m WHERE m.title = \"{title}\""
            ).fetchone()
            if movie_exist_entry is None:
                db.execute(
                    f"INSERT INTO movie (title) VALUES (\"{title}\")",
                )
                movie_entry = db.execute(
                    f"SELECT id FROM movie m WHERE m.title = \"{title}\""
                ).fetchone()
                db.execute(
                    "INSERT INTO movie_list (movie_id, user_id) VALUES (?,?)",
                    (movie_entry["id"], g.user["id"]),
                )
                db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@movlist.auth.login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = movlist.db.get()
            db.execute(
                "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@movlist.auth.login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = movlist.db.get()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))
