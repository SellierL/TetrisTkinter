# tetris/game.py
import random

COLOR_PALETTE = ["#aed6f1","#d2b4de", "#f5b7b1", "#f9e79f", "#abebc6", "#c0392b", "#dc7633"]

# Définition des formes de Tetriminos (exemple simplifié)
TETRIMINOS = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1],
          [1, 1]],
    "T": [[0, 1, 0],
          [1, 1, 1]],
    # Ajoutez d'autres formes si besoin...
}

class TetrisGame:
    def __init__(self, rows=20, cols=10):
        self.rows = rows
        self.cols = cols
        self.grid_humain = self.create_empty_grid()
        self.grid_ia = self.create_empty_grid()
        self.score_humain = 0
        self.score_ia = 0
        
        # Initialisation des flags pour la règle "cadeau surprise"
        self.next_piece_easy_humain = False
        self.next_piece_easy_ia = False

        # Initialiser l'attribut pour stocker le message de points (preview)
        self.last_points_message = None
        
        # Génération de la première pièce en cours et de la pièce suivante
        self.current_piece_humain = self.new_piece(for_player="humain")
        self.next_piece_humain = self.new_piece(for_player="humain")
        self.current_piece_ia = self.new_piece(for_player="ia")
        self.next_piece_ia = self.new_piece(for_player="ia")


    def create_empty_grid(self):
            # On initialise la grille avec 0 (cellule vide)
            return [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    def new_piece(self, for_player="humain"):
        # Si on demande une pièce pour le joueur humain et qu'il a reçu le cadeau,
        # on renvoie une pièce facile (ici, on choisit par exemple le carré "O").
        if for_player == "humain" and self.next_piece_easy_humain:
            self.next_piece_easy_humain = False
            piece_type = "O"  # On suppose que "O" est défini dans TETRIMINOS
        elif for_player == "ia" and self.next_piece_easy_ia:
            self.next_piece_easy_ia = False
            piece_type = "O"
        else:
            piece_type = random.choice(list(TETRIMINOS.keys()))
        
        shape = TETRIMINOS[piece_type]
        x = self.cols // 2 - len(shape[0]) // 2
        y = 0
        color = random.choice(COLOR_PALETTE)
        return {"shape": shape, "x": x, "y": y, "color": color}

    
    def place_piece(self, piece, grid):
        shape = piece["shape"]
        # Utilisez .get() pour avoir une couleur par défaut si jamais 'color' n'est pas présent
        color = piece.get("color", "gray")
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    grid_y = piece["y"] + i
                    grid_x = piece["x"] + j
                    grid[grid_y][grid_x] = color  # Stocke la couleur dans la grille

    def valid_position(self, piece, grid, dx=0, dy=0, rotated_shape=None):
        # Utilise rotated_shape si fourni, sinon la forme actuelle
        shape = rotated_shape if rotated_shape is not None else piece["shape"]
        new_x = piece["x"] + dx
        new_y = piece["y"] + dy
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    grid_x = new_x + j
                    grid_y = new_y + i
                    # Vérifier les bornes de la grille
                    if grid_x < 0 or grid_x >= self.cols or grid_y < 0 or grid_y >= self.rows:
                        return False
                    # Vérifier s’il y a déjà une pièce placée
                    if grid[grid_y][grid_x]:
                        return False
        return True
    
    def draw_piece(self, canvas, piece):
        cell_size = 20
        shape = piece["shape"]
        color = piece.get("color", "yellow")
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    x0 = (piece["x"] + j) * cell_size
                    y0 = (piece["y"] + i) * cell_size
                    x1 = x0 + cell_size
                    y1 = y0 + cell_size
                    canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black")

    def place_piece(self, piece, grid):
        shape = piece["shape"]
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    grid_y = piece["y"] + i
                    grid_x = piece["x"] + j
                    grid[grid_y][grid_x] = cell

    def move_piece(self, piece, grid, dx=0, dy=0):
        if self.valid_position(piece, grid, dx, dy):
            piece["x"] += dx
            piece["y"] += dy
            return True
        return False

    def rotate_piece(self, piece, grid):
        shape = piece["shape"]
        # Effectuer une rotation : transposition puis inversion des lignes
        rotated = [list(row) for row in zip(*shape[::-1])]
        if self.valid_position(piece, grid, rotated_shape=rotated):
            piece["shape"] = rotated
            return True
        return False

    def lock_piece(self, piece, grid):
        self.place_piece(piece, grid)
        lines_cleared, cleared_rows = self.clear_lines(grid)
        
        bonus = 0
        if lines_cleared == 2:
            bonus = 100
            # Offrir la pièce facile à l'adversaire
            if grid is self.grid_humain:
                self.next_piece_easy_ia = True
            elif grid is self.grid_ia:
                self.next_piece_easy_humain = True
        elif lines_cleared == 3:
            bonus = 200
        elif lines_cleared == 4:
            bonus = 300
        
        points = lines_cleared * 50 + bonus
        
        if grid is self.grid_humain:
            self.score_humain += points
            # Pour afficher le bonus, on pourra aussi stocker le message (comme vu précédemment)
            self.last_points_message = {"points": points, "grid": "humain", "y": (cleared_rows[0] * 20 + 10) if cleared_rows else None}
        elif grid is self.grid_ia:
            self.score_ia += points
            self.last_points_message = {"points": points, "grid": "ia", "y": (cleared_rows[0] * 20 + 10) if cleared_rows else None}


    def clear_lines(self, grid):
        cleared_rows = []
        new_grid = []
        for i, row in enumerate(grid):
            if all(cell != 0 for cell in row):
                cleared_rows.append(i)
            else:
                new_grid.append(row)
        lines_cleared = len(cleared_rows)
        # Ajoute des lignes vides en haut pour conserver la taille de la grille
        for _ in range(lines_cleared):
            new_grid.insert(0, [0 for _ in range(self.cols)])
        grid[:] = new_grid
        return lines_cleared, cleared_rows

    def update(self):
        # Mise à jour pour le joueur humain
        if not self.move_piece(self.current_piece_humain, self.grid_humain, dy=1):
            self.lock_piece(self.current_piece_humain, self.grid_humain)
            # La pièce suivante devient la pièce en cours, et on en génère une nouvelle
            self.current_piece_humain = self.next_piece_humain
            self.next_piece_humain = self.new_piece(for_player="humain")
        
        # Mise à jour pour l'IA
        if not self.move_piece(self.current_piece_ia, self.grid_ia, dy=1):
            self.lock_piece(self.current_piece_ia, self.grid_ia)
            self.current_piece_ia = self.next_piece_ia
            self.next_piece_ia = self.new_piece(for_player="ia")
            self.ai_target = None
            self.ai_rotations = 0