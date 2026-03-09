import socket, sqlite3, threading, hashlib

class Terminal:
    def __init__(self, address):
        self.user = "guest"
        self.address = address

    def register(self, user, password):
        conn = sqlite3.connect("Toki.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM User WHERE userid == '{hashlib.sha256(user.encode()).hexdigest()}'")
        if len(cursor.fetchall()):
            return "User already exist.\n\r"
        else:
            cursor.execute(f"INSERT INTO User(userid, user, password) VALUES (?, ?, ?)", (hashlib.sha256(user.encode()).hexdigest(), user, hashlib.sha256(password.encode()).hexdigest()))
            conn.commit()
            return "User added.\n\r"

    def login(self, user, password):
        conn = sqlite3.connect("user.db")
        cursor = conn.cursor()
        self.user = user


def conection_handler(cs, address):
    print("Conection from "+address[0]+":"+str(address[1]))
    t = Terminal(address)
    cs.send(bytes("!h for help\n\r\n\r", encoding='utf-8'))
    while 1:
        d = cs.recv(4096)
        try:
            s = d.decode()
        except UnicodeDecodeError:
            continue

        print(f"{t.user} {t.address} -> {repr(s)[1:-1]}")
        help = "!login user, password\n\r!register user, password\n\r"

        if not d:
            print(f"Client disconnected")
            break
        elif s=="!h":
            cs.send(help.encode())

        elif s.split(" ")[0]=="!register":
            cs.send(t.register(s.split(" ")[1], s.split(" ")[2]).encode())
            


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(("0.0.0.0", 81))
serversocket.listen(0)

while 1:
    (clientsocket, address) = serversocket.accept()
    
    t1 = threading.Thread(target=conection_handler, args=(clientsocket, address,))
    t1.start()

