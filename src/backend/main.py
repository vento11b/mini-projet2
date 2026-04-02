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

@flask.route("/connexion")
def connexion():
    return send_from_directory("../frontend/connexion", "connexion.html")

@flask.route("/inscription")
def inscription():
    return send_from_directory("../frontend/inscription", "inscription.html")


@flask.before_request
def allapp():
    g.session_id = request.cookies.get('session_id')
    g.username = session.check(g.session_id)
    
    if not g.username:
        if request.path.startswith('/app') and request.path not in ["/app", "/app/connexion", "/app/inscription"]:
            return {"status": 0, "info": "Le cookie est manquant ou incorrect"}

        resp = Response()
        resp.status_code = 302
        if g.session_id:
            if g.session_id:
                resp.delete_cookie("session_id")
            if request.path == "/app":
                resp.location = "/connexion"
            else:
                resp.location = request.path
            return resp
        else:
            if request.path == "/app":
                resp.location = "/connexion"
                return resp
            
            
@flask.route("/app", methods=["GET"])
def app():
    return send_from_directory("../frontend/app","app.html")

@flask.route("/app/ami/envoyer/<friend>", methods=["POST"])
def send_friend(friend):
    data = request.get_json()
    if not data or "message" not in data:
        return {"status": 0, "info": "Mensaje no proporcionado"}

    message = data["message"]
    resp = appdb.send_friend(g.username, friend, message)
    return {"status": resp[0], "info": resp[1]}

@flask.route("/app/ami/messages/<friend>", methods=["POST"])
def get_private_mesages(friend):
    # Gestion de chats privees
    resp = appdb.get_private_chat_history(g.username, friend)
    return {"status": resp[0], "info": resp[1]}

@flask.route("/app/salon/envoyer/<channel>", methods=["POST"])
def send_channel(channel):
    # Gestion de salons
    data = request.get_json()
    if not data or "message" not in data:
        return {"status": 0, "info": "Message vide"}

    message = data["message"]
    resp = appdb.send_channel(g.username, channel, message)
    return {"status": resp[0], "info": resp[1]}

@flask.route("/app/salon/messages/<channel>", methods=["POST"])
def get_channel_messages(channel):
    # Gestion de chats privees
    resp = appdb.get_channel_chat_history(channel)
    return {"status": resp[0], "info": resp[1]}

@flask.route("/app/info", methods=["POST"])
def info():
    resp = {"username": g.username, "amis": appdb.get_friends(g.username)[1], "requetes_amis": appdb.get_friend_requests(g.username)[1], "salons": appdb.get_user_channels(g.username)[1]}
    return {"status": 1, "info": resp}

@flask.route("/app/amis", methods=["POST"])
def get_friends():
    resp = appdb.get_friends(g.username)
    return {"status": resp[0], "info": resp[1]}

@flask.route("/app/salons", methods=["POST"])
def get_channels():
    resp = appdb.get_user_channels(g.username)
    return {"status": resp[0], "info": resp[1]}

@flask.route("/app/ajouter/<friend>", methods=["POST"])
def add_friend(friend):
    resp =  appdb.add_friend(g.username, friend)
    return {"status": resp[0], "info": resp[1]}

@flask.route("/app/joindre/<channel>", methods=["POST"])
def join_channel(channel):
    resp = appdb.join_channel(g.username, channel)
    return {"status": resp[0], "info": resp[1]}


@flask.route("/app/deconnexion", methods=["POST"])
def deconnexion():
    session.remove(g.session_id)
    return {"status": request.cookies.get('session_id')==None, "info": ""}


@flask.route("/app/inscription", methods=["POST"])
def appinscription():
    resp = Response()
    resp.content_type = "application/json"
    resp.status_code = 302
    # Recevoir les donnes pour l'inscription:
    username, password = request.form.get("username"), request.form.get("password")

    if appdb.check_password(password):
        if appdb.username_exist(username):
            # Creer utilisateur
            if appdb.add_user(username, password):
                resp.location = "/connexion"
            else:
                error = {"error": "Erreur inconnue"}
                resp.location = "/inscription?"+urlencode(error)
        else:
            error = {"error": "L'utilisateur existe deja"}
            resp.location = "/inscription?"+urlencode(error)
    else:
        error = {"error": "Le mot de passe ne remplit pas les conditions"}
        resp.location = "/inscription?"+urlencode(error)


    return resp

@flask.route("/app/connexion", methods=["POST"])
def appconnexion():
    resp = Response()
    resp.content_type = "application/json"
    resp.status_code = 302

    # Recevoir les donnes pour l'inscription:
    username, password = request.form.get("username"), request.form.get("password")
    
    if appdb.check_credentials(username, password)[0]:
        # Creer une session
        session_id = session.create(username)
        # Creer la cookie
        resp.set_cookie("session_id", session_id)
        resp.location = "/app"
    else:
        error = {"error": "Le nom d\'utilisateur ou le mot de passe est incorrect"}
        resp.location = "/connexion?"+urlencode(error)

    return resp

if __name__ == '__main__':
    flask.debug = False
    flask.run()