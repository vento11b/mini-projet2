import sqlite3, hashlib

db_file = "Toki.db"

def check_credentials(username, password):
    sqli = sqlite3.connect(db_file)
    cursor = sqli.cursor()
    cursor.execute("SELECT username, password FROM users WHERE username = ? AND password = ?", (username, hashlib.sha256(password.encode()).hexdigest()))    
    return len(cursor.fetchall())==1

def check_username(username):
    sqli = sqlite3.connect(db_file)
    cursor = sqli.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ?", (username))
    return len(cursor.fetchall())==0


def create_user(username, password):
    sqli = sqlite3.connect(db_file)
    cursor = sqli.cursor()
    if check_username(username) and check_password(password):
        cursor.execute("INSERT INTO users(username, password) VALUES (?, ?)", (username, hashlib.sha256(password.encode()).hexdigest()))
        sqli.commit()
        return 1
    else:
        return 0

def check_password(username, password):
    taille = len(password) >= 8
    majuscule = any([c.isupper() for c in password])
    minuscule = any([c.islower() for c in password])
    chiffre = any([c.isdecimal() for c in password])
    special = any([c in "@%^_=\{\}[]()+;,.?#-" for c in password])
    return taille and majuscule and minuscule and chiffre and special

def reset_db():
    sqli = sqlite3.connect(db_file)
    cursor = sqli.cursor()

    cursor.execute("DROP TABLE users;")
    cursor.execute("CREATE TABLE users(username TEXT PRIMARY KEY, password TEXT);")

    cursor.execute("DROP TABLE friends;")
    cursor.execute("CREATE TABLE friends(username TEXT, friend TEXT, PRIMARY KEY (username, friend), FOREIGN KEY(username) REFERENCES users(username), FOREIGN KEY(friend) REFERENCES users(username));")
    
    cursor.execute("DROP TABLE channels;")
    cursor.execute("CREATE TABLE channels(name TEXT PRIMARY KEY );")
    
    cursor.execute("DROP TABLE channel_members;")
    cursor.execute("CREATE TABLE channel_members(channel TEXT , username TEXT , role TEXT , PRIMARY KEY (channel, username), FOREIGN KEY(channel) REFERENCES channels(name));")
    
    conn.commit()