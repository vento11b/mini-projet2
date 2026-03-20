import sqlite3, hashlib

db_file = "Toki.db"

def validate_user(username, password):
    sqli = sqlite3.connect(db_file)
    cursor = sqli.cursor()
    cursor.execute(f"SELECT username, password FROM users WHERE username = ? AND password = ?", (username, hashlib.sha256(password.encode()).hexdigest()))    
    return len(cursor.fetchall())==1

def create_user(username, password):
    sqli = sqlite3.connect(db_file)
    cursor = sqli.cursor()
    cursor.execute(f"SELECT username FROM users WHERE username == '{username}'")
    if len(cursor.fetchall())>0:
        return 0
    else:
        cursor.execute(f"INSERT INTO users(username, password) VALUES (?, ?)", (username, hashlib.sha256(password.encode()).hexdigest()))
        sqli.commit()
        return 1
