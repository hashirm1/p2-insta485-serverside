"""User profile views."""
import flask
import insta485

@insta485.app.route("/users/<user_url_slug>/")
def show_user(user_url_slug):
    """Display user profile page."""
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    
    logname = flask.session['logname']
    connection = insta485.model.get_db()
    
    # Check if user exists
    user = connection.execute(
        "SELECT username, fullname, email, filename FROM users WHERE username = ?",
        (user_url_slug,)
    ).fetchone()
    
    if user is None:
        flask.abort(404)
    
    # Get user's posts
    posts = connection.execute(
        "SELECT postid, filename FROM posts WHERE owner = ? ORDER BY postid DESC",
        (user_url_slug,)
    ).fetchall()
    
    # Get follower/following counts
    followers_count = connection.execute(
        "SELECT COUNT(*) as count FROM following WHERE followee = ?",
        (user_url_slug,)
    ).fetchone()['count']
    
    following_count = connection.execute(
        "SELECT COUNT(*) as count FROM following WHERE follower = ?",
        (user_url_slug,)
    ).fetchone()['count']
    
    # Check if logged in user follows this user
    following_relationship = ""
    if logname != user_url_slug:
        is_following = connection.execute(
            "SELECT * FROM following WHERE follower = ? AND followee = ?",
            (logname, user_url_slug)
        ).fetchone()
        following_relationship = "following" if is_following else "not following"
    
    context = {
        "logname": logname,
        "username": user_url_slug,
        "fullname": user["fullname"],
        "following": following_relationship,
        "posts": posts,
        "posts_count": len(posts),
        "followers": followers_count,
        "following_count": following_count,
        "user_img_url": "/uploads/" + user["filename"]
    }
    
    return flask.render_template("user.html", **context)

@insta485.app.route("/users/<user_url_slug>/followers/")
def show_followers(user_url_slug):
    """Display followers page."""
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    
    logname = flask.session['logname']
    connection = insta485.model.get_db()
    
    # Check if user exists
    user = connection.execute(
        "SELECT username FROM users WHERE username = ?",
        (user_url_slug,)
    ).fetchone()
    
    if user is None:
        flask.abort(404)
    
    # Get followers
    followers = connection.execute(
        """
        SELECT users.username, users.filename
        FROM users
        JOIN following ON users.username = following.follower
        WHERE following.followee = ?
        """,
        (user_url_slug,)
    ).fetchall()
    
    # Check relationships for each follower
    followers_list = []
    for follower in followers:
        username = follower["username"]
        relationship = ""
        if username != logname:
            is_following = connection.execute(
                "SELECT * FROM following WHERE follower = ? AND followee = ?",
                (logname, username)
            ).fetchone()
            relationship = "following" if is_following else "not following"
        
        followers_list.append({
            "username": username,
            "user_img_url": "/uploads/" + follower["filename"],
            "logname_follows_username": relationship
        })
    
    context = {
        "logname": logname,
        "followers": followers_list
    }
    
    return flask.render_template("followers.html", **context)

@insta485.app.route("/users/<user_url_slug>/following/")
def show_following(user_url_slug):
    """Display following page."""
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    
    logname = flask.session['logname']
    connection = insta485.model.get_db()
    
    # Check if user exists
    user = connection.execute(
        "SELECT username FROM users WHERE username = ?",
        (user_url_slug,)
    ).fetchone()
    
    if user is None:
        flask.abort(404)
    
    # Get following
    following = connection.execute(
        """
        SELECT users.username, users.filename
        FROM users
        JOIN following ON users.username = following.followee
        WHERE following.follower = ?
        """,
        (user_url_slug,)
    ).fetchall()
    
    # Check relationships
    following_list = []
    for follow in following:
        username = follow["username"]
        relationship = ""
        if username != logname:
            is_following = connection.execute(
                "SELECT * FROM following WHERE follower = ? AND followee = ?",
                (logname, username)
            ).fetchone()
            relationship = "following" if is_following else "not following"
        
        following_list.append({
            "username": username,
            "user_img_url": "/uploads/" + follow["filename"],
            "logname_follows_username": relationship
        })
    
    context = {
        "logname": logname,
        "following": following_list
    }
    
    return flask.render_template("following.html", **context)