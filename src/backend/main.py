from flask import Flask, request, Response,send_from_directory
from app import users, session


flask = Flask(__name__)

@flask.route("/src/<path:file>")
def src(file):
    return send_from_directory("../frontend",file)


@flask.route("/app", methods=["GET"])
def app():
    resp = Response()
    
    # Si la cookie 'session_id' est valide
    if (session_id := request.cookies.get('session_id')) and (username := session.check_session(session_id)):
        # Envoyer page html:
        resp.data = open("src/frontend/app/app.html", "r").read()
    else:
        # Redireiger vers page de identification:
        resp.status_code = 302
        resp.headers["Location"] = "/identifier"

    return resp

@flask.route("/app/user/<dst_username>/<message>", methods=["POST"])
def user(dst_username, message):
    # Gestion de chats privees
    pass

@flask.route("/app/channel", methods=["POST"])
def channel():
    # Gestion de salons
    pass

@flask.route("/app/profile", methods=["POST"])
def profile():
    # Gestion de compte
    pass

@flask.route("/inscription", methods=["GET", "POST"])
def inscription():
    resp = Response()
    
    # Si la methode de la requete est GET:
    if request.method == "GET":

        # Envoyer page HTML
        if session_id := request.cookies.get("session_id"):
            # Si la cookie 'session_id' est valide, redireiger vers l'application:

            resp.status_code = 302
            resp.location = "/app"
        else:
            resp.data = open("src/frontend/inscription.html", "r").read()

    # Si la methode de la requete est POST:
    else:
        resp.data = {'status': 0, 'info': ''}
        resp.content_type = "application/json"
        resp.status_code = 302

        # Recevoir les donnes pour l'inscription:
        username, password = request.json["username"], request.json["password"]
            
        if users.check_password():
            if users.check_username():
                # Creer utilisateur
                if users.create_user(username, password):
                    ## Creer une session
                    #session_id = session.create_session(username)
                    ## Creer la cookie
                    #resp.set_cookie("session_id", session_id)
                    resp.data = {'status': 0, 'info': 'Compte cree.'}
                    resp.location = "/1"
                else:
                    resp.data = {'status': 0, 'info': 'Error dans la creation du compte'}
                    resp.location = "/inscription"
            else:
                resp.data = {'status': 0, 'info': 'Le nom d\'utilisateur n\'est pas disponible.'}
                resp.location = "/inscription"
        else:
            resp.data = {'status': 0, 'info': 'Le mot de passe ne remplit pas les conditions.'}
            resp.location = "/inscription"
    
    resp.data = str(resp.data).encode()
    
    return resp

@flask.route("/connexion", methods=["GET", "POST"])
def connexion():
    return
    resp = Response()

    # Creer une session
    session_id = session.create_session(username)
    # Creer la cookie
    resp.set_cookie("session_id", session_id)
    # Si la methode de la requete est GET:

    if request.method == "GET":

        
        if session_id := request.cookies.get("session_id"):
            # Si la cookie 'session_id' est valide, redireiger vers l'application:

            resp.status_code = 302
            resp.location = "/connexion"
        else:
            # Sinon envoyer page HTML
            resp.data = open("src/frontend/connexion.html", "r").read()

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