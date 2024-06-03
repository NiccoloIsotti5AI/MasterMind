import socket
import threading
import random

class MastermindServer:
    def __init__(self):
        self.colori = ["red", "blue", "green", "yellow", "orange", "purple", "teal", "magenta"]
        self.code = random.sample(self.colori, 4)
        self.connections = []
        self.attempts = [0, 0]
        self.finished = [False, False]
        self.lock = threading.Lock()
        self.game_over = False

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 5555))
        self.server_socket.listen(2)
        print("Server listening for Player 1...")

        self.player1_conn, _ = self.server_socket.accept()
        self.connections.append(self.player1_conn)
        print("Player 1 connected.")

        self.player1_thread = threading.Thread(target=self.controlla_client, args=(self.player1_conn, 0))
        self.player1_thread.start()

        print("Server listening for Player 2...")
        self.server_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket2.bind(('localhost', 5556))
        self.server_socket2.listen(2)

        self.player2_conn, _ = self.server_socket2.accept()
        self.connections.append(self.player2_conn)
        print("Player 2 connected.")

        self.player2_thread = threading.Thread(target=self.controlla_client, args=(self.player2_conn, 1))
        self.player2_thread.start()

    def controlla_client(self, client_socket, indice_player):
        while True:
            if self.game_over:
                break

            data = client_socket.recv(1024).decode('utf-8').split(",")
            if not data or data[0] == "QUIT":
                self.send_game_over_message("GAME OVER: Player {} has left the game.".format(indice_player + 1))
                break

            print(f"Received data from player {indice_player + 1}: {data}")
            result = self.controlla_risultato(data)
            client_socket.send(",".join(map(str, result)).encode())
            self.attempts[indice_player] += 1

            if result == [1, 1, 1, 1]:
                self.finished[indice_player] = True
                if self.controlla_entrambi():
                    self.dichiara_vincitore()
                else:
                    client_socket.send("WAIT".encode())
            elif self.attempts[indice_player] >= 12:
                self.finished[indice_player] = True
                client_socket.send("GAMEOVER".encode())
                if self.controlla_entrambi():
                    self.dichiara_vincitore()


    def controlla_risultato(self, guess):
        result = [0] * 4
        code_copy = self.code[:]
        for i in range(4):
            if guess[i] == code_copy[i]:
                result[i] = 1
                code_copy[i] = None
        for i in range(4):
            if guess[i] in code_copy:
                result[i] = 2
                code_copy[code_copy.index(guess[i])] = None
        return result

    def controlla_entrambi(self):
        return all(self.finished)


    def dichiara_vincitore(self):
        if self.attempts[0] < self.attempts[1]:
            index_vincitore = 0
        elif self.attempts[1] < self.attempts[0]:
            index_vincitore = 1
        else:
            index_vincitore = None  # Pareggio

        if index_vincitore is not None:
            for i, conn in enumerate(self.connections):
                if i == index_vincitore:
                    conn.send("WIN".encode())
                else:
                    conn.send("LOSS".encode())
            self.send_game_over_message("GAME OVER: Player {} has won!".format(index_vincitore + 1))
        else:
            for conn in self.connections:
                conn.send("TIE".encode())  # Invia il messaggio "TIE" a entrambi i client
            self.send_game_over_message("GAME OVER: It's a tie! Both players have used the same number of attempts.")

        self.ricomincia_partita()

    def ricomincia_partita(self):
        self.game_over = False
        self.code = random.sample(self.colori, 4)
        self.attempts = [0, 0]
        self.finished = [False, False]


server = MastermindServer()
server.start()