"""
Insta485 following views.

URLs include:
/following/
"""
import flask
import insta485


@insta485.app.route('/following/', methods=['POST'])
def update_following():
    """Handle follow/unfollow operations."""
    if 'logname' not in flask.session:
        flask.abort(403)
    
    logname = flask.session['logname']
    connection = insta485.model.get_db()
    operation = flask.request.form["operation"]
    username = flask.request.form["username"]
    target = flask.request.args.get("target", "/")
    
    if operation == "follow":
        # Check if already following
        existing_follow = connection.execute(
            "SELECT * FROM following WHERE username1 = ? AND username2 = ?",
            (logname, username)
        ).fetchone()
        
        if existing_follow:
            flask.abort(409)
        
        connection.execute(
            "INSERT INTO following (username1, username2) VALUES (?, ?)",
            (logname, username)
        )
        
    elif operation == "unfollow":
        # Check if not following
        existing_follow = connection.execute(
            "SELECT * FROM following WHERE username1 = ? AND username2 = ?",
            (logname, username)
        ).fetchone()
        
        if not existing_follow:
            flask.abort(409)
        
        connection.execute(
            "DELETE FROM following WHERE username1 = ? AND username2 = ?",
            (logname, username)
        )
    
    connection.commit()
    return flask.redirect(target)
