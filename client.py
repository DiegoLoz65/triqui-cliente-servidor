import socket

host = '127.0.0.1'
port = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

while True:
    data = client.recv(1024).decode()
    print(data)

    if data.startswith("#OK#Tu eres el jugador"):
        choice = input("Elige X o O: ")
        client.send(f"#JUGADA#{choice}#".encode())
    elif data.startswith("#OK#Es tu turno"):
        move = input("Elige una posición (0-8): ")
        client.send(f"#JUGADA#{move}#".encode())
