import sqlite3, hashlib

db_file = "src/backend/app/Toki.db"

def check_credentials(username, password):
    

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users WHERE username = ? AND password = ?", (username, hashlib.sha256(password.encode()).hexdigest()))    
    return len(cursor.fetchall())==1

def check_username(username):
    

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    return len(cursor.fetchall())==0


def create_user(username, password):
    

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    if check_username(username) and check_password(password):
        cursor.execute("INSERT INTO users(username, password) VALUES (?, ?)", (username, hashlib.sha256(password.encode()).hexdigest()))
        conn.commit()
        return 1
    else:
        return 0

def check_password(password):
    

    taille = len(password) >= 8
    majuscule = any([c.isupper() for c in password])
    minuscule = any([c.islower() for c in password])
    chiffre = any([c.isdigit() for c in password])
    special = any([c in "!@#$%^&*" for c in password])
    return taille and majuscule and minuscule and chiffre and special


def list_users():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    return [user[0].encode('utf-8') for user in cursor.fetchall()]
