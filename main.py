import pygame
from settings import SCREEN_SIZE, GRID_SIZE, RGA, RRA, RD, RN, RTL, ACTIONS
from snake import spawn_snake, get_snake_vision_simple, display_matrix
from board import draw_board, spawn_apples, spawn_apple
from agentqtable import Agent
import matplotlib.pyplot as plt
import pandas as pd


def reset_game():
    green_apples = spawn_apples(GRID_SIZE, num_apples=2)
    red_apple = spawn_apple(GRID_SIZE, snake=[green_apples])
    snake = spawn_snake(length=3, grid_size=GRID_SIZE, green_apples=green_apples, red_apple=red_apple)
    running = True
    reward = 0
    mouv = 0
    result = None
    vision = 0
    vision_snake = get_snake_vision_simple(snake, green_apples, red_apple, GRID_SIZE)
    return green_apples, red_apple, snake, running, reward, mouv, vision_snake, result, vision


def graph(snake_sizes):
    snake_sizes_series = pd.Series(snake_sizes)

    # Calcul d'une moyenne mobile sur 100 épisodes pour lisser les fluctuations
    rolling_mean = snake_sizes_series.rolling(window=100).mean()

    # Création du graphique
    plt.figure(figsize=(10, 5))
    plt.plot(snake_sizes, alpha=0.3, label="Taille brute du serpent", color="blue")  # Valeurs brutes en semi-transparent
    plt.plot(rolling_mean, label="Moyenne mobile (100 épisodes)", color="red", linewidth=2)  # Moyenne mobile en rouge

    # Ajout des labels et titres
    plt.xlabel("Épisode")
    plt.ylabel("Taille moyenne du serpent")
    plt.title("Évolution de la taille du serpent au fil des épisodes (lissée)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)

    # Affichage du graphique
    plt.show()


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    pygame.display.set_caption("Snake 10x10")

    # Initialisation des variables
    green_apples = spawn_apples(GRID_SIZE, num_apples=2)
    red_apple = spawn_apple(GRID_SIZE, snake=[], occupied=[green_apples])
    snake = spawn_snake(length=3, grid_size=GRID_SIZE, green_apples=green_apples, red_apple=red_apple)
    clock = pygame.time.Clock()

    # Mode pas-à-pas
    step_by_step = False
    next_step = False
    snake_sizes = []
    num_episodes = 2000
    episode_counter = 0
    vision_snake = get_snake_vision_simple(snake, green_apples, red_apple, GRID_SIZE)
    agent = Agent()
    # Boucle d'entraînement
    for episode in range(num_episodes):
        episode_counter += 1
        running = True
        agent.decay_epsilon()
        # Reset du jeu
        green_apples, red_apple, snake, running, reward, mouv, vision_snake, result, vision = reset_game()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if step_by_step and event.key == pygame.K_SPACE:
                        next_step = True
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_p:
                        step_by_step = True
                    elif event.key == pygame.K_o:
                        step_by_step = False

            draw_board(screen, snake, green_apples, red_apple)
            pygame.display.flip()

            if step_by_step:
                if not next_step:
                    continue
                next_step = False
            vision = agent.get_reduced_state(vision_snake)
            result = agent.choose_action(vision)
            dx, dy = ACTIONS[result]
            mouv = (dx, dy)

            if mouv is not None:
                head = (snake[0][0] + dx, snake[0][1] + dy)
                snake.insert(0, head)
                if head in green_apples:
                    green_apples.remove(head)
                    green_apples.append(spawn_apple(grid_size=GRID_SIZE, snake=[snake], occupied=green_apples + [red_apple]))
                    reward = RGA
                elif head == red_apple:
                    red_apple = spawn_apple(grid_size=GRID_SIZE, snake=[snake], occupied=[green_apples])
                    if len(snake) > 2:
                        snake.pop()
                        snake.pop()
                    else:
                        reward = RD
                        agent.update_q_value(vision, result, reward, vision, True)
                        snake_sizes.append(len(snake))
                        green_apples, red_apple, snake, running, reward, mouv, vision_snake, result, vision = reset_game()
                        break
                    reward = RRA

                elif (
                    head[0] < 0 or head[0] >= GRID_SIZE or
                    head[1] < 0 or head[1] >= GRID_SIZE or
                    head in snake[1:]
                ):
                    reward = RD
                    agent.update_q_value(vision, result, reward, vision, True)
                    snake_sizes.append(len(snake))
                    green_apples, red_apple, snake, running, reward, mouv, vision_snake, result, vision = reset_game()
                    break

                else:
                    reward = RN
                    snake.pop()

                vision_snake_new = get_snake_vision_simple(snake, green_apples, red_apple, GRID_SIZE)
                agent.update_q_value(vision, result, reward, agent.get_reduced_state(vision_snake_new), False)
                vision_snake = vision_snake_new

    pygame.quit()
    graph(snake_sizes)


if __name__ == "__main__":
    main()
