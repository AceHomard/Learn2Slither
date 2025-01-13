import pygame
import random

pygame.init()

CELL_SIZE = 60
GRID_SIZE = 10
SCREEN_SIZE = CELL_SIZE * GRID_SIZE


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Snake 10x10")


def spawn_snake(length=3, grid_size=10, apples=[]):
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
        else:
            print("oui")


def spawn_apples(grid_size=10, snake=[], num_apples=1, occupied=[]):
    """
    Génère plusieurs positions aléatoires pour des pommes sans overlap avec le serpent ou entre elles.
    """
    apples = []
    while len(apples) < num_apples:
        apple = (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))
        if apple not in snake and apple not in apples and apple not in occupied:
            apples.append(apple)
    return apples


def spawn_apple(grid_size=10, snake=[], occupied=[]):
    """
    Génère une position aléatoire pour une seule pomme sans overlap.
    """
    while True:
        apple = (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))
        if apple not in snake and apple not in occupied:
            return apple


# Générer les pommes en premier
green_apples = spawn_apples(GRID_SIZE, num_apples=2)
red_apple = spawn_apple(GRID_SIZE, snake=[green_apples])  # Évite le chevauchement

# Générer le serpent
snake = spawn_snake(length=3, grid_size=GRID_SIZE, apples=[green_apples, red_apple])

# Variables du jeu
clock = pygame.time.Clock()


def draw_grid():
    for x in range(0, SCREEN_SIZE, CELL_SIZE):
        for y in range(0, SCREEN_SIZE, CELL_SIZE):
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 1)


def draw_board():
    screen.fill(BLACK)
    draw_grid()
    # Dessiner le serpent
    for index, segment in enumerate(snake):
        rect = pygame.Rect(segment[1] * CELL_SIZE, segment[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if index == 0:  # La tête
            pygame.draw.rect(screen, "darkblue", rect)  # Couleur différente pour la tête
        else:  # Le corps
            pygame.draw.rect(screen, BLUE, rect)
    # Dessiner les pommes vertes
    for green_apple in green_apples:
        green_rect = pygame.Rect(green_apple[1] * CELL_SIZE, green_apple[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, GREEN, green_rect)
    red_rect = pygame.Rect(red_apple[1] * CELL_SIZE, red_apple[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, RED, red_rect)


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
    print(len(snake))
    return matrix


def display_matrix(matrix):
    """
    Affiche la matrice sous forme de chaîne de caractères.
    """
    for row in matrix:
        print("".join(row))  # Convertir chaque ligne en chaîne et l'afficher


def reset_game():
    global snake, direction, green_apples, red_apple, running
    snake = spawn_snake(length=3, grid_size=GRID_SIZE, apples=[green_apples, red_apple])
    direction = None  # Le jeu attend la première input
    green_apples = spawn_apples(GRID_SIZE, num_apples=2)
    red_apple = spawn_apple(GRID_SIZE, snake=[green_apples])
    running = True  # On continue le jeu


# Mode pas-à-pas
step_by_step = False  # Activer ou désactiver le mode pas-à-pas
next_step = False    # Variable pour avancer à l'étape suivante

# Boucle principale du jeu
running = True
direction = None
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Gestion des touches
        elif event.type == pygame.KEYDOWN:
            # Contrôles du serpent
            if event.key == pygame.K_UP and direction != (1, 0):
                direction = (-1, 0)
            elif event.key == pygame.K_DOWN and direction != (-1, 0):
                direction = (1, 0)
            elif event.key == pygame.K_LEFT and direction != (0, 1):
                direction = (0, -1)
            elif event.key == pygame.K_RIGHT and direction != (0, -1):
                direction = (0, 1)
            elif event.key == pygame.K_ESCAPE:
                running = False

            # Mode pas-à-pas : Avancer à l'étape suivante avec ESPACE
            if step_by_step and event.key == pygame.K_SPACE:
                next_step = True
    draw_board()
    pygame.display.flip()
    vision_matrix = get_snake_vision_matrix(snake, green_apples, red_apple, GRID_SIZE)
    display_matrix(vision_matrix)
    # Si le mode pas-à-pas est activé, attendre l'appui sur ESPACE
    if step_by_step:
        if not next_step:  # Tant que l'utilisateur n'appuie pas sur ESPACE, on ne fait rien
            continue
        next_step = False  # Réinitialiser après avoir avancé d'une étape
    if direction is not None:  # Commencer à jouer une fois une direction définie
        # Déplacement du serpent
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        snake.insert(0, head)
        # Gérer la collision avec les pommes vertes
        if head in green_apples:
            # Supprimer la pomme verte mangée
            green_apples.remove(head)
            # Ajouter une nouvelle pomme verte
            green_apples.append(spawn_apple(grid_size=GRID_SIZE, snake=snake + green_apples + [red_apple]))

        # Gérer la collision avec la pomme rouge
        elif head == red_apple:
            red_apple = spawn_apple(grid_size=GRID_SIZE, snake=snake + green_apples + [red_apple])
            if len(snake) > 2:
                snake.pop()
                snake.pop()
            else:
                # print("Game Over!")
                reset_game()  # Réinitialise l'environnement
                continue
        else:
            snake.pop()  # Enlève la dernière cellule si aucune pomme n'est mangée

        # Gérer les collisions avec les murs ou la queue
        if (
            head[0] < 0 or head[0] >= GRID_SIZE or
            head[1] < 0 or head[1] >= GRID_SIZE or
            head in snake[1:]
        ):
            # print("Game Over!")
            # print(head in snake[1:])
            # print(snake)
            # print(f'Len:{len(snake)}')

            reset_game()  # Réinitialise l'environnement
            continue  # Redémarre le jeu
    pass
    clock.tick(8)  # Limite à 8 FPS

pygame.quit()
