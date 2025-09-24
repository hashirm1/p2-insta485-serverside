"""Explore view."""
import flask
import insta485

@insta485.app.route("/explore/")
def show_explore():
    """Display explore page."""
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    
    logname = flask.session['logname']
    connection = insta485.model.get_db()
    
    # Get users that logname is NOT following (excluding logname)
    users = connection.execute(
        """
        SELECT username, filename FROM users
        WHERE username != ? AND username NOT IN (
            SELECT followee FROM following WHERE follower = ?
        )
        """,
        (logname, logname)
    ).fetchall()
    
    not_following = []
    for user in users:
        not_following.append({
            "username": user["username"],
            "user_img_url": "/uploads/" + user["filename"]
        })
    
    context = {
        "logname": logname,
        "not_following": not_following
    }
    
    return flask.render_template("explore.html", **context)