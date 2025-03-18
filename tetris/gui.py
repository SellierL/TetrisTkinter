# tetris/gui.py
import tkinter as tk
from tetris.game import TetrisGame

class TetrisGUI:
    def __init__(self, master):
        self.master = master
        self.game = TetrisGame()
        
        # Canvas principal pour le jeu
        self.canvas_humain = tk.Canvas(master, width=200, height=400, bg="black")
        self.canvas_ia = tk.Canvas(master, width=200, height=400, bg="black")
        self.canvas_humain.grid(row=0, column=0, padx=10, pady=10)
        self.canvas_ia.grid(row=0, column=1, padx=10, pady=10)
        
        # Zone d'affichage du score
        self.score_label_humain = tk.Label(master, text="Score Humain: 0")
        self.score_label_ia = tk.Label(master, text="Score IA: 0")
        self.score_label_humain.grid(row=1, column=0)
        self.score_label_ia.grid(row=1, column=1)
        
        # Zone de prévisualisation de la prochaine pièce
        self.preview_canvas_humain = tk.Canvas(master, width=100, height=100, bg="white")
        self.preview_canvas_ia = tk.Canvas(master, width=100, height=100, bg="white")
        tk.Label(master, text="Prochaine pièce (Humain)").grid(row=2, column=0)
        self.preview_canvas_humain.grid(row=3, column=0, pady=5)
        tk.Label(master, text="Prochaine pièce (IA)").grid(row=2, column=1)
        self.preview_canvas_ia.grid(row=3, column=1, pady=5)
        
        master.bind("<Key>", self.on_key_press)
        self.update()

    def display_floating_points(self, canvas, message):
        points = message["points"]
        if points == 0:
            return
        # Position verticale : utiliser celle fournie ou centrer verticalement
        y = message["y"] if message["y"] is not None else int(canvas['height']) // 2
        margin = 10
        offset = 20  # Décalage initial hors de l'écran
        total_duration = 6000  # Durée totale d'affichage en ms
        animation_duration = 600  # Durée de l'animation de slide en ms
        steps = 20
        delay = animation_duration // steps

        if message["grid"] == "ia":
            # Pour l'IA, le texte vient de la droite
            x_final = int(canvas['width']) - margin
            anchor = "e"
            x_initial = x_final + offset
            dx = - offset / steps
        elif message["grid"] == "humain":
            # Pour le joueur humain, le texte vient de la gauche
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
        # On efface le canvas avant de redessiner
        self.canvas_humain.delete("all")
        self.canvas_ia.delete("all")
        
        # Dessiner la grille de fond (avec les lignes) et les blocs déjà placés
        self.draw_grid(self.canvas_humain, self.game.grid_humain)
        self.draw_grid(self.canvas_ia, self.game.grid_ia)
        
        # Dessiner la pièce en mouvement sur le canvas
        self.draw_piece(self.canvas_humain, self.game.current_piece_humain)
        self.draw_piece(self.canvas_ia, self.game.current_piece_ia)
        
        # Mise à jour des labels de score
        self.score_label_humain.config(text=f"Score Humain: {self.game.score_humain}")
        self.score_label_ia.config(text=f"Score IA: {self.game.score_ia}")
        
        # Affichage dynamique des gains (voir nos modifications précédentes)
        if self.game.last_points_message:
            message = self.game.last_points_message
            if message["points"] > 0:
                if message["grid"] == "humain":
                    self.display_floating_points(self.canvas_humain, message)
                elif message["grid"] == "ia":
                    self.display_floating_points(self.canvas_ia, message)
            self.game.last_points_message = None

        # Mettre à jour l'affichage de la prochaine pièce    
        self.update_preview()

    def draw_grid(self, canvas, grid):
        cell_size = 20
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0
        # Dessiner les lignes de la grille
        for i in range(rows + 1):
            canvas.create_line(0, i * cell_size, cols * cell_size, i * cell_size, fill="gray")
        for j in range(cols + 1):
            canvas.create_line(j * cell_size, 0, j * cell_size, rows * cell_size, fill="gray")
        
        # Dessiner les cases remplies
        for i, row in enumerate(grid):
            for j, cell in enumerate(row):
                if cell:  # Si cell n'est pas 0
                    x0 = j * cell_size
                    y0 = i * cell_size
                    x1 = x0 + cell_size
                    y1 = y0 + cell_size
                    # Vérifier que cell est une chaîne, sinon utiliser une couleur par défaut
                    if isinstance(cell, str):
                        color = cell
                    else:
                        color = "gray"
                    canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

    def draw_piece(self, canvas, piece):
        cell_size = 20
        color = piece.get("color", "yellow")  # Utilise la couleur définie dans la pièce
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
        # Effacer les zones de prévisualisation
        self.preview_canvas_humain.delete("all")
        self.preview_canvas_ia.delete("all")
        # Dessiner la pièce suivante pour le joueur humain et l'IA
        self.draw_piece_preview(self.preview_canvas_humain, self.game.next_piece_humain)
        self.draw_piece_preview(self.preview_canvas_ia, self.game.next_piece_ia)

    def draw_piece_preview(self, canvas, piece):
        # On dessine la pièce avec une échelle adaptée (par exemple, cellule de 20 pixels)
        cell_size = 20
        color = piece.get("color", "yellow")
        shape = piece["shape"]
        # Centrer la pièce dans le canvas de prévisualisation
        rows = len(shape)
        cols = len(shape[0])
        # Calculer un décalage pour centrer la pièce
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
