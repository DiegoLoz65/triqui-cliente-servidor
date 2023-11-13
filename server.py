import socket
import threading

# Inicialización del servidor
host = '127.0.0.1'
port = 12345
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Variables para el juego
player_turn = 0
board = [' '] * 9
players = [None, None]
signs = ['X', 'O']
game_count = 0
player_scores = [0, 0]

# Función para manejar la lógica del juego
def play_game(player1, player2):
    global player_turn
    global board
    global signs
    global game_count

    player1.send("#OK#Tu eres el jugador 1. Elige X o O: ".encode())
    choice = player1.recv(1024).decode().strip()
    if choice.split('#')[2] == 'X':
        player2.send("#OK#Tu signo es O.".encode())
        player_turn = 0
    else:
        player2.send("#OK#Tu signo es X.".encode())
        player_turn = 1

    while game_count < 5:
        if player_turn == 0:
            current_player = player1
            other_player = player2
        else:
            current_player = player2
            other_player = player1

        current_player.send(f"#OK#Es tu turno. Tablero actual: {board}".encode())
        move = current_player.recv(1024).decode().strip()
        print(move)
        print(move.startswith("#JUGADA#"))
        print(move.split('#')[2])

        if move.startswith("#JUGADA#"):
            position = int(move.split('#')[2])
            if position < 0 or position > 8 or board[position] != ' ':
                current_player.send("#NOK#Movimiento no válido. Inténtalo de nuevo.".encode())
                continue

            board[position] = signs[player_turn]
            current_player.send("#OK#Movimiento exitoso.".encode())
            other_player.send(f"#OK#Tu oponente hizo una jugada. Tablero actual: {board}".encode())

            if check_win():
                player_scores[player_turn] += 1
                game_count += 1
                reset_board()
                current_player.send("#OK#¡Ganaste esta partida!".encode())
                other_player.send("#OK#Perdiste esta partida.".encode())
            else:
                player_turn = 1 - player_turn
        else:
            current_player.send("#NOK#Instrucción no válida. Inténtalo de nuevo.".encode())

    player1.send(f"#OK#Jugador 1: {player_scores[0]} - Jugador 2: {player_scores[1]}".encode())
    player2.send(f"#OK#Jugador 1: {player_scores[0]} - Jugador 2: {player_scores[1]}".encode())
    game_count = 0
    reset_board()

def check_win():
    # Verificar si alguien ha ganado
    winning_combinations = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != ' ':
            return True
    return False

def reset_board():
    # Reiniciar el tablero
    global board
    board = [' '] * 9

def handle_client(client_socket):
    global players
    if players[0] is None:
        players[0] = client_socket
        client_socket.send("#OK#Esperando al segundo jugador...".encode())
    elif players[1] is None:
        players[1] = client_socket
        client_socket.send("#OK#Esperando al primer jugador...".encode())
        play_game(players[0], players[1])
        players = [None, None]

# Ciclo principal del servidor
while True:
    client_socket, addr = server.accept()
    client_handler = threading.Thread(target=handle_client, args=(client_socket,))
    client_handler.start()
