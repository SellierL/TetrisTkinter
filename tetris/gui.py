# tetris/gui.py
import tkinter as tk
from tetris.game import TetrisGame

class TetrisGUI:
    def __init__(self, master):
        self.master = master
        # Initialisation de la logique du jeu
        self.game = TetrisGame()
        
        # Création des canvas pour chaque joueur
        self.canvas_humain = tk.Canvas(master, width=200, height=400, bg="black")
        self.canvas_ia = tk.Canvas(master, width=200, height=400, bg="black")
        self.canvas_humain.grid(row=0, column=0, padx=10, pady=10)
        self.canvas_ia.grid(row=0, column=1, padx=10, pady=10)
        
        # Création des labels pour les scores
        self.score_label_humain = tk.Label(master, text="Score Humain: 0")
        self.score_label_ia = tk.Label(master, text="Score IA: 0")
        self.score_label_humain.grid(row=1, column=0)
        self.score_label_ia.grid(row=1, column=1)
        
        # Lier les événements clavier
        master.bind("<Key>", self.on_key_press)
        
        # Démarrer la boucle d'actualisation
        self.update()

    def on_key_press(self, event):
        # Gestion des touches fléchées pour déplacer/faire tourner la pièce du joueur humain
        if event.keysym == "Left":
            self.game.move_piece(self.game.current_piece_humain, self.game.grid_humain, dx=-1)
        elif event.keysym == "Right":
            self.game.move_piece(self.game.current_piece_humain, self.game.grid_humain, dx=1)
        elif event.keysym == "Down":
            self.game.move_piece(self.game.current_piece_humain, self.game.grid_humain, dy=1)
        elif event.keysym == "Up":
            self.game.rotate_piece(self.game.current_piece_humain, self.game.grid_humain)
        self.draw()

    def update(self):
        # Mise à jour de la logique du jeu pour le joueur humain
        self.game.update()
        # Appel de l'IA pour faire son mouvement
        from tetris.ai import ai_move
        ai_move(self.game)
        # Actualisation de l'affichage
        self.draw()
        # Replanifier l'update après 100 ms
        self.master.after(100, self.update)

    def draw(self):
        # Effacer les canvas et redessiner grilles et pièces
        self.canvas_humain.delete("all")
        self.canvas_ia.delete("all")
        self.draw_grid(self.canvas_humain, self.game.grid_humain)
        self.draw_grid(self.canvas_ia, self.game.grid_ia)
        self.draw_piece(self.canvas_humain, self.game.current_piece_humain)
        self.draw_piece(self.canvas_ia, self.game.current_piece_ia)
        self.score_label_humain.config(text=f"Score Humain: {self.game.score_humain}")
        self.score_label_ia.config(text=f"Score IA: {self.game.score_ia}")

    def draw_grid(self, canvas, grid):
        cell_size = 20
        for i, row in enumerate(grid):
            for j, cell in enumerate(row):
                if cell:
                    x0 = j * cell_size
                    y0 = i * cell_size
                    x1 = x0 + cell_size
                    y1 = y0 + cell_size
                    canvas.create_rectangle(x0, y0, x1, y1, fill="cyan", outline="grey")

    def draw_piece(self, canvas, piece):
        cell_size = 20
        shape = piece["shape"]
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    x0 = (piece["x"] + j) * cell_size
                    y0 = (piece["y"] + i) * cell_size
                    x1 = x0 + cell_size
                    y1 = y0 + cell_size
                    canvas.create_rectangle(x0, y0, x1, y1, fill="yellow", outline="grey")
