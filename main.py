import pygame
from settings import SCREEN_SIZE, GRID_SIZE, RGA, RRA, RD, RN, RTL, ACTIONS
from snake import spawn_snake, get_snake_vision_matrix, display_matrix
from board import draw_board, spawn_apples, spawn_apple
from agent import Agent


def reset_game():
    green_apples = spawn_apples(GRID_SIZE, num_apples=2)
    red_apple = spawn_apple(GRID_SIZE, snake=[green_apples])
    snake = spawn_snake(length=3, grid_size=GRID_SIZE, green_apples=green_apples, red_apple=red_apple)
    result = None  # Le jeu attend la première input
    running = True  # On continue le jeu
    trewards = 0
    rewards = 0
    mouv = 0
    return green_apples, red_apple, snake, result, running, rewards, mouv, trewards


def update_rewards(rewards, bonus):
    rewards += bonus
    return rewards


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
    step_by_step = False  # Activer ou désactiver le mode pas-à-pas
    next_step = False    # Variable pour avancer à l'étape suivante

    # Boucle principale du jeu
    running = True
    vision_matrix = get_snake_vision_matrix(snake, green_apples, red_apple, GRID_SIZE)
    state = tuple(tuple(row) for row in vision_matrix)  # Convertir en tuple de tuples

    # display_matrix(vision_matrix)
    rewards = 0
    trewards = 0
    agent = Agent()
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
        state = tuple(tuple(row) for row in vision_matrix)  # Convertir en tuple de tuples
        print(state)
        result = agent.choose_action(state)
        dx, dy = ACTIONS[result]
        mouv = (dx, dy)
        if mouv is not None:  # Commencer à jouer une fois une direction définie
            # Déplacement du serpent
            head = (snake[0][0] + mouv[0], snake[0][1] + mouv[1])
            snake.insert(0, head)
            # Gérer la collision avec les pommes vertes
            if head in green_apples:
                # Supprimer la pomme verte mangée
                green_apples.remove(head)
                # Ajouter une nouvelle pomme verte
                green_apples.append(spawn_apple(grid_size=GRID_SIZE, snake=[snake], occupied=green_apples + [red_apple]))
                rewards = RGA
            # Gérer la collision avec la pomme rouge
            elif head == red_apple:
                red_apple = spawn_apple(grid_size=GRID_SIZE, snake=[snake], occupied=[green_apples])
                if len(snake) > 2:
                    snake.pop()
                    snake.pop()
                else:
                    # print("Game Over!")
                    rewards = RD
                    # Mettre à jour la Q-table
                    vision_matrix = get_snake_vision_matrix(snake, green_apples, red_apple, GRID_SIZE)
                    new_state = tuple(tuple(row) for row in vision_matrix)
                    agent.update_q_value(state, result, rewards, new_state)
                    trewards = update_rewards(trewards, rewards)
                    print(trewards)
                    # print("Q-table après cette partie :")
                    # for state, actions in agent.q_table.items():
                    #     print(f"État : {state}")
                    #     for action, q_value in actions.items():
                    #         print(f"  Action {action}: Q = {q_value:.2f}")
                    # print("=" * 50)

                    green_apples, red_apple, snake, result, running, rewards, mouv, trewards = reset_game()  # Réinitialise l'environnement
                    continue
                rewards = RRA
            # Gérer les collisions avec les murs ou la queue
            elif (
                head[0] < 0 or head[0] >= GRID_SIZE or
                head[1] < 0 or head[1] >= GRID_SIZE or
                head in snake[1:]
            ):
                rewards = RD
                # Mettre à jour la Q-table
                vision_matrix = get_snake_vision_matrix(snake, green_apples, red_apple, GRID_SIZE)
                new_state = tuple(tuple(row) for row in vision_matrix)
                agent.update_q_value(state, result, rewards, new_state)
                trewards = update_rewards(trewards, rewards)
                print(trewards)
                # print("Q-table après cette partie :")
                # for state, actions in agent.q_table.items():
                #     print(f"État : {state}")
                #     for action, q_value in actions.items():
                #         print(f"  Action {action}: Q = {q_value:.2f}")
                # print("=" * 50)

                green_apples, red_apple, snake, result, running, rewards, mouv, trewards = reset_game()  # Réinitialise l'environnement
                continue  # Redémarre le jeu
            else:
                rewards = RN
                snake.pop()  # Enlève la dernière cellule si aucune pomme n'est mangée

            if len(snake) >= 10:
                rewards = RTL
            # Mettre à jour la Q-table
            vision_matrix = get_snake_vision_matrix(snake, green_apples, red_apple, GRID_SIZE)
            new_state = tuple(tuple(row) for row in vision_matrix)
            agent.update_q_value(state, result, rewards, new_state)
            trewards = update_rewards(trewards, rewards)

            # Affiche le score actuel
            print(f"Récompenses cumulées : {trewards}")
        pass
        clock.tick(8)  # Limite à 8 FPS

    pygame.quit()


if __name__ == "__main__":
    main()
