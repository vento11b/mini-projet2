from flask import Flask, request, Response,send_from_directory, redirect, g
from app import appdb, session
import json, base64

#from urllib import urlencode # -> python2 
from urllib.parse import urlencode # -> python3

# def = fonction 


flask = Flask(__name__)

@flask.route("/favicon.ico")     # flask.route() est un decorateur qui associe une URL a une fonction et decorateur = une fonction qui modifie le comportement d'une autre fonction
def favicon():
    return send_from_directory("../frontend/ressources", "Toki-removebg-preview2.png")

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
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            if not file.mimetype.startswith('image/'):
                return {"status": 0, "info": "Seuls les fichiers image sont autorises"}
            # Leer y convertir a base64
            image_data = base64.b64encode(file.read()).decode('utf-8')
            message_type = 'image'
            message = "data:"+file.mimetype+";base64,"+image_data  # Formato para mostrar en HTML
        else:
            return {"status": 0, "info": "Image invalide"}
    else:
        data = request.get_json()
        if not data or "message" not in data:
            return {"status": 0, "info": "Message non fourni"}
        message = data["message"]
        message_type = 'text'
    
    resp = appdb.send_friend(g.username, friend, message, message_type)
    return {"status": resp[0], "info": resp[1]}

@flask.route("/app/ami/messages/<friend>", methods=["POST"])
def get_private_mesages(friend):
    # Gestion de chats privees
    resp = appdb.get_private_chat_history(g.username, friend)
    return {"status": resp[0], "info": resp[1]}

@flask.route("/app/salon/envoyer/<channel>", methods=["POST"])
def send_channel(channel):
    # Gestion de salons
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            if not file.mimetype.startswith('image/'):
                return {"status": 0, "info": "Seuls les fichiers image sont autorises"}
            image_data = base64.b64encode(file.read()).decode('utf-8')
            message_type = 'image'
            message = "data:"+file.mimetype+";base64,"+image_data
        else:
            return {"status": 0, "info": "Image invalide"}
    else:
        data = request.get_json()
        if not data or "message" not in data:
            return {"status": 0, "info": "Message vide"}
        message = data["message"]
        message_type = 'text'
    
    resp = appdb.send_channel(g.username, channel, message, message_type)
    return {"status": resp[0], "info": resp[1]}

@flask.route("/app/salon/messages/<channel>", methods=["POST"])
def get_channel_messages(channel):
    resp = appdb.get_channel_chat_history(channel)
    return {"status": resp[0], "info": resp[1]}

@flask.route("/app/salon/membres/<channel>", methods=["POST"])
def get_channel_members(channel):
    resp = appdb.get_channel_members(channel)
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
    resp = Response(content_type = "application/json", status = 302)
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
    resp = Response(content_type = "application/json", status = 302)
    
    # Recevoir les donnes pour l'inscription:
    username, password = request.form.get("username"), request.form.get("password")
    
    if appdb.check_credentials(username, password)[0]:  # Si les identifiants sont corrects
        session_id = session.create(username)           # Creer une session
        resp.set_cookie("session_id", session_id)       # Creer la cookie
        resp.location = "/app"
    else:
        error = {"error": "Le nom d\'utilisateur ou le mot de passe est incorrect"}
        resp.location = "/connexion?"+urlencode(error)  # Envoyer l'information de l'erreur dans la url

    return resp

if __name__ == '__main__':
    flask.debug = False
    flask.run(host='0.0.0.0', port=80)