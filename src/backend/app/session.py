import random

sessions = {}

def create(username):
    session_id = "".join(chr(random.randrange(33, 126)) for _ in range(16))
    sessions[session_id] = username
    return session_id

def remove(session_id):
    if session_id in sessions:
        del sessions[session_id]
        return 1
    else:
        return 0

def check(session_id):
    username = sessions.get(session_id)
    if username:
        return username
    remove(session_id)
    return 0

def get_all():
    return sessions