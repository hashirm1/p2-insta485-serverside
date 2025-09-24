# insta485/views/accounts.py
"""Account management views."""
import flask
import insta485
import hashlib
import uuid
import pathlib
import os


@insta485.app.route("/accounts/login/")
def show_login():
    """Display login page."""
    if 'logname' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template("login.html")

@insta485.app.route("/accounts/create/")
def show_create():
    """Display create account page."""
    if 'logname' in flask.session:
        return flask.redirect(flask.url_for('show_edit'))
    
    return flask.render_template("create.html")

@insta485.app.route("/accounts/delete/")
def show_delete():
    """Display delete account page."""
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    
    logname = flask.session['logname']
    context = {"logname": logname}
    return flask.render_template("delete.html", **context)

@insta485.app.route("/accounts/edit/")
def show_edit():
    """Display edit account page."""
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    
    logname = flask.session['logname']
    connection = insta485.model.get_db()
    
    user = connection.execute(
        "SELECT username, fullname, email, filename FROM users WHERE username = ?",
        (logname,)
    ).fetchone()
    
    context = {
        "logname": logname,
        "fullname": user["fullname"],
        "email": user["email"],
        "filename": user["filename"]
    }
    
    return flask.render_template("edit.html", **context)

@insta485.app.route("/accounts/password/")
def show_password():
    """Display password change page."""
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    
    context = {"logname": flask.session['logname']}
    return flask.render_template("password.html", **context)

@insta485.app.route("/accounts/auth/")
def auth():
    """Authentication endpoint for AWS deployment."""
    if 'logname' not in flask.session:
        flask.abort(403)
    return "", 200

@insta485.app.route("/accounts/logout/", methods=["POST"])
def logout():
    """Handle logout."""
    flask.session.clear()
    return flask.redirect(flask.url_for('show_login'))

def hash_password(password):
    """Hash password using SHA512."""
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    return "$".join([algorithm, salt, password_hash])

def verify_password(password, password_db_string):
    """Verify password against hash."""
    algorithm, salt, password_hash = password_db_string.split('$')
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    return password_hash == hash_obj.hexdigest()

@insta485.app.route("/accounts/", methods=["POST"])
def update_account():
    """Handle account operations."""
    operation = flask.request.form["operation"]
    target = flask.request.args.get("target", "/")
    connection = insta485.model.get_db()
    
    if operation == "login":
        username = flask.request.form.get("username", "").strip()
        password = flask.request.form.get("password", "").strip()
        
        if not username or not password:
            flask.abort(400)
        
        user = connection.execute(
            "SELECT username, password FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        
        if user is None or not verify_password(password, user["password"]):
            flask.abort(403)
        
        flask.session['logname'] = username
        
    elif operation == "create":
        # Get form data
        username = flask.request.form.get("username", "").strip()
        password = flask.request.form.get("password", "").strip()
        fullname = flask.request.form.get("fullname", "").strip()
        email = flask.request.form.get("email", "").strip()
        
        if not all([username, password, fullname, email]):
            flask.abort(400)
        
        if 'file' not in flask.request.files or flask.request.files['file'].filename == '':
            flask.abort(400)
        
        # Check if username exists
        existing_user = connection.execute(
            "SELECT username FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        
        if existing_user:
            flask.abort(409)
        
        # Handle file upload
        fileobj = flask.request.files["file"]
        filename = fileobj.filename
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)
        
        # Hash password
        password_hash = hash_password(password)
        
        # Insert user
        connection.execute(
            "INSERT INTO users (username, fullname, email, filename, password) VALUES (?, ?, ?, ?, ?)",
            (username, fullname, email, uuid_basename, password_hash)
        )
        connection.commit()
        
        flask.session['logname'] = username
        
    elif operation == "delete":
        if 'logname' not in flask.session:
            flask.abort(403)
        
        logname = flask.session['logname']
        
        # Get user's files
        user_files = connection.execute(
            "SELECT filename FROM users WHERE username = ?",
            (logname,)
        ).fetchone()
        
        post_files = connection.execute(
            "SELECT filename FROM posts WHERE owner = ?",
            (logname,)
        ).fetchall()
        
        # Delete user icon
        if user_files:
            filepath = insta485.app.config["UPLOAD_FOLDER"]/user_files["filename"]
            if os.path.exists(filepath):
                os.remove(filepath)
        
        # Delete post files
        for post in post_files:
            filepath = insta485.app.config["UPLOAD_FOLDER"]/post["filename"]
            if os.path.exists(filepath):
                os.remove(filepath)
        
        # Delete user from database (CASCADE will handle related records)
        connection.execute("DELETE FROM users WHERE username = ?", (logname,))
        connection.commit()
        
        flask.session.clear()
        target = flask.url_for('show_create')
        
    elif operation == "edit_account":
        if 'logname' not in flask.session:
            flask.abort(403)
        
        logname = flask.session['logname']
        fullname = flask.request.form.get("fullname", "").strip()
        email = flask.request.form.get("email", "").strip()
        
        if not fullname or not email:
            flask.abort(400)
        
        # Handle file upload if provided
        if 'file' in flask.request.files and flask.request.files['file'].filename != '':
            # Get old filename to delete
            old_file = connection.execute(
                "SELECT filename FROM users WHERE username = ?",
                (logname,)
            ).fetchone()
            
            fileobj = flask.request.files["file"]
            filename = fileobj.filename
            stem = uuid.uuid4().hex
            suffix = pathlib.Path(filename).suffix.lower()
            uuid_basename = f"{stem}{suffix}"
            path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
            fileobj.save(path)
            
            # Update with new file
            connection.execute(
                "UPDATE users SET fullname = ?, email = ?, filename = ? WHERE username = ?",
                (fullname, email, uuid_basename, logname)
            )
            
            # Delete old file
            if old_file:
                old_filepath = insta485.app.config["UPLOAD_FOLDER"]/old_file["filename"]
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
        else:
            # Update without changing file
            connection.execute(
                "UPDATE users SET fullname = ?, email = ? WHERE username = ?",
                (fullname, email, logname)
            )
        
        connection.commit()
        
    elif operation == "update_password":
        if 'logname' not in flask.session:
            flask.abort(403)
        
        logname = flask.session['logname']
        password = flask.request.form.get("password", "").strip()
        new_password1 = flask.request.form.get("new_password1", "").strip()
        new_password2 = flask.request.form.get("new_password2", "").strip()
        
        if not all([password, new_password1, new_password2]):
            flask.abort(400)
        
        # Verify current password
        user = connection.execute(
            "SELECT password FROM users WHERE username = ?",
            (logname,)
        ).fetchone()
        
        if not verify_password(password, user["password"]):
            flask.abort(403)
        
        # Verify new passwords match
        if new_password1 != new_password2:
            flask.abort(401)
        
        # Update password
        new_password_hash = hash_password(new_password1)
        connection.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (new_password_hash, logname)
        )
        connection.commit()
    
    return flask.redirect(target)