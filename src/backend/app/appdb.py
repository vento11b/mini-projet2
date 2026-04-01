import sqlite3, hashlib, sys
import inspect

DB_FILE = "src/backend/app/Toki.db"
DEBUG = 0
DEFAULT_CONDITIONS = [lambda passwd: len(passwd) >= 8,
                    lambda pw: any([c.isupper() for c in pw]),
                    lambda pw: any([c.islower() for c in pw]),
                    lambda pw: any([c.isdigit() for c in pw]),
                    lambda pw: any([c in "!@#$%^&*" for c in pw])]



conn = sqlite3.connect(DB_FILE, check_same_thread=False)

def debug(*args, **kwargs):
    if DEBUG: print(args, kwargs)

def check_credentials(username, password):
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users WHERE username = ? AND password = ?", (username, hashlib.sha256(password.encode()).hexdigest()))    
    return (len(cursor.fetchall())==1, "")

def username_exist(username):
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    return (len(cursor.fetchall()), "")

def channel_exist(channel):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM channels WHERE name = ?", (channel,))
    return (len(cursor.fetchall())>0, "")

def check_password(password, conditions=None):
    #debug("Checking password: ->")
    if conditions is None:
        conditions = DEFAULT_CONDITIONS

    return all([c(password) for c in conditions])


def add_user(username, password):
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users(username, password) VALUES (?, ?)", (username, hashlib.sha256(password.encode()).hexdigest()))
        conn.commit()
    except sqlite3.Error as er:
        return (0, str(er))
    
    return (1, "")


def get_usernames():
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username FROM users;")
    except sqlite3.Error as er:
        return (0, str(er))
    return (1, [username[0] for username in cursor.fetchall()])

def get_channels():
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM channels;")
    except sqlite3.Error as er:
        return (0, str(er))
    return (1, [channel[0] for channel in cursor.fetchall()])


def get_friends(username):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT t1.friend FROM friends t1 JOIN friends t2 ON t1.username = t2.friend AND t1.friend = t2.username WHERE t1.username=?", (username,))
    except sqlite3.Error as er:
        return (0, str(er))
    return (1, [friend[0] for friend in cursor.fetchall()])

def get_friend_requests(username):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT t1.username, t1.friend FROM friends t1 WHERE NOT EXISTS ( SELECT 1 FROM friends t2 WHERE t2.username = t1.friend AND t2.friend = t1.username) AND t1.friend=?;", (username,))
    except sqlite3.Error as er:
        return (0, str(er))
    
    return (1, [friend[0] for friend in cursor.fetchall()])

def get_user_channels(username):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT channel FROM channel_members WHERE username=?;", (username,))
    except sqlite3.Error as er:
        return (0, str(er))
    return (1, [channel[0] for channel in cursor.fetchall()])

def add_friend(username, friend):
    cursor = conn.cursor()
    try:
        debug("adding friend", friend)
        cursor.execute("INSERT INTO friends (username, friend) VALUES (?, ?);", (username, friend))
        conn.commit()
        return (1, "")

    except sqlite3.Error as er:
        return (0, str(er))
    

def join_channel(username, channel):
    cursor = conn.cursor()
    try:
        if not channel_exist(channel)[0]:
            debug(username, "creating", channel)
            cursor.execute("INSERT INTO channels (name, admin) VALUES (?, ?);", (channel, username))
        debug(username, "joining", channel)
        cursor.execute("INSERT INTO channel_members (channel, username) VALUES (?, ?);", (channel, username))
        conn.commit()

    except sqlite3.Error as er:
        return (0, str(er))
    
    return (1, "")

def get_private_chat_history(username, friend):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username, message, timestamp FROM private_messages WHERE private_room=?;", ("".join(sorted([username, friend])),))
    except sqlite3.Error as er:
        return (0, str(er))
    return (1 ,[message for message in cursor.fetchall()])

def get_channel_chat_history(channel):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username, message, timestamp FROM channel_messages WHERE channel=?;", (channel,))
    except sqlite3.Error as er:
        return (0, str(er))
    return (1, [message for message in cursor.fetchall()])

def send_friend(username, friend, message):
    cursor = conn.cursor()
    try:
        if friend in get_friends(username)[1]:
            cursor.execute("INSERT INTO private_messages (private_room, username, message, timestamp) VALUES (?, ?, ?,  datetime('now'));", ("".join(sorted([username, friend])), username, message))
            conn.commit()
        else:
            return (0, "not friends")
    except sqlite3.Error as er:
        return (0, str(er))
    
    return (1, "")

def send_channel(username, channel, message):
    cursor = conn.cursor()
    try:
        debug("")
        cursor.execute("INSERT INTO channel_messages (channel, username, message, timestamp) VALUES (?, ?, ?,  datetime('now'));", (channel, username, message))
        conn.commit()

    except sqlite3.Error as er:
        return (0, str(er))
    
    return (1, "")

def reset_db():
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS users;")
    cursor.execute("DROP TABLE IF EXISTS friends;")
    cursor.execute("DROP TABLE IF EXISTS channels;")
    cursor.execute("DROP TABLE IF EXISTS channel_messages;")
    cursor.execute("DROP TABLE IF EXISTS private_messages;")
    cursor.execute("DROP TABLE IF EXISTS channel_members;")

    conn.execute("PRAGMA foreign_keys = ON;")
    
    cursor.execute("CREATE TABLE users(username TEXT PRIMARY KEY, password TEXT);")
    cursor.execute("CREATE TABLE friends(username TEXT, friend TEXT, CHECK (username != friend), PRIMARY KEY (username, friend), FOREIGN KEY(username) REFERENCES users(username), FOREIGN KEY(friend) REFERENCES users(username));")
    cursor.execute("CREATE TABLE channels(name TEXT PRIMARY KEY, admin TEXT NOT NULL, FOREIGN KEY(admin) REFERENCES users(username));")
    cursor.execute("CREATE TABLE channel_messages(channel TEXT, username TEXT, message TEXT, timestamp TEXT, FOREIGN KEY(channel) REFERENCES channels(name), FOREIGN KEY(username) REFERENCES users(username));")
    cursor.execute("CREATE TABLE private_messages(private_room TEXT, username TEXT, message TEXT, timestamp TEXT);")
    cursor.execute("CREATE TABLE channel_members(channel TEXT, username TEXT, PRIMARY KEY (channel, username), FOREIGN KEY(channel) REFERENCES channels(name));")
    
    
    conn.commit()

    debug("db reseted.")




if __name__ == "__main__":
    DEBUG = 1
    
    if "--reset" in sys.argv[1:]:
        reset_db()