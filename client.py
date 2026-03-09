import socket

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.connect((input("Server IP: "), 81))
while True:
    d = serversocket.send(bytes(input("-> "), encoding="utf-8"))
