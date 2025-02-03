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


def get_snake_vision_simple(snake, green_apples, red_apple, grid_size):
    """
    Retourne une vision simplifiée des 4 directions autour du serpent.
    Les directions sans obstacles ('S', 'G', 'R') sont considérées comme neutres (0), 
    sauf si elles sont proches du mur à 1 case de distance.
    """
    head_x, head_y = snake[0]  # Position de la tête du serpent

    # Directions : UP, DOWN, LEFT, RIGHT
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    vision = []

    for dx, dy in directions:
        x, y = head_x, head_y
        found = False  # Flag pour savoir si on a trouvé un obstacle

        while 0 <= x < grid_size and 0 <= y < grid_size:  # Explorer tant qu'on est dans la grille
            x += dx
            y += dy

            # Vérification des obstacles
            if (x, y) in snake:
                vision.append("W")  # Corps du serpent
                found = True
                break
            elif (x, y) in green_apples:
                vision.append("G")  # Pomme verte
                found = True
                break
            elif (x, y) == red_apple:
                vision.append("R")  # Pomme rouge
                found = True
                break

        if not found:  # Si aucun obstacle n'a été trouvé
            # Vérifier si la tête est proche du mur à 1 case
            if head_x + dx < 0 or head_x + dx >= grid_size or head_y + dy < 0 or head_y + dy >= grid_size:
                vision.append("W")  # Si proche du mur, marquer comme 'W'
            else:
                vision.append("0")  # Sinon direction neutre
    return vision


def get_snake_vision_matrix(snake, green_apples, red_apple, grid_size):
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


# def get_snake_vision_vector(snake, green_apples, red_apple, grid_size):
#     """
#     Retourne un vecteur PyTorch représentant la vision du serpent.

#     Args:
#         snake (list): Liste des coordonnées du serpent.
#         green_apples (list): Liste des coordonnées des pommes vertes.
#         red_apple (tuple): Coordonnées de la pomme rouge.
#         grid_size (int): Taille de la grille.

#     Returns:
#         torch.Tensor: Vecteur numérique représentant la vision.
#     """
#     head_x, head_y = snake[0]  # Position de la tête du serpent

#     vision = []  # Liste pour stocker la vision numérique

#     # Directions : UP, DOWN, LEFT, RIGHT
#     directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

#     for dx, dy in directions:
#         x, y = head_x, head_y
#         while 0 <= x < grid_size and 0 <= y < grid_size:  # Explorer tant qu'on est dans la grille
#             x += dx
#             y += dy
#             if not (0 <= x < grid_size and 0 <= y < grid_size):
#                 vision.append(OBJECT_MAPPING["W"])
#                 break  # Sortie de la grille
#             if (x, y) in snake:
#                 vision.append(OBJECT_MAPPING["S"])
#             elif (x, y) in green_apples:
#                 vision.append(OBJECT_MAPPING["G"])
#             elif (x, y) == red_apple:
#                 vision.append(OBJECT_MAPPING["R"])
#             else:
#                 vision.append(OBJECT_MAPPING["0"])
#     # Convertir la liste en vecteur PyTorch
#     return torch.tensor(vision, dtype=torch.float32)


def display_matrix(matrix):
    """
    Affiche la matrice sous forme de chaîne de caractères.
    """
    for row in matrix:
        print("".join(row))  # Convertir chaque ligne en chaîne et l'afficher
    print()
