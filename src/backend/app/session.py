import random

sessions = {}

def create_session(username):
    session_id = "".join(chr(random.randrange(33, 126)) for _ in range(16))
    sessions[session_id] = username
    return session_id

def remove_session(session_id):
    if session_id in sessions:
        del sessions[session_id]
        return 1
    else:
        return 0

def check_session(session_id):
    session = sessions.get(session_id)
    if session != None:
        return session
    remove_session(session_id)
    return 0