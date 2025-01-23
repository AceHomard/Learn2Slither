# Paramètres du jeu
CELL_SIZE = 60
GRID_SIZE = 10
SCREEN_SIZE = CELL_SIZE * GRID_SIZE

RGA = 100
RRA = -5
RD = -20
RN = -0.05
RTL = 100

# Mappage des actions vers les directions
ACTIONS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}

ACTION_TO_INDEX = {
    "UP": 0,
    "DOWN": 1,
    "LEFT": 2,
    "RIGHT": 3,
}
