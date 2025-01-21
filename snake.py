import random


def spawn_snake(length=3, grid_size=10, green_apples=[], red_apple=None):
    """
    Génère un serpent aléatoire en partant de la tête et en construisant le corps.
    """
    while True:
        # Choisir une position de départ aléatoire pour la tête
        head_x = random.randint(0, grid_size - 1)
        head_y = random.randint(0, grid_size - 1)
        head = (head_x, head_y)

        # Vérifie que la tête n'est pas sur une pomme
        all_apples = green_apples + ([red_apple] if red_apple else [])
        if head in all_apples:
            continue

        # Initialisation du serpent avec la tête
        snake = [head]

        # Directions possibles : UP, DOWN, LEFT, RIGHT
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # Générer les segments du corps
        for _ in range(length - 1):
            possible_directions = []
            for dx, dy in directions:
                new_x = snake[-1][0] + dx
                new_y = snake[-1][1] + dy
                new_pos = (new_x, new_y)

                # Vérifier que la position est valide
                if (
                    0 <= new_x < grid_size and  # Dans la grille
                    0 <= new_y < grid_size and  # Dans la grille
                    new_pos not in snake and  # Pas sur le corps du serpent
                    new_pos not in all_apples  # Pas sur une pomme
                ):
                    possible_directions.append((dx, dy))

            # Si aucune direction n'est valide, le placement échoue
            if not possible_directions:
                break

            # Choisir une direction aléatoire parmi les possibles
            dx, dy = random.choice(possible_directions)
            new_segment = (snake[-1][0] + dx, snake[-1][1] + dy)
            snake.append(new_segment)

        # Si le serpent a la bonne longueur, on le retourne
        if len(snake) == length:
            return snake


def get_snake_vision_matrix_human(snake, green_apples, red_apple, grid_size):
    """
    Retourne une matrice représentant la vision du serpent.
    """
    head_x, head_y = snake[0]  # Position de la tête du serpent

    # Initialiser la matrice vide
    matrix = [[" " for _ in range(grid_size + 2)] for _ in range(grid_size + 2)]

    # Placer la tête
    matrix[head_x+1][head_y+1] = "H"

    # Directions : UP, DOWN, LEFT, RIGHT
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dx, dy in directions:
        x, y = head_x, head_y
        while 0 <= x < grid_size and 0 <= y < grid_size:  # Explorer tant qu'on est dans la grille
            x += dx
            y += dy
            if not (0 <= x < grid_size and 0 <= y < grid_size):
                break  # Sortie de la grille
            if (x, y) in snake:
                matrix[x+1][y+1] = "S"
            elif (x, y) in green_apples:
                matrix[x+1][y+1] = "G"
            elif (x, y) == red_apple:
                matrix[x+1][y+1] = "R"
            else:
                matrix[x+1][y+1] = "0"
        matrix[x+1][y+1] = "W"
    return matrix


def get_snake_vision_matrix(snake, green_apples, red_apple, grid_size):
    """
    Retourne une matrice représentant la vision du serpent.
    """
    head_x, head_y = snake[0]  # Position de la tête du serpent

    # Initialiser la matrice vide
    vision = []  # Liste pour stocker la vision simplifiée

    # Directions : UP, DOWN, LEFT, RIGHT
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dx, dy in directions:
        x, y = head_x, head_y
        while 0 <= x < grid_size and 0 <= y < grid_size:  # Explorer tant qu'on est dans la grille
            x += dx
            y += dy
            if not (0 <= x < grid_size and 0 <= y < grid_size):
                vision.append("W")
                break  # Sortie de la grille
            if (x, y) in snake:
                vision.append("S")
            elif (x, y) in green_apples:
                vision.append("G")
            elif (x, y) == red_apple:
                vision.append("R")
            else:
                vision.append("0")
    return vision


def display_matrix(matrix):
    """
    Affiche la matrice sous forme de chaîne de caractères.
    """
    for row in matrix:
        print("".join(row))  # Convertir chaque ligne en chaîne et l'afficher
    print()
