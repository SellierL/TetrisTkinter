# tetris/game.py
import random

# Définition simplifiée des formes de Tetriminos
TETRIMINOS = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1],
          [1, 1]],
    "T": [[0, 1, 0],
          [1, 1, 1]],
    # Vous pouvez ajouter d'autres formes ici...
}

class TetrisGame:
    def __init__(self, rows=20, cols=10):
        self.rows = rows
        self.cols = cols
        self.grid_humain = self.create_empty_grid()
        self.grid_ia = self.create_empty_grid()
        self.score_humain = 0
        self.score_ia = 0
        self.current_piece_humain = self.new_piece()
        self.current_piece_ia = self.new_piece()

    def create_empty_grid(self):
        return [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    def new_piece(self):
        piece_type = random.choice(list(TETRIMINOS.keys()))
        shape = TETRIMINOS[piece_type]
        x = self.cols // 2 - len(shape[0]) // 2
        y = 0
        return {"shape": shape, "x": x, "y": y}

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
        # Placer la pièce sur la grille
        self.place_piece(piece, grid)
        # Supprimer les lignes complètes et récupérer le nombre de lignes supprimées
        lines_cleared = self.clear_lines(grid)
        
        # Calcul du score en fonction du joueur (humain ou IA)
        bonus = 0
        if lines_cleared == 2:
            bonus = 100
        elif lines_cleared == 3:
            bonus = 200
        elif lines_cleared == 4:
            bonus = 300

        # Mise à jour du score
        if grid is self.grid_humain:
            self.score_humain += lines_cleared * 50 + bonus
        elif grid is self.grid_ia:
            self.score_ia += lines_cleared * 50 + bonus


    def clear_lines(self, grid):
        # Créer une nouvelle grille sans les lignes complètes
        new_grid = [row for row in grid if any(cell == 0 for cell in row)]
        lines_cleared = self.rows - len(new_grid)
        # Ajouter des lignes vides en haut pour maintenir la taille de la grille
        for _ in range(lines_cleared):
            new_grid.insert(0, [0 for _ in range(self.cols)])
        grid[:] = new_grid  # Mise à jour de la grille existante
        return lines_cleared


    def update(self):
        # Mise à jour pour le joueur humain
        if not self.move_piece(self.current_piece_humain, self.grid_humain, dy=1):
            self.lock_piece(self.current_piece_humain, self.grid_humain)
            self.current_piece_humain = self.new_piece()
        
        # Mise à jour pour l'IA : la pièce descend automatiquement
        if not self.move_piece(self.current_piece_ia, self.grid_ia, dy=1):
            self.lock_piece(self.current_piece_ia, self.grid_ia)
            self.current_piece_ia = self.new_piece()
            self.ai_target = None
            self.ai_rotations = 0