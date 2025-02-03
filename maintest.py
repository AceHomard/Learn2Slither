import pygame
import argparse
import csv
import os
from settings import SCREEN_SIZE, GRID_SIZE, RGA, RRA, RD, RN, ACTIONS
from snake import get_snake_vision_simple, spawn_snake
from board import draw_board, spawn_apple, spawn_apples
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


def parse_args():
    """Gestion des arguments en ligne de commande"""
    parser = argparse.ArgumentParser(description="Entraînement d'un agent Snake avec Q-Learning")

    parser.add_argument("-visual", choices=["on", "off"], default="on", help="Activer/désactiver l'affichage graphique")
    parser.add_argument("-load", type=str, help="Charger un modèle pré-entraîné (fichier)")
    parser.add_argument("-sessions", type=int, default=250, help="Nombre d'épisodes d'entraînement")
    parser.add_argument("-dontlearn", action="store_true", help="Désactiver l'apprentissage (mode validation)")
    parser.add_argument("-step-by-step", action="store_true", help="Mode pas-à-pas (appuyer sur espace pour avancer)")
    parser.add_argument("-noepsil", choices=["on", "off"], default="off", help="Empêcher l'Exploration")

    return parser.parse_args()


def save_results(filename, snake_sizes):
    """Enregistre les tailles de serpent dans un fichier CSV"""
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Episode", "Snake Size"])
        for i, size in enumerate(snake_sizes):
            writer.writerow([i, size])
    print(f"Résultats sauvegardés dans {filename}")


def play_step(agent, snake, green_apples, red_apple):
    """ Exécute une action et met à jour l'environnement """
    vision = agent.get_reduced_state(get_snake_vision_simple(snake, green_apples, red_apple, GRID_SIZE))
    action = agent.choose_action(vision)
    dx, dy = ACTIONS[action]
    head = (snake[0][0] + dx, snake[0][1] + dy)

    if head in snake[1:] or head[0] < 0 or head[0] >= GRID_SIZE or head[1] < 0 or head[1] >= GRID_SIZE:
        return vision, RD, False

    reward = RN
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
            return vision, RD, False

    else:
        snake.pop()

    return vision, reward, True


def train_snake(agent, num_episodes=1000, visual=True, learn=True, step_by_step=False, noepsil=False):
    """ Boucle d'entraînement """
    snake_sizes = []
    if noepsil:
        agent.no_epsilon()
    for episode in range(num_episodes):
        agent.decay_epsilon()
        green_apples, red_apple, snake, running, reward, _, vision_snake, _, _ = reset_game()

        while running:
            if visual:
                draw_board(screen, snake, green_apples, red_apple)
                pygame.display.flip()
            if step_by_step:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return snake_sizes
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        break

            vision, reward, running = play_step(agent, snake, green_apples, red_apple)
            next_vision = agent.get_reduced_state(get_snake_vision_simple(snake, green_apples, red_apple, GRID_SIZE))

            if learn:
                agent.update_q_value(vision, agent.last_action, reward, next_vision, not running)

            if not running:
                snake_sizes.append(len(snake))

    return snake_sizes


def main():
    """ Fonction principale avec gestion des arguments """
    args = parse_args()

    # Initialisation pygame si affichage activé
    if args.visual == "on":
        pygame.init()
        global screen
        screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        pygame.display.set_caption("Snake 10x10")

    agent = Agent()
    # Chargement d'un modèle si spécifié
    if args.load:
        if os.path.exists(args.load):
            agent.import_model(args.load)
            print(f"Modèle chargé depuis {args.load}")
        else:
            print(f"⚠️ Fichier {args.load} introuvable !")

    # Lancement de l'entraînement
    snake_sizes = train_snake(agent, num_episodes=args.sessions,
                              visual=(args.visual == "on"),
                              learn=not args.dontlearn,
                              step_by_step=args.step_by_step,
                              noepsil=(args.noepsil == "on"))
    if args.visual == "on":
        pygame.quit()

    # Sauvegarde des résultats
    # save_results("snake_results.csv", snake_sizes)
    agent.export_model(f'{args.sessions}sess')
    print("Taille max atteinte :", max(snake_sizes))
    graph(snake_sizes)


if __name__ == "__main__":
    main()
