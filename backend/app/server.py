from flask import Flask, request, Response
from markupsafe import escape


flask = Flask(__name__)


@flask.route("/app")
def app():
    username = request.cookies.get('username')
    if username is not None:
        return f"Hello, {escape(username)}!"
    else:
        r = Response()
        r.status_code = 302
        r.headers["Location"] = "/login"

@flask.route("/login")
def app():
    username = request.cookies.get('username')
    if username is not None:
        return f"Hello, {escape(username)}!"
    else:
        r = Response()
        r.status_code = 302
        r.headers["Location"] = "/login"

if __name__ == '__main__':
    flask.run()