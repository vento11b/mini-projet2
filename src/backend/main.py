from flask import Flask, request, Response,send_from_directory
from app import appdb, session
import json

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
    username = session.check(session_id)
    if session_id and username:
        # Envoyer page html:
        resp.data = open("src/frontend/app/app.html", "r").read()
    else:
        # Redireiger vers page de identification:
        resp.status_code = 302
        resp.delete_cookie("session_id")
        resp.headers["Location"] = "/connexion"

    return resp

@flask.route("/app/envoyer/<dst_username>/<message>", methods=["POST"])
def utilisateur(dst_username, message):
    # Gestion de chats privees
    pass


@flask.route("/app/compte", methods=["POST"])
def compte():
    session_id = request.cookies.get('session_id')
    username = session.check(session_id)
    if session_id and username:
        return {"status": 1, "info": [managedb.get_friends(username), managedb.get_channels(username)]}
    else:
        return {"status": 0, "info": "Le cookie est manquant ou incorrect"}

@flask.route("/app/amis", methods=["POST"])
def friends():
    session_id = request.cookies.get('session_id')
    username = session.check(session_id)
    if session_id and username:
        return {"status": 1, "info": managedb.get_friends(username)}
    else:
        return {"status": 0, "info": "Le cookie est manquant ou incorrect"}

@flask.route("/app/ajouter/<friend>", methods=["POST"])
def add_friend(friend):
    print(session.get_all())
    session_id = request.cookies.get('session_id')
    username = session.check(session_id)
    if session_id and username:
        if managedb.add_friend(username, friend)!=0:
            return {"status": 0, "info": "Ami ajoute"}
        else:
            return {"status": 0, "info": "Impossible d'ajouter un ami"}
    else:
        return {"status": 0, "info": "Le cookie est manquant ou incorrect"}

@flask.route("/app/deconnexion", methods=["POST"])
def deconnexion():
    session_id = request.cookies.get('session_id')
    username = session.check(session_id)
    if session_id and username:
        session.remove(session_id)
    #print(session.get_all(), request.cookies.get('session_id')!=None)
    return {"status": request.cookies.get('session_id')==None}


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

        if managedb.check_password(password):
            if managedb.check_username(username):
                # Creer utilisateur
                if managedb.add_user(username, password):
                    ## Creer une session
                    #session_id = session.create(username)
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
    
        print(managedb.list_users())

    return resp

@flask.route("/connexion", methods=["GET", "POST"])
@flask.route("/connexion/connexion.html", methods=["GET", "POST"])
def connexion():
    print(managedb.add_friend("vento", "caca"))
    print(managedb.add_friend("cac`fa", "vento"))
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

        if managedb.check_credentials(username, password):
            # Creer une session
            session_id = session.create(username)
            # Creer la cookie
            resp.set_cookie("session_id", session_id)
            resp.location = "/app"
        else:
            error = {"error": "Le nom d\'utilisateur ou le mot de passe est incorrect"}
            resp.location = "/connexion?"+urlencode(error)
    print(session.get_all())
    return resp

if __name__ == '__main__':
    flask.debug = True
    flask.run()