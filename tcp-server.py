import socket, sqlite3, threading, hashlib

chats = []

class Client:
    def __init__(self, csocket, address, sqli):
        self.username = "guest"
        self.csocket = csocket
        self.address = address
        self.sqli = sqli
        self.cursor = sqli.cursor()


    def register(self, username, password):
        self.cursor.execute(f"SELECT username FROM users WHERE username == '{username}'")
        if len(self.cursor.fetchall())>0:
            return "User already exist."
        else:
            self.cursor.execute(f"INSERT INTO users(username, password) VALUES (?, ?)", (username, hashlib.sha256(password.encode()).hexdigest()))
            self.sqli.commit()
            return "User added."

    def login(self, username, password):
        self.cursor.execute(f"SELECT username, password FROM users WHERE username=='{username}' AND password == '{hashlib.sha256(password.encode()).hexdigest()}'")
        
        if len(self.cursor.fetchall())==1:
            self.username = username
            return f"Welcome back, {self.username}."
        else:
            return "Wrong username or password."
    
    def logout(self):
        self.username = "guest"
        return "Logging out..."

    def listfriends(self):
        self.cursor.execute(f"SELECT friend FROM friends WHERE username=='{self.username}'")
        friends = [i[0] for i in self.cursor.fetchall()]
        return friends

    def addfriend(self, friend):
        self.cursor.execute(f"INSERT INTO friends(username, friend) VALUES (?, ?)", (self.username, friend))
        self.sqli.commit()
        return "Friend added."
    
    



def conection_handler(csocket, address):
    client = Client(csocket, address, sqlite3.connect("Toki.db"))

    print("Conection from "+address[0]+":"+str(address[1]))

    clientsocket.send(bytes("!h for help\n\r", encoding='utf-8'))
    while 1:
        data = csocket.recv(4096)
        if data!=b"":
            #print(data)
            try:
                string = data.decode()
            except UnicodeDecodeError:
                continue

            cmd = string.splitlines()[0].split(" ")[0]
            args = string.splitlines()[0].split(" ")[1:]

            print(f"{client.username} ({client.address[0]}:{client.address[1]}) -> {cmd} {args}")        

            response = []
            if client.username != "guest":
                if cmd == "!h":
                    response = ["!whoami", "!logout", "!listfriends", "!listchannels", "!addfriend (friend)", "!createchannel", "!joinchannel", "!joinfriend", "!deletefriend"]
                if cmd == "!logout":
                    response = [client.logout()]
                if cmd == "!listfriends":
                    response = client.listfriends()
                if cmd == "!addfriend":
                    response = [client.addfriend(args[0])]
                if cmd == "!joinfriend":
                    response = [client.addfriend(args[0])]
                
            else:
                if cmd == "!h":
                    response = ["!whoami", "!login (username) (password)", "!register (username) (password)"]
                elif cmd == "!login":
                    if len(args)==2: response = [client.login(args[0], args[1])]
                    else: response = ["There should be 2 arguments."]
                elif cmd == "!register":
                    if len(args)==2: response = [client.register(args[0], args[1])]
                    else: response = ["There should be 2 arguments."]
                else:
                    response = ["Command not found."]

            if cmd == "!whoami":
                response = [client.username]
            csocket.send(("\n\r".join(response)+"\n\r").encode())
        else:
            print(f"Client disconnected.")
            break
            


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind(("0.0.0.0", 81))
serversocket.listen(0)

while 1:
    (clientsocket, address) = serversocket.accept()
    
    t1 = threading.Thread(target=conection_handler, args=(clientsocket, address,))
    t1.start()

