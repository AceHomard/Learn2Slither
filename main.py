import pygame
from settings import SCREEN_SIZE, GRID_SIZE
from snake import spawn_snake, get_snake_vision_matrix, display_matrix, choose_action
from board import draw_board, spawn_apples, spawn_apple


def reset_game():
    green_apples = spawn_apples(GRID_SIZE, num_apples=2)
    red_apple = spawn_apple(GRID_SIZE, snake=[green_apples])
    snake = spawn_snake(length=3, grid_size=GRID_SIZE, green_apples=green_apples, red_apple=red_apple)
    result = None  # Le jeu attend la première input
    running = True  # On continue le jeu
    vision_matrix = get_snake_vision_matrix(snake, green_apples, red_apple, GRID_SIZE)
    display_matrix(vision_matrix)
    return green_apples, red_apple, snake, result, running


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    pygame.display.set_caption("Snake 10x10")

    # Générer les pommes en premier
    green_apples = spawn_apples(GRID_SIZE, num_apples=2)
    red_apple = spawn_apple(GRID_SIZE, snake=[], occupied=[green_apples])  # Évite le chevauchement

    # Générer le serpent
    snake = spawn_snake(length=3, grid_size=GRID_SIZE, green_apples=green_apples, red_apple=red_apple)

    # Variables du jeu
    clock = pygame.time.Clock()

    # Mode pas-à-pas
    step_by_step = True  # Activer ou désactiver le mode pas-à-pas
    next_step = False    # Variable pour avancer à l'étape suivante

    # Boucle principale du jeu
    running = True
    vision_matrix = get_snake_vision_matrix(snake, green_apples, red_apple, GRID_SIZE)
    display_matrix(vision_matrix)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Mode pas-à-pas : Avancer à l'étape suivante avec ESPACE
            elif event.type == pygame.KEYDOWN:
                if step_by_step and event.key == pygame.K_SPACE:
                    next_step = True
                elif event.key == pygame.K_ESCAPE:
                    running = False
        draw_board(screen, snake, green_apples, red_apple)
        pygame.display.flip()
        # Si le mode pas-à-pas est activé, attendre l'appui sur ESPACE
        if step_by_step:
            if not next_step:  # Tant que l'utilisateur n'appuie pas sur ESPACE, on ne fait rien
                continue
            next_step = False  # Réinitialiser après avoir avancé d'une étape
        result = choose_action()
        if result is not None:  # Commencer à jouer une fois une direction définie
            # Déplacement du serpent
            head = (snake[0][0] + result[0], snake[0][1] + result[1])
            snake.insert(0, head)
            vision_matrix = get_snake_vision_matrix(snake, green_apples, red_apple, GRID_SIZE)
            display_matrix(vision_matrix)
            # Gérer la collision avec les pommes vertes
            if head in green_apples:
                # Supprimer la pomme verte mangée
                green_apples.remove(head)
                # Ajouter une nouvelle pomme verte
                green_apples.append(spawn_apple(grid_size=GRID_SIZE, snake=[snake], occupied=green_apples + [red_apple]))

            # Gérer la collision avec la pomme rouge
            elif head == red_apple:
                red_apple = spawn_apple(grid_size=GRID_SIZE, snake=[snake], occupied=[green_apples])
                if len(snake) > 2:
                    snake.pop()
                    snake.pop()
                else:
                    # print("Game Over!")
                    green_apples, red_apple, snake, result, running = reset_game()  # Réinitialise l'environnement
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

                green_apples, red_apple, snake, result, running = reset_game()  # Réinitialise l'environnement
                continue  # Redémarre le jeu
        pass
        clock.tick(8)  # Limite à 8 FPS

    pygame.quit()


if __name__ == "__main__":
    main()
