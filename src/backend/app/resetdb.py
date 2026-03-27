import sqlite3

def reset_db(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS users;")
    cursor.execute("CREATE TABLE users(username TEXT PRIMARY KEY, password TEXT);")

    cursor.execute("DROP TABLE IF EXISTS friends;")
    cursor.execute("CREATE TABLE friends(username TEXT, friend TEXT, PRIMARY KEY (username, friend), FOREIGN KEY(username) REFERENCES users(username), FOREIGN KEY(friend) REFERENCES users(username));")
    
    cursor.execute("DROP TABLE IF EXISTS channels;")
    cursor.execute("CREATE TABLE channels(name TEXT PRIMARY KEY );")
    
    cursor.execute("DROP TABLE IF EXISTS channel_members;")
    cursor.execute("CREATE TABLE channel_members(channel TEXT , username TEXT , role TEXT , PRIMARY KEY (channel, username), FOREIGN KEY(channel) REFERENCES channels(name));")
    
    conn.commit()
    conn.close()
    print("db reseted.")

if __name__ == '__main__':
    reset_db("src/backend/app/Toki.db")