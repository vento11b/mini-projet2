import sqlite3, hashlib, sys
import inspect

DB_FILE = "src/backend/app/Toki.db"
DEBUG = 0
DEFAULT_CONDITIONS = [lambda passwd: len(passwd) >= 8,
                    lambda pw: any([c.isupper() for c in pw]),
                    lambda pw: any([c.islower() for c in pw]),
                    lambda pw: any([c.isdigit() for c in pw]),
                    lambda pw: any([c in "!@#$%^&*" for c in pw])]

if __name__ == "__main__":
    DEBUG = 1


conn = sqlite3.connect(DB_FILE, check_same_thread=False)


def debug(*args, **kwargs):
    if DEBUG: print(args, kwargs)



def check_credentials(username, password):
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users WHERE username = ? AND password = ?", (username, hashlib.sha256(password.encode()).hexdigest()))    
    return len(cursor.fetchall())==1

def username_exist(username):
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    return len(cursor.fetchall())==0

def check_password(password, conditions=None):
    debug("Checking password: ->")
    if conditions is None:
        conditions = DEFAULT_CONDITIONS
        
    for c in conditions:
        debug(c(password))

    return all([c(password) for c in conditions])


def add_user(username, password):
    cursor = conn.cursor()
    if username_exist(username) and check_password(password):
        cursor.execute("INSERT INTO users(username, password) VALUES (?, ?)", (username, hashlib.sha256(password.encode()).hexdigest()))
        conn.commit()
        debug(cursor.fetchall())
        return 1
    else:
        debug("username_exist('", username, "')", username_exist(username), "check_password('", password, "')", check_password(password), "'", sep="")
        return 0


def get_usernames():
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    return [user[0].encode() for user in cursor.fetchall()]

def get_channels(username):
    cursor = conn.cursor()
    cursor.execute("SELECT channel FROM channel_members WHERE username=?", (username,))
    return [channel[0] for channel in cursor.fetchall()]

def get_user_channels(username):
    cursor = conn.cursor()
    cursor.execute("SELECT channel FROM channel_members WHERE username=?", (username,))
    return [channel[0] for channel in cursor.fetchall()]



def get_friends(username):
    cursor = conn.cursor()
    cursor.execute("SELECT friend FROM friends WHERE username=? AND state=1", (username,))
    return [friend[0] for friend in cursor.fetchall()]

def get_friend_requests(username):
    cursor = conn.cursor()
    cursor.execute("SELECT friend FROM friends WHERE username=? AND state=0", (username,))
    return [friend[0] for friend in cursor.fetchall()]

def add_friend(username, friend):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO friends (username, friend, state) VALUES (?, ?, 0);", (username,friend))
    conn.commit()
    return friend[0] in get_friend_requests(username)


def reset_db():
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS users;")
    cursor.execute("CREATE TABLE users(username TEXT PRIMARY KEY, password TEXT);")

    cursor.execute("DROP TABLE IF EXISTS friends;")
    cursor.execute("CREATE TABLE friends(username TEXT, friend TEXT, state INT NOT NULL DEFAULT 0, PRIMARY KEY (username, friend), FOREIGN KEY(username) REFERENCES users(username), FOREIGN KEY(friend) REFERENCES users(username));")
    
    cursor.execute("DROP TABLE IF EXISTS channels;")
    cursor.execute("CREATE TABLE channels(name TEXT PRIMARY KEY)")
    
    cursor.execute("DROP TABLE IF EXISTS channel_members;")
    cursor.execute("CREATE TABLE channel_members(channel TEXT , username TEXT , role TEXT , PRIMARY KEY (channel, username), FOREIGN KEY(channel) REFERENCES channels(name));")
    
    cursor.execute("DROP TABLE IF EXISTS channel_messages;")
    cursor.execute("CREATE TABLE channel_messages(channel TEXT , username TEXT , timestamp TEXT, PRIMARY KEY (channel, username, timestamp));")
    
    conn.commit()

    debug("db reseted.")




if "--reset" in sys.argv[1:]:
    reset_db()