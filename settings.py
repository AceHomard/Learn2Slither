# Paramètres du jeu
CELL_SIZE = 60
GRID_SIZE = 10
SCREEN_SIZE = CELL_SIZE * GRID_SIZE

RGA = 50
RRA = -5
RD = -100
RN = -0.1

# Mappage des actions vers les directions
ACTIONS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}

OBJECT_MAPPING = {
    "W": 0,  # Mur ou corps du serpent
    "G": 1,  # Pomme verte
    "R": 2,  # Pomme rouge
    "0": 3   # Case vide
}

# Actions opposées
OP_DIR = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}
