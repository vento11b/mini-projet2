import socket, sqlite3, threading, hashlib


class Client:
    def __init__(self, address, sqli):
        self.username = "guest"
        self.address = address
        #self.sqli = sqli
        self.sqlic = sqli.cursor()


    def register(self, username, password):
        self.sqlic.execute(f"SELECT username FROM Users WHERE username == '{username}'")
        if len(cursor.fetchall())>0:
            return "User already exist.\n\r"
        else:
            self.sqlic.execute(f"INSERT INTO Users(username, password) VALUES (?, ?)", (username, hashlib.sha256(password.encode()).hexdigest()))
            self.sqli.commit()
            return "User added.\n\r"

    def login(self, username, password):
        self.sqlic.execute(f"SELECT username, password FROM Users WHERE username=='{username}' AND password == '{hashlib.sha256(password.encode()).hexdigest()}'")
        
        if len(self.sqlic.fetchall())==1:
            self.username = username
            return f"Welcome back, {self.username}"
        else:
            return "Wrong username or password"


def conection_handler(csocket, address):
    client = Client(address, sqlite3.connect("Toki.db"))

    print("Conection from "+address[0]+":"+str(address[1]))

    clientsocket.send(bytes("!h for help\n\r", encoding='utf-8'))
    while 1:
        data = csocket.recv(4096)
        try:
            string = data.decode()
        except UnicodeDecodeError:
            continue

        cmd = string.split("\n")[0].split(" ")[0]
        args = string.split("\n")[0].split(" ")[1:]

        print(f"{client.username} {client.address} -> {cmd} {args}")        

        if data!="":
            response = []
            if client.username != "guest":
                if cmd == "!h":
                    response = ["!whoami", "!logout"]
                if cmd == "!h":
                    response = ["!whoami", "!logout"]
            else:
                if cmd == "!h":
                    response = ["!whoami", "!login (username) (password)", "!register (username) (password)"]
                elif cmd == "!login":
                    if len(args)==2: response = [client.login(args[0], args[1])]
                    else: response = ["There should be 2 arguments"]
                elif cmd == "!register":
                    if len(args)==2: response = [client.register(args[0], args[1])]
                    else: response = ["There should be 2 arguments"]
            if cmd == "!whoami":
                response = [client.username]
            csocket.send(("\n\r".join(response)+"\n\r").encode())
        else:
            print(f"Client disconnected")
            break
            


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind(("0.0.0.0", 81))
serversocket.listen(0)

while 1:
    (clientsocket, address) = serversocket.accept()
    
    t1 = threading.Thread(target=conection_handler, args=(clientsocket, address,))
    t1.start()

