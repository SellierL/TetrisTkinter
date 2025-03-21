# tetris/game.py
import random
import time

# Définition des Tetriminos classiques
TETRIMINOS = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1],
          [1, 1]],
    "T": [[0, 1, 0],
          [1, 1, 1]],
    "L": [[1, 0],
          [1, 0],
          [1, 1]],
    "J": [[0, 1],
          [0, 1],
          [1, 1]],
    "S": [[0, 1, 1],
          [1, 1, 0]],
    "Z": [[1, 1, 0],
          [0, 1, 1]]
}

# Définition de quelques pièces spéciales pour la règle "Pièce rigolote"
SPECIAL_PIECES = {
    "heart": [
        [0, 1, 0],
        [1, 1, 1],
        [1, 0, 1]
    ],
    "star": [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0]
    ]
}

# Palette de couleurs (vous pouvez utiliser des codes hexadécimaux)
COLOR_PALETTE = ["#aed6f1","#d2b4de", "#f5b7b1", "#f9e79f", "#abebc6", "#c0392b", "#dc7633"]

class TetrisGame:
    def __init__(self, rows=20, cols=10):
        self.rows = rows
        self.cols = cols
        self.grid_humain = self.create_empty_grid()
        self.grid_ia = self.create_empty_grid()
        self.score_humain = 0
        self.score_ia = 0
        self.game_over_humain = False
        self.game_over_ia = False

        # Règle "Pause douceur"
        self.next_pause_threshold = 1000
        self.pause_active = False
        self.pause_end_time = 0

        # Règle "Cadeau surprise"
        self.next_piece_easy_humain = False
        self.next_piece_easy_ia = False

        # Règle "Pièce rigolote"
        self.next_special_humain = False
        self.next_special_ia = False
        self.next_special_threshold = 3000

        # Règle "Arc-en-ciel"
        self.rainbow_active = False
        self.rainbow_end_time = 0
        self.next_rainbow_time = time.time() + 120  # Activation toutes les 2 minutes

        # Gestion des pièces : pièce en cours et pièce suivante pour chaque joueur
        self.current_piece_humain = self.new_piece(for_player="humain")
        self.next_piece_humain = self.new_piece(for_player="humain")
        self.current_piece_ia = self.new_piece(for_player="ia")
        self.next_piece_ia = self.new_piece(for_player="ia")

        # Pour l'IA, on pourra ajouter des attributs supplémentaires (ici simplifiés)
        self.ai_target = None
        self.ai_rotations = 0

        # Pour afficher un message de gain temporaire (floating points)
        self.last_points_message = None

    def create_empty_grid(self):
        return [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    def new_piece(self, for_player="humain"):
        # Priorité à la pièce spéciale si le flag est actif
        if for_player == "humain" and self.next_special_humain:
            self.next_special_humain = False
            shape = random.choice(list(SPECIAL_PIECES.values()))
        elif for_player == "ia" and self.next_special_ia:
            self.next_special_ia = False
            shape = random.choice(list(SPECIAL_PIECES.values()))
        # Si cadeau surprise, on renvoie la pièce facile ("O")
        elif for_player == "humain" and self.next_piece_easy_humain:
            self.next_piece_easy_humain = False
            shape = TETRIMINOS["O"]
        elif for_player == "ia" and self.next_piece_easy_ia:
            self.next_piece_easy_ia = False
            shape = TETRIMINOS["O"]
        else:
            shape = random.choice(list(TETRIMINOS.values()))
        
        x = self.cols // 2 - len(shape[0]) // 2
        y = 0
        color = random.choice(COLOR_PALETTE)
        special = shape in list(SPECIAL_PIECES.values())
        return {"shape": shape, "x": x, "y": y, "color": color, "special": special}

    def valid_position(self, piece, grid, dx=0, dy=0, rotated_shape=None):
        shape = rotated_shape if rotated_shape is not None else piece["shape"]
        new_x = piece["x"] + dx
        new_y = piece["y"] + dy
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    grid_x = new_x + j
                    grid_y = new_y + i
                    if grid_x < 0 or grid_x >= self.cols or grid_y < 0 or grid_y >= self.rows:
                        return False
                    if grid[grid_y][grid_x]:
                        return False
        return True

    def move_piece(self, piece, grid, dx=0, dy=0):
        if self.valid_position(piece, grid, dx, dy):
            piece["x"] += dx
            piece["y"] += dy
            return True
        return False

    def rotate_piece(self, piece, grid):
        shape = piece["shape"]
        rotated = [list(row) for row in zip(*shape[::-1])]
        if self.valid_position(piece, grid, rotated_shape=rotated):
            piece["shape"] = rotated
            return True
        return False

    def place_piece(self, piece, grid):
        shape = piece["shape"]
        color = piece["color"]
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    grid_y = piece["y"] + i
                    grid_x = piece["x"] + j
                    grid[grid_y][grid_x] = color

    def clear_lines(self, grid):
        cleared_rows = []
        new_grid = []
        for i, row in enumerate(grid):
            if all(cell != 0 for cell in row):
                cleared_rows.append(i)
            else:
                new_grid.append(row)
        lines_cleared = len(cleared_rows)
        for _ in range(lines_cleared):
            new_grid.insert(0, [0 for _ in range(self.cols)])
        grid[:] = new_grid
        return lines_cleared, cleared_rows

    def lock_piece(self, piece, grid):
        self.place_piece(piece, grid)
        lines_cleared, cleared_rows = self.clear_lines(grid)

        bonus = 0
        # Règle "Cadeau surprise" : si exactement 2 lignes sont éliminées, l'adversaire reçoit une pièce facile.
        if lines_cleared == 2:
            bonus = 100
            if grid is self.grid_humain:
                self.next_piece_easy_ia = True
            elif grid is self.grid_ia:
                self.next_piece_easy_humain = True
        elif lines_cleared == 3:
            bonus = 200
        elif lines_cleared == 4:
            bonus = 300

        # Règle "Pièce rigolote" : si la pièce spéciale est bien placée (ici, par simplicité, si la pièce est proche du bas)
        if piece.get("special") and piece["y"] > self.rows - 4:
            bonus += 100

        points = lines_cleared * 50 + bonus

        if grid is self.grid_humain:
            self.score_humain += points
        elif grid is self.grid_ia:
            self.score_ia += points

        # Règle "Pause douceur" : active un ralentissement si le seuil est atteint
        if self.score_humain >= self.next_pause_threshold or self.score_ia >= self.next_pause_threshold:
            self.pause_active = True
            self.pause_end_time = time.time() + 10  # 10 secondes de ralentissement
            self.next_pause_threshold += 1000

        # Règle "Pièce rigolote" : active la prochaine pièce spéciale à chaque seuil de 3000 points
        if self.score_humain >= self.next_special_threshold:
            self.next_special_humain = True
            self.next_special_threshold += 3000
        if self.score_ia >= self.next_special_threshold:
            self.next_special_ia = True
            self.next_special_threshold += 3000

        # Optionnel : vous pouvez stocker un message de points pour affichage temporaire
        if cleared_rows:
            y_pos = cleared_rows[0] * 20 + 10
        else:
            y_pos = None
        self.last_points_message = {"points": points, "grid": "humain" if grid is self.grid_humain else "ia", "y": y_pos}

    def update(self):
        # Règle "Arc-en-ciel" : activation toutes les 2 minutes pendant 20 secondes
        if time.time() >= self.next_rainbow_time:
            self.rainbow_active = True
            self.rainbow_end_time = time.time() + 20
            self.next_rainbow_time = time.time() + 120
        if self.rainbow_active and time.time() > self.rainbow_end_time:
            self.rainbow_active = False

        # Mise à jour pour le joueur humain (s'il n'est pas en game over)
        if not self.game_over_humain:
            if not self.move_piece(self.current_piece_humain, self.grid_humain, dy=1):
                self.lock_piece(self.current_piece_humain, self.grid_humain)
                if not self.valid_position(self.next_piece_humain, self.grid_humain):
                    self.game_over_humain = True
                else:
                    self.current_piece_humain = self.next_piece_humain
                    self.next_piece_humain = self.new_piece(for_player="humain")
        
        # Mise à jour pour le joueur IA (s'il n'est pas en game over)
        if not self.game_over_ia:
            if not self.move_piece(self.current_piece_ia, self.grid_ia, dy=1):
                self.lock_piece(self.current_piece_ia, self.grid_ia)
                if not self.valid_position(self.next_piece_ia, self.grid_ia):
                    self.game_over_ia = True
                else:
                    self.current_piece_ia = self.next_piece_ia
                    self.next_piece_ia = self.new_piece(for_player="ia")
                    self.ai_target = None
                    self.ai_rotations = 0