import pygame
from settings import SCREEN_SIZE, GRID_SIZE, RGA, RRA, RD, RN, ACTIONS
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


def play_step(agent, snake, green_apples, red_apple):
    """
    Exécute une action de l'agent et met à jour l'environnement.
    Retourne :
    - Nouvelle vision du serpent
    - Récompense obtenue
    - État du jeu (running)
    """
    vision = agent.get_reduced_state(get_snake_vision_simple(snake, green_apples, red_apple, GRID_SIZE))
    action = agent.choose_action(vision)
    dx, dy = ACTIONS[action]
    head = (snake[0][0] + dx, snake[0][1] + dy)

    # Gestion des collisions
    if head in snake[1:] or head[0] < 0 or head[0] >= GRID_SIZE or head[1] < 0 or head[1] >= GRID_SIZE:
        return vision, RD, False  # Fin de partie

    # Gestion des pommes
    reward = RN  # Par défaut, mouvement normal
    snake.insert(0, head)
    if head in green_apples:
        green_apples.remove(head)
        green_apples.append(spawn_apple(GRID_SIZE, snake=[snake], occupied=green_apples + [red_apple]))
        reward = RGA
    elif head == red_apple:
        red_apple = spawn_apple(GRID_SIZE, snake=[snake], occupied=[green_apples])
        if len(snake) > 2:
            snake.pop()
            snake.pop()
            reward = RRA
        else:
            return vision, RD, False  # Fin de partie

    # Retrait de la queue si pas de pomme mangée
    else:
        snake.pop()

    return vision, reward, True


def train_snake(agent, num_episodes=1000):
    """ Boucle d'entraînement principale """
    snake_sizes = []

    for episode in range(num_episodes):
        agent.decay_epsilon()
        green_apples, red_apple, snake, running, reward, _, vision_snake, _, _ = reset_game()

        while running:
            vision, reward, running = play_step(agent, snake, green_apples, red_apple)
            next_vision = agent.get_reduced_state(get_snake_vision_simple(snake, green_apples, red_apple, GRID_SIZE))
            agent.update_q_value(vision, agent.last_action, reward, next_vision, not running)

            if not running:
                snake_sizes.append(len(snake))

    return snake_sizes


def main():
    """ Fonction principale """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    pygame.display.set_caption("Snake 10x10")

    agent = Agent()
    snake_sizes = train_snake(agent)

    pygame.quit()
    print("Taille max atteinte :", max(snake_sizes))
    graph(snake_sizes)


if __name__ == "__main__":
    main()