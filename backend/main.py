from flask import Flask, request, Response,send_file
from app import db, session
#from markupsafe import escape


flask = Flask(__name__)

@flask.route("/src/<path:file>")
def src(file):
    return send_file(f"../frontend/{file}")


@flask.route("/app", methods=["GET"])
def app():
    resp = Response()
    
    # Si la cookie 'session_id' est valide
    if (session_id := request.cookies.get('session_id')) and (username := session.check_session(session_id)):
        # Envoyer page html:
        resp.data = open("./frontend/app/app.html", "r").read()
    else:
        # Redireiger vers page de identification:
        resp.status_code = 302
        resp.headers["Location"] = "/identifier"

    return resp

@flask.route("/app/user/<dst_username>/<message>", methods=["POST"])
def user(dst_username, message):
# Gestion de chats privees

@flask.route("/app/channel", methods=["POST"])
def channel():
# Gestion de salons

@flask.route("/app/profile", methods=["POST"])
def profile():
# Gestion de compte

@flask.route("/identifier", methods=["GET", "POST"])
def identifier():
    resp = Response()
    
    # Si la methode de la requete est GET:
    if request.method == "GET":

        # Envoyer page HTML
        if session_id := request.cookies.get("session_id"):
            # Si la cookie 'session_id' est valide, redireiger vers l'application:

            resp.status_code = 302
            resp.location = "/identifier"
        else:
            resp.data = open("./frontend/identifier/conexion.html", "r").read()

    # Si la methode de la requete est POST:
    else:
        
        # Recevoir les donnes pour conexion/inscription:
        username, password = request.json["username"], request.json["password"]
        if db.validate_user(username, password):
            # Si utilisateur et mot de passe sont corrects:
            
            # Creer une session
            session_id = session.create_session(username)
            resp.data = b"{'status': 1}"
            resp.content_type = "application/json"

            # Creer la cookie
            resp.set_cookie("session_id", session_id)
        else:
            resp.data = b"{'status': 0}"
            resp.content_type = "application/json"
    return resp


if __name__ == '__main__':
    flask.run()