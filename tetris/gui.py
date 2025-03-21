# tetris/gui.py
import tkinter as tk
import random
import time
from tetris.game import TetrisGame
from tetris.ai import ai_move
from tetris.game import COLOR_PALETTE

class TetrisGUI:
    def __init__(self, master):
        self.master = master
        self.game = TetrisGame()
        # Canvas principal pour le jeu
        self.canvas_humain = tk.Canvas(master, width=200, height=400, bg="black")
        self.canvas_ia = tk.Canvas(master, width=200, height=400, bg="black")
        self.canvas_humain.grid(row=0, column=0, padx=10, pady=10)
        self.canvas_ia.grid(row=0, column=1, padx=10, pady=10)
        # Labels de score
        self.score_label_humain = tk.Label(master, text="Score Humain: 0")
        self.score_label_ia = tk.Label(master, text="Score IA: 0")
        self.score_label_humain.grid(row=1, column=0)
        self.score_label_ia.grid(row=1, column=1)
        # Prévisualisation de la prochaine pièce
        self.preview_canvas_humain = tk.Canvas(master, width=100, height=100, bg="white")
        self.preview_canvas_ia = tk.Canvas(master, width=100, height=100, bg="white")
        tk.Label(master, text="Prochaine pièce (Humain)").grid(row=2, column=0)
        self.preview_canvas_humain.grid(row=3, column=0, pady=5)
        tk.Label(master, text="Prochaine pièce (IA)").grid(row=2, column=1)
        self.preview_canvas_ia.grid(row=3, column=1, pady=5)
        master.bind("<Key>", self.on_key_press)
        self.update()

    def on_key_press(self, event):
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
        self.game.update()
        # On fait bouger l'IA uniquement si son jeu n'est pas terminé
        if not self.game.game_over_ia:
            from tetris.ai import ai_move
            ai_move(self.game)
        self.draw()

        import time
        # Application de la règle "Pause douceur" : si active, augmenter le délai
        if self.game.pause_active and time.time() < self.game.pause_end_time:
            delay = 120  # Par exemple, 120 ms
        else:
            self.game.pause_active = False
            delay = 100
        self.master.after(delay, self.update)

    def draw(self):
        self.canvas_humain.delete("all")
        self.canvas_ia.delete("all")
        self.draw_grid(self.canvas_humain, self.game.grid_humain)
        self.draw_grid(self.canvas_ia, self.game.grid_ia)
        
        # Afficher la pièce en cours si le jeu n'est pas terminé pour ce joueur
        if not self.game.game_over_humain:
            self.draw_piece(self.canvas_humain, self.game.current_piece_humain)
        if not self.game.game_over_ia:
            self.draw_piece(self.canvas_ia, self.game.current_piece_ia)
        
        self.score_label_humain.config(text=f"Score Humain: {self.game.score_humain}")
        self.score_label_ia.config(text=f"Score IA: {self.game.score_ia}")
        self.update_preview()
        
        # Afficher "Game Over" sur le canvas concerné si le jeu est terminé
        if self.game.game_over_humain:
            self.display_game_over(self.canvas_humain)
        if self.game.game_over_ia:
            self.display_game_over(self.canvas_ia)

    def draw_grid(self, canvas, grid):
        cell_size = 20
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0
        # Dessiner la grille de fond
        for i in range(rows + 1):
            canvas.create_line(0, i * cell_size, cols * cell_size, i * cell_size, fill="gray")
        for j in range(cols + 1):
            canvas.create_line(j * cell_size, 0, j * cell_size, rows * cell_size, fill="gray")
        # Dessiner les blocs
        for i, row in enumerate(grid):
            for j, cell in enumerate(row):
                if cell:
                    x0 = j * cell_size
                    y0 = i * cell_size
                    x1 = x0 + cell_size
                    y1 = y0 + cell_size
                    if self.game.rainbow_active:
                        color = random.choice(COLOR_PALETTE)
                    else:
                        color = cell
                    canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

    def draw_piece(self, canvas, piece):
        cell_size = 20
        if self.game.rainbow_active:
            color = random.choice(COLOR_PALETTE)
        else:
            color = piece.get("color", "yellow")
        shape = piece["shape"]
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    x0 = (piece["x"] + j) * cell_size
                    y0 = (piece["y"] + i) * cell_size
                    x1 = x0 + cell_size
                    y1 = y0 + cell_size
                    canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="gray")

    def update_preview(self):
        self.preview_canvas_humain.delete("all")
        self.preview_canvas_ia.delete("all")
        self.draw_piece_preview(self.preview_canvas_humain, self.game.next_piece_humain)
        self.draw_piece_preview(self.preview_canvas_ia, self.game.next_piece_ia)

    def draw_piece_preview(self, canvas, piece):
        cell_size = 20
        color = piece.get("color", "yellow")
        shape = piece["shape"]
        rows = len(shape)
        cols = len(shape[0])
        canvas_width = int(canvas['width'])
        canvas_height = int(canvas['height'])
        total_piece_width = cols * cell_size
        total_piece_height = rows * cell_size
        offset_x = (canvas_width - total_piece_width) // 2
        offset_y = (canvas_height - total_piece_height) // 2
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    x0 = offset_x + j * cell_size
                    y0 = offset_y + i * cell_size
                    x1 = x0 + cell_size
                    y1 = y0 + cell_size
                    canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="gray")

    def display_floating_points(self, canvas, message):
        points = message["points"]
        if points == 0:
            return
        y = message["y"] if message["y"] is not None else int(canvas['height']) // 2
        margin = 0
        offset = 0
        total_duration = 8000  # 8 secondes d'affichage total
        animation_duration = 600  # 600 ms d'animation de slide
        steps = 20
        delay = animation_duration // steps
        if message["grid"] == "ia":
            x_final = int(canvas['width']) - margin
            anchor = "e"
            x_initial = x_final + offset
            dx = -offset / steps
        elif message["grid"] == "humain":
            x_final = margin
            anchor = "w"
            x_initial = x_final - offset
            dx = offset / steps
        text_item = canvas.create_text(x_initial, y, text=f"+{points}", fill="yellow",
                                        font=("Helvetica", 20, "bold"), anchor=anchor)
        def slide_step(step):
            if step < steps:
                canvas.move(text_item, dx, 0)
                canvas.after(delay, lambda: slide_step(step + 1))
            else:
                remaining_time = total_duration - animation_duration
                canvas.after(remaining_time, lambda: canvas.delete(text_item))
        slide_step(0)

    def display_game_over(self, canvas):
        w = canvas.winfo_width() // 2
        h = canvas.winfo_height() // 2
        canvas.create_text(w, h, text="Game Over", fill="red", font=("Helvetica", 30, "bold"))