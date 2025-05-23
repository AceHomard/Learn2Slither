# Game parameters
CELL_SIZE = 60

RGA = 50  # Green apple reward
RRA = -10  # Red apple reward
RD = -50  # Wall or self collision penalty
RN = -0.1  # Normal move penalty

# Mapping actions to directions
ACTIONS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}

# Object mapping (states)
OBJECT_MAPPING = {
    "W": 0,  # Wall or snake body
    "G": 1,  # Green apple
    "R": 2,  # Red apple
    "0": 3   # Empty cell
}

# Opposite directions for actions
OP_DIR = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}
