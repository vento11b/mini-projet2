import socket, sqlite3


serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(("0.0.0.0", 81))
serversocket.listen(5)
while 1:
    (clientsocket, address) = serversocket.accept()
    sqliteConnection = sqlite3.connect('salons.db')
    cursor = sqliteConnection.cursor()

    while 1:
        d = str(clientsocket.recv(4096))[2:-1]
        print(d.split(" "))
