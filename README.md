# Tetris à Deux Joueurs

Ce projet est une implémentation d'un jeu Tetris en Python utilisant la bibliothèque Tkinter. Le jeu met en scène deux joueurs : un joueur humain contrôlé via le clavier et une IA qui joue de manière autonome. Le projet intègre également un système de score avec des bonus pour la suppression de lignes multiples.

## Fonctionnalités

- **Deux grilles de jeu** : Une pour le joueur humain et une pour l'IA, affichées côte à côte.
- **Contrôles intuitifs** : Le joueur humain utilise les touches fléchées pour déplacer (gauche, droite et bas) et faire tourner la pièce (haut).
- **Intelligence artificielle améliorée** : L'IA évalue l'état de sa grille pour sélectionner le meilleur coup possible.
- **Système de score dynamique** : Calcul du score avec des bonus (ex. : bonus pour plusieurs lignes supprimées simultanément).
- **Génération d'exécutable** : Possibilité de compiler le projet en un fichier exécutable (.exe) grâce à PyInstaller.

## Prérequis

- Python 3.7 ou supérieur
- Tkinter (inclus avec Python dans la plupart des distributions)
- [Virtualenv](https://docs.python.org/fr/3/library/venv.html) pour créer un environnement virtuel

## Installation (2 & 3 non necessaire si vous choisisez le .exe)

1. **Cloner le dépôt**

   ```sh
   git clone https://github.com/SellierL/TetrisTkinter.git
   cd TetrisTkinter
   ```

2. **Créer un environnement virtuel et l'activer**
    ```sh
    python -m venv envTetris
    .\envTetris\Scripts\Activate
    ```

3. **Installer les dépendances dans requirements.txt présent dans le projet**
    ```sh
    pip install -r requirements.txt
    ```

## Lancer le projet

Vous trouverez directement un .exe dans le dossier ./dist pour lancer le projet.
Lancez le projet avec la commande suivante dans le répertoir racine du projet :
```sh
python -m tetris.main
```

## Structure du Projet

La structure du projet est organisée de manière modulaire :

```sh
TETRISTKINTER/
├── tetris/                # Code source du jeu
│   ├── __init__.py
│   ├── main.py          # Point d'entrée du jeu
│   ├── game.py          # Logique du jeu (grilles, pièces, gestion des règles)
│   ├── gui.py           # Interface graphique avec Tkinter (création de la fenêtre, canvas, gestion des widgets)
│   └── ai.py            # Logique de l'IA (décision de placement, stratégie simple)
├── tests/               # Tests unitaires ou d'intégration
│   └── test_game.py
├── README.md            # Instructions pour lancer le projet
├── PROMPTS.md           # Liste des prompts utilisés pour réaliser le projet
└── requirements.txt     # Liste des dépendances
```