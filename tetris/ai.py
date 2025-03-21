# tetris/ai.py

def rotate_shape(shape):
    """Retourne la forme après une rotation de 90° dans le sens horaire."""
    return [list(row) for row in zip(*shape[::-1])]

def clear_lines(grid, rows, cols):
    new_grid = [row for row in grid if any(cell == 0 for cell in row)]
    lines_cleared = rows - len(new_grid)
    for _ in range(lines_cleared):
        new_grid.insert(0, [0] * cols)
    return new_grid

def get_column_heights(grid, cols, rows):
    heights = [0] * cols
    for j in range(cols):
        for i in range(rows):
            if grid[i][j]:
                heights[j] = rows - i
                break
    return heights

def ai_move(game):
    import random
    # Logique très simple pour l'IA :
    move = random.choice(["left", "right", "none"])
    if move == "left":
        game.move_piece(game.current_piece_ia, game.grid_ia, dx=-1)
    elif move == "right":
        game.move_piece(game.current_piece_ia, game.grid_ia, dx=1)
    # La pièce descend toujours d'un cran
    game.move_piece(game.current_piece_ia, game.grid_ia, dy=1)

def count_holes(grid, cols, rows):
    holes = 0
    for j in range(cols):
        block_found = False
        for i in range(rows):
            if grid[i][j]:
                block_found = True
            elif block_found:
                holes += 1
    return holes

def bumpiness(heights):
    b = 0
    for i in range(len(heights) - 1):
        b += abs(heights[i] - heights[i+1])
    return b

def evaluate_grid(grid, rows, cols):
    """
    Calcule un score pour la grille basée sur plusieurs critères.
    Les coefficients sont choisis d’après des travaux sur l’IA Tetris.
    """
    coef_lines = 0.760666
    coef_height = 0.510066
    coef_holes = 0.35663
    coef_bumpiness = 0.184483

    completed_lines = sum(1 for row in grid if all(cell != 0 for cell in row))
    heights = get_column_heights(grid, cols, rows)
    aggregate_height = sum(heights)
    holes = count_holes(grid, cols, rows)
    bump = bumpiness(heights)
    score = (coef_lines * completed_lines) - (coef_height * aggregate_height) - (coef_holes * holes) - (coef_bumpiness * bump)
    return score

def simulate_drop(piece, grid, game):
    """
    Simule la chute de la pièce jusqu’à ce qu’elle entre en collision.
    Retourne la pièce dans sa position finale.
    """
    sim_piece = {"shape": [row[:] for row in piece["shape"]],
                 "x": piece["x"],
                 "y": piece["y"]}
    while game.valid_position(sim_piece, grid, dx=0, dy=1):
        sim_piece["y"] += 1
    return sim_piece

def simulate_place(piece, grid, game):
    """
    Retourne une copie de la grille avec la pièce placée et les lignes éventuelles supprimées.
    """
    new_grid = [row[:] for row in grid]
    shape = piece["shape"]
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                new_grid[piece["y"] + i][piece["x"] + j] = cell
    new_grid = clear_lines(new_grid, game.rows, game.cols)
    return new_grid

def find_best_move(game):
    """
    Parcourt toutes les possibilités (rotations et positions horizontales)
    pour la pièce IA et retourne la configuration qui donne le meilleur score.
    Renvoie un dictionnaire avec :
       - "target_x" : la position horizontale cible
       - "rotation_count" : le nombre de rotations à appliquer
    """
    best_score = -float('inf')
    best_move = None
    current_piece = game.current_piece_ia
    # Copie de la forme actuelle (l’état de base)
    original_shape = [row[:] for row in current_piece["shape"]]
    
    # Tester 0, 1, 2 et 3 rotations
    for rotation in range(4):
        rotated_shape = original_shape
        for _ in range(rotation):
            rotated_shape = rotate_shape(rotated_shape)
        shape_width = len(rotated_shape[0])
        # Pour chaque position horizontale possible
        for x in range(game.cols - shape_width + 1):
            candidate_piece = {"shape": [row[:] for row in rotated_shape],
                               "x": x,
                               "y": 0}
            # Si la position initiale n'est pas valide, on passe
            if not game.valid_position(candidate_piece, game.grid_ia):
                continue
            final_piece = simulate_drop(candidate_piece, game.grid_ia, game)
            simulated_grid = simulate_place(final_piece, game.grid_ia, game)
            score = evaluate_grid(simulated_grid, game.rows, game.cols)
            if score > best_score:
                best_score = score
                best_move = {"target_x": x, "rotation_count": rotation}
    return best_move

def ai_move(game):
    """
    Amélioration de l'IA :
    - Calcule le meilleur déplacement pour la pièce IA.
    - Si la pièce n'est pas encore alignée avec la configuration cible,
      effectue une rotation ou un déplacement horizontal.
    - Sinon, laisse la gravité (déplacement vertical automatique) faire son travail.
    """
    best_move = find_best_move(game)
    if best_move is None:
        return

    # Initialiser la cible IA dans le jeu si nécessaire
    if not hasattr(game, 'ai_target') or game.ai_target is None:
        game.ai_target = best_move
        game.ai_rotations = 0  # Compteur de rotations appliquées

    # D'abord, appliquer les rotations nécessaires
    if game.ai_rotations < game.ai_target["rotation_count"]:
        if game.rotate_piece(game.current_piece_ia, game.grid_ia):
            game.ai_rotations += 1
        return

    # Une fois la rotation effectuée, ajuster la position horizontale
    target_x = game.ai_target["target_x"]
    if game.current_piece_ia["x"] < target_x:
        game.move_piece(game.current_piece_ia, game.grid_ia, dx=1)
    elif game.current_piece_ia["x"] > target_x:
        game.move_piece(game.current_piece_ia, game.grid_ia, dx=-1)
    # Si la pièce est alignée, on laisse la gravité la faire descendre.