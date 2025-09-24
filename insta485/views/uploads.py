"""Upload files view."""
import flask
import insta485
import os

@insta485.app.route("/uploads/<filename>")
def show_upload(filename):
    """Serve uploaded files."""
    if 'logname' not in flask.session:
        flask.abort(403)
    
    # Check if file exists
    filepath = insta485.app.config["UPLOAD_FOLDER"]/filename
    if not os.path.exists(filepath):
        flask.abort(404)
    
    return flask.send_from_directory(insta485.app.config["UPLOAD_FOLDER"], filename)