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
    Génère un serpent aléatoire et contigu sur une grille sans overlap avec les pommes.
    """
    while True:
        # Choisir une position de départ aléatoire
        head_x = random.randint(0, grid_size - 1)
        head_y = random.randint(0, grid_size - 1)

        # Choisir une direction aléatoire : horizontal ou vertical
        direction = random.choice(["horizontal", "vertical"])

        # Générer le serpent
        snake = [(head_x, head_y)]  # Tête du serpent
        for i in range(1, length):
            if direction == "horizontal":
                new_y = head_y - i
                if 0 <= new_y < grid_size:
                    snake.append((head_x, new_y))
                else:
                    break
            else:
                new_x = head_x - i
                if 0 <= new_x < grid_size:
                    snake.append((new_x, head_y))
                else:
                    break

        # Vérifie que le serpent a bien la bonne longueur et n'est pas sur une pomme
        if len(snake) == length and all(cell not in apples for cell in snake):
            return snake


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
direction = (0, 1)  # Direction initiale : vers la droite


def draw_grid():
    for x in range(0, SCREEN_SIZE, CELL_SIZE):
        for y in range(0, SCREEN_SIZE, CELL_SIZE):
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 1)


def draw_board():
    screen.fill(BLACK)
    draw_grid()
    # Dessiner le serpent
    for segment in snake:
        rect = pygame.Rect(segment[1] * CELL_SIZE, segment[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, BLUE, rect)
    # Dessiner les pommes vertes
    for green_apple in green_apples:
        green_rect = pygame.Rect(green_apple[1] * CELL_SIZE, green_apple[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, GREEN, green_rect)
    red_rect = pygame.Rect(red_apple[1] * CELL_SIZE, red_apple[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, RED, red_rect)


# Mode pas-à-pas
step_by_step = False  # Activer ou désactiver le mode pas-à-pas
next_step = False    # Variable pour avancer à l'étape suivante

# Boucle principale du jeu
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Gestion des touches
        if event.type == pygame.KEYDOWN:
            # Contrôles du serpent
            if event.key == pygame.K_UP and direction != (1, 0):
                direction = (-1, 0)
                print("U")
            elif event.key == pygame.K_DOWN and direction != (-1, 0):
                direction = (1, 0)
                print("D")
            elif event.key == pygame.K_LEFT and direction != (0, 1):
                direction = (0, -1)
                print("L")
            elif event.key == pygame.K_RIGHT and direction != (0, -1):
                direction = (0, 1)
                print("R")

            # Mode pas-à-pas : Avancer à l'étape suivante avec ESPACE
            if step_by_step and event.key == pygame.K_SPACE:
                next_step = True

    # Si le mode pas-à-pas est activé, attendre l'appui sur ESPACE
    if step_by_step:
        if not next_step:  # Tant que l'utilisateur n'appuie pas sur ESPACE, on ne fait rien
            continue
        next_step = False  # Réinitialiser après avoir avancé d'une étape

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
            print("Game Over!")
            running = False
            break
    else:
        snake.pop()  # Enlève la dernière cellule si aucune pomme n'est mangée

    # Gérer les collisions avec les murs ou la queue
    if (
        head[0] < 0 or head[0] >= GRID_SIZE or
        head[1] < 0 or head[1] >= GRID_SIZE or
        head in snake[1:]
    ):
        print("Game Over!")
        print(head in snake[1:])
        print(snake)
        running = False
        break

    # Affichage
    draw_board()
    pygame.display.flip()
    clock.tick(200)  # Limite à 8 FPS

pygame.quit()
