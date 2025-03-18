# tests/test_game.py
import unittest
from tetris.game import TetrisGame

class TestTetrisGame(unittest.TestCase):
    def setUp(self):
        self.game = TetrisGame(rows=4, cols=4)  # grille réduite pour le test

    def test_new_piece(self):
        piece = self.game.new_piece()
        self.assertIn("shape", piece)
        self.assertIn("x", piece)
        self.assertIn("y", piece)

    def test_move_piece(self):
        piece = {"shape": [[1]], "x": 1, "y": 1}
        self.game.move_piece(piece, dx=1, dy=1)
        self.assertEqual(piece["x"], 2)
        self.assertEqual(piece["y"], 2)

if __name__ == "__main__":
    unittest.main()