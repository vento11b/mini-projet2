from flask import Flask, request, Response,send_from_directory
from app import users, session
#from urllib import urlencode # -> python2 
from urllib.parse import urlencode # -> python3

flask = Flask(__name__)

@flask.route("/src/frontend/<path:file>")
def src(file):
    return send_from_directory("../frontend",file)

@flask.route("/")
def index():
    resp = Response()
    resp.status_code = 302
    resp.headers["Location"] = "/app"
    return resp

@flask.route("/app", methods=["GET"])
def app():
    resp = Response()
    
    # Si la cookie 'session_id' est valide
    session_id = request.cookies.get('session_id')
    username = session.check_session(session_id)
    if session_id and username:
        # Envoyer page html:
        resp.data = open("src/frontend/app/app.html", "r").read()
    else:
        # Redireiger vers page de identification:
        resp.status_code = 302
        resp.delete_cookie("session_id")
        resp.headers["Location"] = "/connexion"

    return resp

@flask.route("/app/user/<dst_username>/<message>", methods=["POST"])
def user(dst_username, message):
    # Gestion de chats privees
    pass

@flask.route("/app/channel", methods=["POST"])
def channel():
    # Gestion de salons
    pass

@flask.route("/app/profil", methods=["POST"])
def profile():
    # Gestion de compte
    pass

@flask.route("/inscription", methods=["GET", "POST"])
@flask.route("/inscription/inscription.html", methods=["GET", "POST"])
def inscription():
    resp = Response()
    # Si la methode de la requete est GET:
    if request.method == "GET":

        # Envoyer page HTML
        session_id = request.cookies.get("session_id")
        if session_id:
            # Si la cookie 'session_id' est valide, redireiger vers l'application:

            resp.status_code = 302
            resp.location = "/app"
        else:
            resp.data = open("src/frontend/inscription/inscription.html", "r").read()

    # Si la methode de la requete est POST:
    else:
        resp.content_type = "application/json"
        resp.status_code = 302

        # Recevoir les donnes pour l'inscription:
        username, password = request.form.get("username"), request.form.get("password")
        print(username, password)

        if users.check_password(password):
            if users.check_username(username):
                # Creer utilisateur
                if users.create_user(username, password):
                    ## Creer une session
                    #session_id = session.create_session(username)
                    ## Creer la cookie
                    #resp.set_cookie("session_id", session_id)
                    print("success")
                    resp.location = "/connexion"

                else:
                    print("error")
                    error = {"error": "Erreur inconnue"}
                    resp.location = "/inscription?"+urlencode(error)
            else:
                print("error user unavailable")
                error = {"error": "L'utilisateur existe deja"}
                resp.location = "/inscription?"+urlencode(error)
        else:
            print("error incompatible password")
            error = {"error": "Le mot de passe ne remplit pas les conditions"}
            resp.location = "/inscription?"+urlencode(error)
    
        print(users.list_users())

    return resp

@flask.route("/connexion", methods=["GET", "POST"])
@flask.route("/connexion/connexion.html", methods=["GET", "POST"])
def connexion():
    resp = Response()
    # Si la methode de la requete est GET:
    if request.method == "GET":

        # Envoyer page HTML
        session_id = request.cookies.get("session_id")
        if session_id:
            # Si la cookie 'session_id' est valide, redireiger vers l'application:

            resp.status_code = 302
            resp.location = "/app"
        else:
            resp.data = open("src/frontend/connexion/connexion.html", "r").read()

    # Si la methode de la requete est POST:
    else:
        resp.content_type = "application/json"
        resp.status_code = 302

        # Recevoir les donnes pour l'inscription:
        username, password = request.form.get("username"), request.form.get("password")
        print(username,password)

        if users.check_credentials(username, password):
            # Creer une session
            session_id = session.create_session(username)
            # Creer la cookie
            resp.set_cookie("session_id", session_id)
            resp.location = "/src/frontend/app/app.html"
        else:
            error = {"error": "Le nom d\'utilisateur ou le mot de passe est incorrect"}
            resp.location = "/connexion?"+urlencode(error)

    return resp

if __name__ == '__main__':
    flask.debug = True
    flask.run()