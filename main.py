import pygame
import argparse
import os
from settings import SCREEN_SIZE, GRID_SIZE, RGA, RRA, RD, RN, ACTIONS
from snake import get_snake_vision_simple, spawn_snake, \
    get_snake_vision_matrix, display_matrix
from board import draw_board, spawn_apple, spawn_apples
from agentqtable import Agent
import matplotlib.pyplot as plt
import pandas as pd


def reset_game():
    green_apples = spawn_apples(GRID_SIZE, num_apples=2)
    red_apple = spawn_apple(GRID_SIZE, snake=[green_apples])
    snake = spawn_snake(length=3, grid_size=GRID_SIZE,
                        green_apples=green_apples, red_apple=red_apple)
    running = True
    reward = 0
    return green_apples, red_apple, snake, running, reward


def graph(results):
    """
        Affiche l'évolution de la taille du serpent
        et du nombre de déplacements
    """
    snake_sizes, move_counts = zip(*results)  # Extraction des données
    episodes = range(len(snake_sizes))

    plt.figure(figsize=(12, 6))

    # Courbe de la taille du serpent
    plt.subplot(2, 1, 1)
    plt.plot(episodes, snake_sizes, alpha=0.3, label="Taille brute",
             color="blue")
    plt.plot(pd.Series(snake_sizes).rolling(window=100).mean(),
             label="Moyenne mobile (100)", color="red", linewidth=2)
    plt.ylabel("Taille du serpent")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)

    # Courbe du nombre de déplacements
    plt.subplot(2, 1, 2)
    plt.plot(episodes, move_counts, alpha=0.3, label="Déplacements bruts",
             color="green")
    plt.plot(pd.Series(move_counts).rolling(window=100).mean(),
             label="Moyenne mobile (100)", color="orange", linewidth=2)
    plt.xlabel("Épisode")
    plt.ylabel("Nombre de déplacements")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)

    plt.suptitle("Évolution de la taille et des déplacements du serpent")
    plt.show()


def parse_args():
    """Gestion des arguments en ligne de commande"""
    parser = argparse.ArgumentParser(
        description="Entraînement d'un agent Snake avec Q-Learning")
    parser.add_argument("-visual", choices=["on", "off"], default="on",
                        help="Activer/désactiver l'affichage graphique")
    parser.add_argument("-load", type=str,
                        help="Charger un modèle pré-entraîné (fichier)")
    parser.add_argument("-sessions", type=int, default=250,
                        help="Nombre d'épisodes d'entraînement")
    parser.add_argument("-dontlearn", action="store_true",
                        help="Désactiver l'apprentissage (mode validation)")
    parser.add_argument("-dontsave", action="store_true",
                        help="Désactiver la sauvegarde du model")
    parser.add_argument("-noepsil", choices=["on", "off"], default="off",
                        help="Empêcher l'Exploration")
    parser.add_argument("-displayterm", choices=["on", "off"], default="off",
                        help="Affichage terminal")

    return parser.parse_args()


def play_step(agent, snake, green_apples, red_apple, displayterm):
    """ Exécute une action et met à jour l'environnement """
    vision = agent.get_reduced_state(
        get_snake_vision_simple(snake, green_apples, red_apple, GRID_SIZE))
    action = agent.choose_action(vision)

    dx, dy = ACTIONS[action]
    head = (snake[0][0] + dx, snake[0][1] + dy)

    if head in snake[1:] or head[0] < 0 or head[0] >= GRID_SIZE\
            or head[1] < 0 or head[1] >= GRID_SIZE:
        return vision, RD, False, red_apple

    reward = RN
    snake.insert(0, head)
    if head in green_apples:
        green_apples.remove(head)
        green_apples.append(spawn_apple(GRID_SIZE, snake=[snake],
                                        occupied=green_apples + [red_apple]))
        reward = RGA
    elif head == red_apple:
        red_apple = spawn_apple(GRID_SIZE, snake=[snake],
                                occupied=[green_apples])
        if len(snake) > 2:
            snake.pop()
            snake.pop()
            reward = RRA
        else:
            return vision, RD, False, red_apple

    else:
        snake.pop()
    if displayterm:
        display_matrix(get_snake_vision_matrix(
            snake, green_apples, red_apple, GRID_SIZE))
        print(action)
    return vision, reward, True, red_apple


def train_snake(agent, num_episodes=1000, visual=True, learn=True,
                noepsil=False, displayterm=False):
    """ Boucle d'entraînement """
    snake_sizes = []
    next_step = False  # Variable pour contrôler le passage à l'étape suivante
    step_by_step = True
    if noepsil:
        agent.no_epsilon()
    for episode in range(num_episodes):
        agent.decay_epsilon()
        green_apples, red_apple, snake, running, reward = reset_game()
        num_moves = 0
        while running:
            if visual:
                draw_board(screen, snake, green_apples, red_apple)
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return snake_sizes
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                            return snake_sizes
                        elif event.key == pygame.K_SPACE and step_by_step:
                            next_step = True
                        elif event.key == pygame.K_p:
                            step_by_step = True
                        elif event.key == pygame.K_o:
                            step_by_step = False

                if step_by_step and not next_step:
                    continue
                next_step = False

            vision, reward, running, red_apple = play_step(
                agent, snake, green_apples, red_apple, displayterm)
            next_vision = agent.get_reduced_state(get_snake_vision_simple(
                snake, green_apples, red_apple, GRID_SIZE))
            num_moves += 1
            if learn:
                agent.update_q_value(vision, agent.last_action, reward,
                                     next_vision, not running)

            if not running:
                snake_sizes.append((len(snake), num_moves))

    return snake_sizes


def main():
    """ Fonction principale avec gestion des arguments """
    args = parse_args()

    if args.visual == "on":
        pygame.init()
        global screen
        screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        pygame.display.set_caption("Snake 10x10")

    agent = Agent()

    if args.load:
        if os.path.exists(args.load):
            agent.import_model(args.load)
        else:
            print(f"⚠️ Fichier {args.load} introuvable !")

    snake_sizes = train_snake(agent, num_episodes=args.sessions,
                              visual=(args.visual == "on"),
                              learn=not args.dontlearn,
                              noepsil=(args.noepsil == "on"),
                              displayterm=(args.displayterm == "on"))
    if args.visual == "on":
        pygame.quit()

    save = not args.dontsave
    if save:
        agent.export_model(f'{args.sessions}sess')

    # Affichage des stats
    if snake_sizes:
        max_size = max([r[0] for r in snake_sizes])
        max_moves = max([r[1] for r in snake_sizes])
        print(f"Taille max atteinte : {max_size},\
Déplacements max : {max_moves}")
        graph(snake_sizes)


if __name__ == "__main__":
    main()
