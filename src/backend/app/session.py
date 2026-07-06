import random

sessions = {}

def create(username):       #fonction pour creer une session pour utilisateur
    session_id = "".join(chr(random.randrange(33, 126)) for _ in range(16))
    sessions[session_id] = username
    return session_id

def remove(session_id):     # fonction pour supprimer une session pour utlisateur 
    if session_id in sessions:
        del sessions[session_id]
        return 1
    else:
        return 0

def check(session_id):      # fonction pour verifier si une session est valide pour un utilisateur
    username = sessions.get(session_id)
    if username:
        return username
    remove(session_id)
    return 0

def get_all():      #fonction pour recuperer toutes les sessions actives
    return sessions