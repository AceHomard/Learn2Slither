import pygame
from settings import SCREEN_SIZE, GRID_SIZE, RGA, RRA, RD, RN, RTL, ACTIONS, ACTION_TO_INDEX
from snake import spawn_snake, get_snake_vision_vector, display_matrix
from board import draw_board, spawn_apples, spawn_apple
from agentnn import DQN
import torch.optim as optim
import random
import torch
import torch.nn as nn
import torch.nn.functional as F


def reset_game(trewards):
    green_apples = spawn_apples(GRID_SIZE, num_apples=2)
    red_apple = spawn_apple(GRID_SIZE, snake=[green_apples])
    snake = spawn_snake(length=3, grid_size=GRID_SIZE, green_apples=green_apples, red_apple=red_apple)
    result = None  # Le jeu attend la première input
    running = True  # On continue le jeu
    trewards = 0
    reward = 0
    mouv = 0
    vision_snake = get_snake_vision_vector(snake, green_apples, red_apple, GRID_SIZE)
    state_tensor = vision_snake.unsqueeze(0)  # Transforme [22] en [1, 22]
    action = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])  # Exploration

    return green_apples, red_apple, snake, result, running, reward, mouv, trewards, state_tensor, action


def train(model, optimizer, state, action, reward, next_state, done, gamma=0.9):
    # Calculer les valeurs Q actuelles
    q_values = model(state)  # Sortie : [1, 4]

    action_idx = ACTION_TO_INDEX[action]
    q_value = q_values[0, action_idx]  # Récupérer Q(s, a) pour l'action choisie
    # Calculer la cible Q
    with torch.no_grad():  # Désactiver la rétropropagation pour cette partie
        if done:
            target = torch.tensor([reward], dtype=torch.float32)  # Si terminé, Q cible = récompense
        else:
            next_q_values = model(next_state)  # Valeurs Q pour l'état suivant
            max_next_q_value = torch.max(next_q_values)  # max(Q(s', a'))
            target = torch.tensor([reward + gamma * max_next_q_value], dtype=torch.float32)
    
    target = target.squeeze()  # Transforme [1] en scalaire
    # Calculer la perte (erreur quadratique moyenne entre Q actuel et cible)
    loss = F.mse_loss(q_value, target)

    # Effectuer la rétropropagation et mettre à jour les poids
    optimizer.zero_grad()  # Réinitialiser les gradients
    loss.backward()        # Calculer les gradients
    optimizer.step()       # Mettre à jour les poids

    return loss.item()


def get_valid_actions(snake, direction):
    """
    Retourne une liste d'actions valides pour le serpent, en évitant de revenir en arrière
    ou de choisir des directions qui entraîneraient une collision immédiate.

    Args:
        snake (list): Liste des positions (x, y) du serpent.
        direction (str): La direction actuelle ("UP", "DOWN", "LEFT", "RIGHT").

    Returns:
        list: Liste des actions valides.
    """
    # Actions opposées à éviter
    opposite_directions = {
        "UP": "DOWN",
        "DOWN": "UP",
        "LEFT": "RIGHT",
        "RIGHT": "LEFT",
    }

    # Position actuelle de la tête
    head_x, head_y = snake[0]

    # Toutes les directions possibles
    valid_actions = []

    for action, (dx, dy) in ACTIONS.items():
        # Évite de revenir en arrière
        if action == opposite_directions[direction]:
            continue

        # Calcule la position potentielle de la tête
        next_x, next_y = head_x + dx, head_y + dy

        # Vérifie si cette position est dans les limites du plateau et sans collision
        if (
            0 <= next_x < GRID_SIZE and
            0 <= next_y < GRID_SIZE and
            (next_x, next_y) not in snake
        ):
            valid_actions.append(action)

    return valid_actions


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

    # Initialisation pour le modèle
    model = DQN(input_size=22, output_size=4)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    epsilon = 1.0  # Exploration initiale
    epsilon_min = 0.05
    epsilon_decay = 0.999  # Décroissance d'epsilon
    num_episodes = 10000
    episode_counter = 0

    # Initialisation des statistiques
    cumulative_rewards = []
    losses = []
    num_green_apples_eaten = 0
    action = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])  # Exploration
    # Boucle d'entraînement
    for episode in range(num_episodes):
        episode_counter += 1
        running = True
        reward = 0
        trewards = 0

        # Reset du jeu
        green_apples, red_apple, snake, result, running, reward, mouv, trewards, state_tensor, action = reset_game(trewards)

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

            # Prédictions du modèle
            q_values = model(state_tensor)

            # Stratégie epsilon-greedy
            if random.uniform(0, 1) < epsilon:
                valid_actions = get_valid_actions(snake, action)
                if valid_actions:
                    action = random.choice(valid_actions)
                else:
                    action = action
            else:
                action_idx = torch.argmax(q_values).item()  # Exploitation
                action = ["UP", "DOWN", "LEFT", "RIGHT"][action_idx]

            dx, dy = ACTIONS[action]
            mouv = (dx, dy)

            if mouv is not None:
                head = (snake[0][0] + dx, snake[0][1] + dy)
                snake.insert(0, head)
                if head in green_apples:
                    green_apples.remove(head)
                    green_apples.append(spawn_apple(grid_size=GRID_SIZE, snake=[snake], occupied=green_apples + [red_apple]))
                    reward = RGA
                    num_green_apples_eaten += 1
                elif head == red_apple:
                    red_apple = spawn_apple(grid_size=GRID_SIZE, snake=[snake], occupied=[green_apples])
                    if len(snake) > 2:
                        snake.pop()
                        snake.pop()
                    else:
                        reward = RD
                        loss = train(model, optimizer, state_tensor, action, reward, state_tensor, done=True)
                        cumulative_rewards.append(trewards)
                        losses.append(loss)
                        green_apples, red_apple, snake, result, running, reward, mouv, trewards, state_tensor, action = reset_game(
                            trewards
                        )
                        break
                    reward = RRA

                elif (
                    head[0] < 0 or head[0] >= GRID_SIZE or
                    head[1] < 0 or head[1] >= GRID_SIZE or
                    head in snake[1:]
                ):
                    reward = RD
                    loss = train(model, optimizer, state_tensor, action, reward, state_tensor, done=True)
                    cumulative_rewards.append(trewards)
                    losses.append(loss)

                    green_apples, red_apple, snake, result, running, reward, mouv, trewards, state_tensor, action = reset_game(
                        trewards
                    )
                    break

                else:
                    reward = RN
                    snake.pop()

                if len(snake) >= 10:
                    reward += RTL

                trewards += reward
                next_state_tensor = get_snake_vision_vector(snake, green_apples, red_apple, GRID_SIZE).unsqueeze(0)
                loss = train(model, optimizer, state_tensor, action, reward, next_state_tensor, done=False)
                state_tensor = next_state_tensor

        # Mise à jour de la stratégie epsilon-greedy
        if episode_counter % 100 == 0:
            print(f"Q_values pour l'épisode {episode_counter}: {q_values} Pommes | {num_green_apples_eaten} Eps : {epsilon}")
        if episode_counter % 1000 == 0:
            epsilon = 0.2  # Rehausse temporairement l'exploration

        epsilon = max(epsilon_min, epsilon * epsilon_decay)

    # Afficher les statistiques globales après l'entraînement
    print(f"Récompenses moyennes sur {num_episodes} épisodes : {sum(cumulative_rewards) / num_episodes}")
    pygame.quit()


if __name__ == "__main__":
    main()
