"""Insta485 index (main feed) view."""

import flask
import insta485
import arrow
import sqlite3

@insta485.app.route("/")
def show_index():
    # Hardcode logged-in user for now
    logname = "awdeorio"

    connection = insta485.model.get_db()

    # Who does logname follow?
    follows = connection.execute(
        "SELECT followee FROM following WHERE follower = ?",
        (logname,)
    ).fetchall()
    follow_names = [row["followee"] for row in follows] + [logname]

    # Get posts from these users
    posts = connection.execute(
        """
        SELECT posts.postid, posts.filename, posts.owner, posts.created,
               users.filename AS owner_img
        FROM posts
        JOIN users ON posts.owner = users.username
        WHERE posts.owner IN ({})
        ORDER BY posts.postid DESC
        """.format(",".join("?" * len(follow_names))),
        follow_names
    ).fetchall()

    # Build full post objects
    feed = []
    for post in posts:
        postid = post["postid"]

        # Likes
        like_rows = connection.execute(
            "SELECT owner FROM likes WHERE postid = ?",
            (postid,)
        ).fetchall()
        likes = [row["owner"] for row in like_rows]
        like_count = len(likes)
        user_liked = logname in likes

        # Comments
        comment_rows = connection.execute(
            """
            SELECT commentid, owner, text
            FROM comments
            WHERE postid = ?
            ORDER BY commentid ASC
            """,
            (postid,)
        ).fetchall()

        comments = []
        for c in comment_rows:
            comments.append({
                "owner": c["owner"],
                "text": c["text"]
            })

        # Assemble post dictionary
        feed.append({
            "postid": postid,
            "owner": post["owner"],
            "owner_img_url": "/uploads/" + post["owner_img"],
            "img_url": "/uploads/" + post["filename"],
            "timestamp": arrow.get(post["created"]).humanize(),
            "likes": like_count,
            "user_liked": user_liked,
            "comments": comments
        })

    context = {"logname": logname, "posts": feed}
    return flask.render_template("index.html", **context)
