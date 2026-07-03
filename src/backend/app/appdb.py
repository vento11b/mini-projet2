# coding=latin-1
import sqlite3, hashlib, sys
import os.path

DB_FILE = "src/backend/app/Toki.db"
DEBUG = 0
DEFAULT_CONDITIONS = [lambda passwd: len(passwd) >= 8,   # condition pour les mots de passe au moins 8 caratères
                    lambda pw: any([c.isupper() for c in pw]),  # condition pour les mots de passe au moins une majuscule
                    lambda pw: any([c.islower() for c in pw]),  # condition pour les mots de passe au moins une minuscule
                    lambda pw: any([c.isdigit() for c in pw]),  # condition pour les mots de passe au moins un chffre 
                    lambda pw: any([c in "!@#$%^&*" for c in pw])]  # condition pour les mots de passe au moins un caractére special 


def debug(*args, **kwargs): # def = indique que on definie une fontion 
    if DEBUG: print(args, kwargs)

def check_credentials(username, password):      #fonction pour verifier les identifiants de l'utilisateur, prend en parametre le nom d'utilisateur et le mot de passe
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users WHERE username = ? AND password = ?", (username, hashlib.sha256(password.encode()).hexdigest()))    
    return (len(cursor.fetchall())==1, "")

def username_exist(username):       #fonction pour verifier si le nom d'utilisateur existe dans la bas de données, prend en parametre le nom d'utilisateur 
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,)) # cursor.execute permet d'envoyer une commande SQL a la base de données
    return (len(cursor.fetchall()), "")

def channel_exist(channel):     #fonction pour verifier si le nom du groupe/ canal existe dans la base de données
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM channels WHERE name = ?", (channel,))
    return (len(cursor.fetchall())>0, "")

def check_password(password, conditions=None):      # fonction qui verifie si le mot de passe respecte les conditons de securité
    #debug("Checking password: ->")
    if conditions is None:
        conditions = DEFAULT_CONDITIONS

    return all([c(password) for c in conditions])


def add_user(username, password):       # fonction pour ajouter un utilisateur dans la base de données
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users(username, password, created_at) VALUES (?, ?, datetime('now', 'localtime'))", (username, hashlib.sha256(password.encode()).hexdigest()))
        conn.commit()
    except sqlite3.Error as er:
        return (0, str(er))
    
    return (1, "")


def get_user_info(username):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username, created_at FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if not row:
            return (0, "Utilisateur non trouvé")
        return (1, {"username": row[0], "created_at": row[1]})
    except sqlite3.Error as er:
        return (0, str(er))


def get_usernames():        #fonction pour recuperer tous les noms d'utilisateurs dans la base de données
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username FROM users;")
    except sqlite3.Error as er:
        return (0, str(er))
    return (1, [username[0] for username in cursor.fetchall()])

def get_channels():     # fonction pour recuperer tous les noms de groupe/ canal dans la base de données
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM channels;")
    except sqlite3.Error as er:
        return (0, str(er))
    return (1, [channel[0] for channel in cursor.fetchall()])


def get_friends(username):      # fontion pour recuperer tous les amis d'un utilisateur dans la base de données 
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT t1.friend FROM friends t1 JOIN friends t2 ON t1.username = t2.friend AND t1.friend = t2.username WHERE t1.username=?", (username,))
    except sqlite3.Error as er:
        return (0, str(er))
    return (1, [friend[0] for friend in cursor.fetchall()])

def get_friend_requests(username):      #fonction pour recuperer toutes les demandes d'amis d'un utilisateur dans la base de données
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT t1.username, t1.friend FROM friends t1 WHERE NOT EXISTS ( SELECT 1 FROM friends t2 WHERE t2.username = t1.friend AND t2.friend = t1.username) AND t1.friend=?;", (username,))
    except sqlite3.Error as er:
        return (0, str(er))
    
    return (1, [friend[0] for friend in cursor.fetchall()])

def get_user_channels(username):        #fonction pour recuperer tous les groupes/ canaux d'un utlisateur dans la base de données
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT channel FROM channel_members WHERE username=?;", (username,))
    except sqlite3.Error as er:
        return (0, str(er))
    return (1, [channel[0] for channel in cursor.fetchall()])


def add_friend(username, friend):       #fonction pour ajouter un ami
    cursor = conn.cursor()
    try:
        debug("adding friend", friend)
        cursor.execute("INSERT INTO friends (username, friend) VALUES (?, ?);", (username, friend))
        conn.commit()
        return (1, "")

    except sqlite3.Error as er:
        return (0, str(er))
    

def join_channel(username, channel):        # fonction pour rejoindre un groupe/canal 
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

def get_private_chat_history(username, friend):     #fonction pour recuperer l'historique de chat prive entre deux utilisateur dans 
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, message, message_type, timestamp FROM private_messages WHERE private_room=?;", ("".join(sorted([username, friend])),))
    except sqlite3.Error as er:
        return (0, str(er))
    return (1 ,[message for message in cursor.fetchall()])

def get_channel_chat_history(channel):      #fonction pour recuperer l'historique de chat d'un groupe 
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, message, message_type, timestamp FROM channel_messages WHERE channel=?;", (channel,))
    except sqlite3.Error as er:
        return (0, str(er))
    return (1, [message for message in cursor.fetchall()])

def get_channel_members(channel):       #fonction pour recupere tous les membres d'un groupe 
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username FROM channel_members WHERE channel=?;", (channel,))
    except sqlite3.Error as er:
        return (0, str(er))
    return (1, [username for username in cursor.fetchall()])

def send_friend(username, friend, message, message_type='text'):        #fonction pour envoyer un message prive a un ami
    cursor = conn.cursor()
    try:
        if friend in get_friends(username)[1]:
            cursor.execute("INSERT INTO private_messages (private_room, username, message, message_type, timestamp) VALUES (?, ?, ?, ?, datetime('now', 'localtime'));", ("".join(sorted([username, friend])), username, message, message_type))
            conn.commit()
        else:
            return (0, "not friends")
    except sqlite3.Error as er:
        return (0, str(er))
    
    return (1, "")

def send_channel(username, channel, message, message_type='text'):
    cursor = conn.cursor()
    try:
        debug("")
        cursor.execute("INSERT INTO channel_messages (channel, username, message, message_type, timestamp) VALUES (?, ?, ?, ?, datetime('now', 'localtime'));", (channel, username, message, message_type))
        conn.commit()

    except sqlite3.Error as er:
        return (0, str(er))
    
    return (1, "")

def reset_db():
    conn.execute("PRAGMA foreign_keys = OFF;")  #
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS users;") # cursor.execute permet d'envoyer une commande SQL a la base de données
    cursor.execute("DROP TABLE IF EXISTS friends;")
    cursor.execute("DROP TABLE IF EXISTS channels;")
    cursor.execute("DROP TABLE IF EXISTS channel_messages;")
    cursor.execute("DROP TABLE IF EXISTS private_messages;")
    cursor.execute("DROP TABLE IF EXISTS channel_members;")

    conn.execute("PRAGMA foreign_keys = ON;")
    
    cursor.execute("CREATE TABLE users(username TEXT PRIMARY KEY NOT NULL, password TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')));")
    cursor.execute("CREATE TABLE friends(username TEXT NOT NULL, friend TEXT NOT NULL, CHECK (username != friend), PRIMARY KEY (username, friend), FOREIGN KEY(username) REFERENCES users(username), FOREIGN KEY(friend) REFERENCES users(username));")
    cursor.execute("CREATE TABLE channels(name TEXT PRIMARY KEY NOT NULL, admin TEXT NOT NULL, FOREIGN KEY(admin) REFERENCES users(username));")
    cursor.execute("CREATE TABLE channel_messages(id INTEGER PRIMARY KEY NOT NULL, channel TEXT NOT NULL, username TEXT NOT NULL, message TEXT NOT NULL, message_type TEXT NOT NULL DEFAULT 'text', timestamp TEXT, FOREIGN KEY(channel) REFERENCES channels(name), FOREIGN KEY(username) REFERENCES users(username));")
    cursor.execute("CREATE TABLE private_messages(id INTEGER PRIMARY KEY NOT NULL, private_room TEXT NOT NULL, username TEXT NOT NULL, message TEXT NOT NULL, message_type TEXT NOT NULL DEFAULT 'text', timestamp TEXT NOT NULL, FOREIGN KEY(username) REFERENCES users(username));")
    cursor.execute("CREATE TABLE channel_members(channel TEXT NOT NULL, username TEXT NOT NULL, PRIMARY KEY (channel, username), FOREIGN KEY(channel) REFERENCES channels(name));")
    
    
    conn.commit()   # sert a valider les changements dans la base de données
    
    debug("db reseted.")


if not os.path.isfile(DB_FILE):
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    reset_db()

else:
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)

conn.execute("PRAGMA foreign_keys = ON;")

# Assurer que la colonne created_at existe dans la table users
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(users)")
columns = [row[1] for row in cursor.fetchall()]
if "created_at" not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN created_at TEXT;")
    cursor.execute("UPDATE users SET created_at = datetime('now', 'localtime') WHERE created_at IS NULL;")
    conn.commit()

if __name__ == "__main__":
    DEBUG = 1
    
    if "--reset" in sys.argv[1:]:
        reset_db()