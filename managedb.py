import sqlite3, os

db = "Toki.db"

if os.path.exists(db):
    os.remove(db)

conn = sqlite3.connect(db)
cursor = conn.cursor()

def resetdb():
    #cursor.execute("DROP TABLE users;")
    cursor.execute("CREATE TABLE users(username TEXT UNIQUE NOT NULL, password TEXT NOT NULL);")
    #cursor.execute("DROP TABLE friends;")
    cursor.execute("CREATE TABLE friends(username TEXT NOT NULL, friend TEXT NOT NULL, PRIMARY KEY (username, friend), FOREIGN KEY(username) REFERENCES users(username), FOREIGN KEY(friend) REFERENCES users(username));")
    #cursor.execute("DROP TABLE channels;")
    cursor.execute("CREATE TABLE channels(name TEXT UNIQUE NOT NULL);")
    #cursor.execute("DROP TABLE channel_members;")
    cursor.execute("CREATE TABLE channel_members(channel TEXT NOT NULL, username TEXT NOT NULL, role TEXT NOT NULL, PRIMARY KEY (channel, username), FOREIGN KEY(channel) REFERENCES channels(name));")
    
    conn.commit()
    #"PRAGMA foreign_keys = ON"
resetdb()