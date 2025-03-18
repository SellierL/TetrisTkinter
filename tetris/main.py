# tetris/main.py
import tkinter as tk
from tetris.gui import TetrisGUI

def main():
    # Création de la fenêtre principale
    root = tk.Tk()
    root.title("Tetris à deux joueurs")
    
    # Initialisation de l'interface graphique
    app = TetrisGUI(root)
    
    # Lancement de la boucle principale de Tkinter
    root.mainloop()

if __name__ == "__main__":
    main()
