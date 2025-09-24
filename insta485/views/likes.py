"""Likes views."""
import flask
import insta485

LOGGER = flask.logging.create_logger(insta485.app)

@insta485.app.route("/likes/", methods=["POST"])
def update_likes():
    """Handle like/unlike operations."""
    if 'logname' not in flask.session:
        flask.abort(403)
    
    logname = flask.session['logname']
    connection = insta485.model.get_db()
    operation = flask.request.form["operation"]
    postid = flask.request.form["postid"]
    target = flask.request.args.get("target", "/")
    
    LOGGER.debug("operation = %s", operation)
    LOGGER.debug("postid = %s", postid)
    
    if operation == "like":
        # Check if already liked
        existing_like = connection.execute(
            "SELECT * FROM likes WHERE owner = ? AND postid = ?",
            (logname, postid)
        ).fetchone()
        
        if existing_like:
            flask.abort(409)
        
        connection.execute(
            "INSERT INTO likes (owner, postid) VALUES (?, ?)",
            (logname, postid)
        )
        
    elif operation == "unlike":
        # Check if not liked
        existing_like = connection.execute(
            "SELECT * FROM likes WHERE owner = ? AND postid = ?",
            (logname, postid)
        ).fetchone()
        
        if not existing_like:
            flask.abort(409)
        
        connection.execute(
            "DELETE FROM likes WHERE owner = ? AND postid = ?",
            (logname, postid)
        )
    
    connection.commit()
    return flask.redirect(target)
