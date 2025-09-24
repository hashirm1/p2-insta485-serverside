"""Post views."""
import flask
import insta485
import arrow
import pathlib
import uuid
import os

LOGGER = flask.logging.create_logger(insta485.app)

@insta485.app.route("/posts/<postid_url_slug>/")
def show_post(postid_url_slug):
    """Display single post page."""
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    
    logname = flask.session['logname']
    connection = insta485.model.get_db()
    
    # Get post
    post = connection.execute(
        """
        SELECT posts.postid, posts.filename, posts.owner, posts.created,
               users.filename AS owner_img
        FROM posts
        JOIN users ON posts.owner = users.username
        WHERE posts.postid = ?
        """,
        (postid_url_slug,)
    ).fetchone()
    
    if post is None:
        flask.abort(404)
    
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
            "commentid": c["commentid"],
            "owner": c["owner"],
            "text": c["text"],
            "owner_show_delete": c["owner"] == logname
        })
    
    # Build post object
    post_data = {
        "postid": postid,
        "owner": post["owner"],
        "owner_img_url": "/uploads/" + post["owner_img"],
        "img_url": "/uploads/" + post["filename"],
        "timestamp": arrow.get(post["created"]).humanize(),
        "likes": like_count,
        "user_liked": user_liked,
        "comments": comments,
        "owner_show_delete": post["owner"] == logname
    }
    
    context = {"logname": logname, "post": post_data}
    return flask.render_template("post.html", **context)

@insta485.app.route("/posts/", methods=["POST"])
def update_posts():
    """Handle post operations."""
    if 'logname' not in flask.session:
        flask.abort(403)
    
    logname = flask.session['logname']
    connection = insta485.model.get_db()
    operation = flask.request.form["operation"]
    target = flask.request.args.get("target", flask.url_for("show_user", user_url_slug=logname))
    
    LOGGER.debug("operation = %s", operation)
    
    if operation == "create":
        # Check if file is provided
        if 'file' not in flask.request.files or flask.request.files['file'].filename == '':
            flask.abort(400)
        
        fileobj = flask.request.files["file"]
        filename = fileobj.filename
        
        # Generate UUID filename
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"
        
        # Save file
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)
        
        # Insert into database
        connection.execute(
            "INSERT INTO posts (filename, owner) VALUES (?, ?)",
            (uuid_basename, logname)
        )
        connection.commit()
        
    elif operation == "delete":
        postid = flask.request.form["postid"]
        
        # Check if post exists and is owned by user
        post = connection.execute(
            "SELECT filename, owner FROM posts WHERE postid = ?",
            (postid,)
        ).fetchone()
        
        if post is None or post["owner"] != logname:
            flask.abort(403)
        
        # Delete file
        filepath = insta485.app.config["UPLOAD_FOLDER"]/post["filename"]
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Delete from database (CASCADE will handle comments, likes)
        connection.execute("DELETE FROM posts WHERE postid = ?", (postid,))
        connection.commit()
    
    return flask.redirect(target)