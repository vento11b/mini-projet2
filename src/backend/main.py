from flask import Flask, request, Response,send_from_directory, redirect, g
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
    return redirect("/app")

@flask.before_request
def allapp():
    if request.path.startswith('/app'):
        session_id = request.cookies.get('session_id')
        username = session.check(session_id)
        if not (session_id and username):
            if request.path=="/app":
                return redirect('/connexion')
            g.username = username
            g.session_id = session_id
            return {"status": 0, "info": "Le cookie est manquant ou incorrect"}

@flask.route("/app", methods=["GET"])
def app():
    return send_from_directory("../frontend/app","app.html")

@flask.route("/app/ami/envoyer/<friend>/<message>", methods=["POST"])
def send_friend(friend, message):
    # Gestion de chats privees
    session_id, username = request.cookies.get('session_id'), session.check(session_id)
    if session_id and username:
        resp = appdb.send_private(username, friend, message)
        return {"status": resp[0], "info": resp[1]}
    else:
        {"status": 0, "info": "Le cookie est manquant ou incorrect"}

@flask.route("/app/ami/messages/<friend>", methods=["POST"])
def get_private_mesages(friend):
    # Gestion de chats privees
    session_id, username = request.cookies.get('session_id'), session.check(session_id)
    if session_id and username:
        resp = appdb.get_private_chat_history(username, friend)
        return {"status": resp[0], "info": resp[1]}
    else:
        {"status": 0, "info": "Le cookie est manquant ou incorrect"}

@flask.route("/app/salon/envoyer/<channel>/<message>", methods=["POST"])
def send_channel(channel, message):
    # Gestion de salons
    session_id, username = request.cookies.get('session_id'), session.check(session_id)
    if session_id and username:
        resp = appdb.send_channel(username, channel, message)
        return {"status": resp[0], "info": resp[1]}
    else:
        {"status": 0, "info": "Le cookie est manquant ou incorrect"}

@flask.route("/app/salon/messages/<channel>", methods=["POST"])
def get_channel_messages(channel):
    # Gestion de chats privees
    session_id, username = request.cookies.get('session_id'), session.check(session_id)
    if session_id and username:
        resp = appdb.get_channel_chat_history(channel)
        return {"status": resp[0], "info": resp[1]}
    else:
        {"status": 0, "info": "Le cookie est manquant ou incorrect"}

@flask.route("/app/info", methods=["POST"])
def info():
    return {"status": 1, "info": {"username": username, "amis": appdb.get_friends(username)[1], "requetes amis": appdb.get_friend_requests(username)[1], "salons": appdb.get_user_channels(username)[1]}}


@flask.route("/app/amis", methods=["POST"])
def get_friends():
    session_id, username = request.cookies.get('session_id'), session.check(session_id)
    if session_id and username:
        return {"status": 1, "data": appdb.get_friends(username)}
    else:
        return {"status": 0, "info": "Le cookie est manquant ou incorrect"}

@flask.route("/app/salons", methods=["POST"])
def get_channels():
    session_id, username = request.cookies.get('session_id'), session.check(session_id)
    if session_id and username:
        return {"status": 1, "data": appdb.get_user_channels(username)}
    else:
        return {"status": 0, "info": "Le cookie est manquant ou incorrect"}

@flask.route("/app/ajouter/<friend>", methods=["POST"])
def add_friend(friend):
    session_id, username = request.cookies.get('session_id'), session.check(session_id)
    if session_id and username:
        if appdb.add_friend(username, friend)!=0:
            return {"status": 1, "info": "Ami ajoute"}
        else:
            return {"status": 0, "info": "Impossible d'ajouter un ami"}
    else:
        return {"status": 0, "info": "Le cookie est manquant ou incorrect"}

@flask.route("/app/joindre/<channel>", methods=["POST"])
def join_channel(channel):
    session_id, username = request.cookies.get('session_id'), session.check(session_id)
    if session_id and username:
        resp = appdb.join_channel(username, channel)
        return {"status": resp[0], "info": resp[1]}
    else:
        return {"status": 0, "info": "Le cookie est manquant ou incorrect"}


@flask.route("/app/deconnexion", methods=["POST"])
def deconnexion():
    session_id, username = request.cookies.get('session_id'), session.check(session_id)
    if session_id and username:
        session.remove(session_id)
        return {"status": 1, "data": request.cookies.get('session_id')==None}
    return {"status": 0, "info": "Le cookie est manquant ou incorrect"}


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

        if appdb.check_password(password):
            if appdb.username_exist(username):
                # Creer utilisateur
                if appdb.add_user(username, password):
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
    
        print(appdb.get_usernames())

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

        if appdb.check_credentials(username, password):
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