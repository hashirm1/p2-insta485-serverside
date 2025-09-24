"""Comments views."""
import flask
import insta485

@insta485.app.route("/comments/", methods=["POST"])
def update_comments():
    """Handle comment operations."""
    if 'logname' not in flask.session:
        flask.abort(403)
    
    logname = flask.session['logname']
    connection = insta485.model.get_db()
    operation = flask.request.form["operation"]
    target = flask.request.args.get("target", "/")
    
    if operation == "create":
        postid = flask.request.form["postid"]
        text = flask.request.form.get("text", "").strip()
        
        if not text:
            flask.abort(400)
        
        connection.execute(
            "INSERT INTO comments (owner, postid, text) VALUES (?, ?, ?)",
            (logname, postid, text)
        )
        
    elif operation == "delete":
        commentid = flask.request.form["commentid"]
        
        # Check if comment exists and is owned by user
        comment = connection.execute(
            "SELECT owner FROM comments WHERE commentid = ?",
            (commentid,)
        ).fetchone()
        
        if comment is None or comment["owner"] != logname:
            flask.abort(403)
        
        connection.execute("DELETE FROM comments WHERE commentid = ?", (commentid,))
    
    connection.commit()
    return flask.redirect(target)
