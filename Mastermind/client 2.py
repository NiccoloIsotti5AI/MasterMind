import tkinter as tk
from tkinter import messagebox
import socket
import threading

class MastermindClient2:
    def __init__(self, master):
        self.master = master
        self.master.title("Mastermind Client 2")
        self.master.geometry("500x600")
        self.colori = ["red", "blue", "green", "yellow", "orange", "purple", "teal", "magenta"]
        self.guesses = []
        self.results = []
        self.num_checks = 0
        self.aspetta = False  # Flag per gestire il blocco del gioco
        self.new_game = True  # Flag per gestire l'inizio di una nuova partita
        self.create_widgets()
        self.connect_to_server()

    def connect_to_server(self):
        self.server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_connection.connect(('localhost', 5556))
        threading.Thread(target=self.ricevi_risposta, daemon=True).start()

    def create_widgets(self):
        title_label = tk.Label(self.master, text="Mastermind Client 2", font=("Helvetica", 24, "bold"), pady=10)
        title_label.pack()

        color_frame = tk.Frame(self.master)
        color_frame.pack(pady=10)
        for color in self.colori:
            button = tk.Button(color_frame, bg=color, width=4, height=2, command=lambda c=color: self.fai_guess(c))
            button.pack(side=tk.LEFT, padx=5)

        self.guesses_frame = tk.Frame(self.master)
        self.guesses_frame.pack(pady=10)
        self.guesses_labels = [[tk.Label(self.guesses_frame, width=4, height=2, bg="grey", borderwidth=2, relief="solid") for _ in range(4)] for _ in range(12)]
        for i, row in enumerate(self.guesses_labels):
            for j, label in enumerate(row):
                label.grid(row=i, column=j, padx=2, pady=2)

        self.results_labels = [[tk.Label(self.guesses_frame, width=2, height=1, bg="grey", borderwidth=2, relief="solid") for _ in range(4)] for _ in range(12)]
        for i, row in enumerate(self.results_labels):
            for j, label in enumerate(row):
                label.grid(row=i, column=4+j, padx=1, pady=1)

        check_button = tk.Button(self.master, text="Controlla", font=("Helvetica", 12, "bold"), command=self.invia_guess)
        check_button.pack(pady=10)



        delete_button = tk.Button(self.master, text="Elimina ultima scelta", font=("Helvetica", 12, "bold"), command=self.cancella_ultima_selezione)
        delete_button.pack(pady=10)

    def fai_guess(self, color):
        if len(self.guesses) >= 4:
            messagebox.showinfo("Errore", "Per favore controlla le scelte prima di fare un'altra")
            return
        if self.aspetta:  # Blocca l'invio dei tentativi se il gioco è bloccato
            messagebox.showinfo("Attesa", "Attendere il risultato.")
            return
        self.guesses.append(color)
        self.aggiorna_guesses_labels()

    def cancella_ultima_selezione(self):
        if self.guesses:
            self.guesses.pop()
            self.aggiorna_guesses_labels()

    def invia_guess(self):
        if len(self.guesses) != 4:
            messagebox.showinfo("Errore", "Devi inserire le 4 scelte per poter fare il check")
            return
        guess_str = ','.join(self.guesses)
        self.server_connection.send(str.encode(guess_str))

    def ricevi_risposta(self):
        while True:
            data = self.server_connection.recv(1024).decode('utf-8').split(',')
            if not data:
                break
            if data[0] == "WIN":
                self.fine_gioco("Hai vinto! Il gioco è finito.")
            elif data[0] == "LOSS":
                self.fine_gioco("Hai perso! Il gioco è finito.")
            elif data[0] == "GAMEOVER":
                self.fine_gioco("Il gioco è finito. Nessun vincitore.")
            elif data[0] == "WAIT":
                self.aspetta = True
                self.guesses = []
                self.aggiorna_guesses_labels()
                messagebox.showinfo("Attesa", "Attendere il risultato.")
            elif data[0] == "QUIT":
                self.fine_gioco()
            elif data[0] == "TIE":  # Aggiungi la gestione del messaggio "TIE"
                self.fine_gioco("La partita è terminata in pareggio.")
            else:
                self.elabora_risultato(data)

    def elabora_risultato(self, result):
        self.results.append(result)
        self.aggiorna_results_labels()
        self.guesses = []
        self.num_checks += 1
        self.aspetta = False  # Permette di inviare nuovamente i tentativi

    def fine_gioco(self, message):
        messagebox.showinfo("Fine del Gioco", message)
        self.new_game = False
        self.aspetta = True
        self.guesses = []
        self.aggiorna_guesses_labels()

    def aggiorna_guesses_labels(self):
        current_row = self.guesses_labels[self.num_checks]
        for label in current_row:
            label.config(bg="grey")
        for i, color in enumerate(self.guesses):
            current_row[i].config(bg=color)

    def aggiorna_results_labels(self):
        result = self.results[-1]
        for i in range(4):
            color = "red" if result[i] == '1' else "white" if result[i] == '2' else "grey"
            self.results_labels[self.num_checks][i].config(bg=color)

def main():
    root = tk.Tk()
    app = MastermindClient2(root)
    root.mainloop()

main()