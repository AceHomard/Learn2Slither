import pygame
import argparse
import os
from settings import CELL_SIZE, RGA, RRA, RD, RN, ACTIONS
from snake import get_snake_vision_simple, spawn_snake, \
    get_snake_vision_matrix, display_matrix
from board import draw_board, spawn_apple, spawn_apples
from agentqtable import Agent
import matplotlib.pyplot as plt
import pandas as pd


def reset_game(gridsize):
    """
    Resets the game environment by spawning a new snake, green apples,
    and a red apple.

    Parameters:
    gridsize (int): The size of the game grid.

    Returns:
    tuple: A tuple containing the following elements:
        - green_apples (list): List of green apple positions on the grid.
        - red_apple (tuple): Position of the red apple on the grid.
        - snake (list): List of snake body positions.
        - running (bool): A flag indicating whether the game is running.
        - reward (int): The initial reward for the game.
    """
    green_apples = spawn_apples(gridsize, num_apples=2)
    red_apple = spawn_apple(gridsize, snake=[green_apples])
    snake = spawn_snake(length=3, grid_size=gridsize,
                        green_apples=green_apples, red_apple=red_apple)
    running = True
    reward = 0
    return green_apples, red_apple, snake, running, reward


def graph(results):
    """
    Displays the evolution of the snake's size
    and the number of moves.
    """
    snake_sizes, move_counts = zip(*results)  # Extract data
    episodes = range(len(snake_sizes))

    plt.figure(figsize=(12, 6))

    # Snake size curve
    plt.subplot(2, 1, 1)
    plt.plot(episodes, snake_sizes, alpha=0.3, label="Size", color="blue")
    plt.plot(pd.Series(snake_sizes).rolling(window=100).mean(),
             label="Moving Average (100)", color="red", linewidth=2)
    plt.ylabel("Snake Size")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)

    # Move count curve
    plt.subplot(2, 1, 2)
    plt.plot(episodes, move_counts, alpha=0.3, label="Moves", color="green")
    plt.plot(pd.Series(move_counts).rolling(window=100).mean(),
             label="Moving Average (100)", color="orange", linewidth=2)
    plt.xlabel("Episode")
    plt.ylabel("Number of Moves")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)

    plt.suptitle("Evolution of Snake Size and Moves")
    plt.show()


def parse_args():
    """Handles command-line arguments for training the Snake agent."""
    parser = argparse.ArgumentParser(
        description="Train a Snake agent using Q-Learning")
    parser.add_argument("-visual", choices=["on", "off"], default="on",
                        help="Enable/disable graphical display")
    parser.add_argument("-load", type=str,
                        help="Load a pre-trained model (file path)")
    parser.add_argument("-sessions", type=int, default=250,
                        help="Number of training episodes")
    parser.add_argument("-dontlearn", action="store_true",
                        help="Disable learning (evaluation mode)")
    parser.add_argument("-dontsave", action="store_true",
                        help="Disable model saving")
    parser.add_argument("-noepsil", choices=["on", "off"], default="off",
                        help="Disable exploration")
    parser.add_argument("-displayterm", choices=["on", "off"], default="off",
                        help="Display state matrix in terminal")
    parser.add_argument("-grid", type=int, default=10,
                        help="Size of the grid")
    return parser.parse_args()


def play_step(agent, snake, green_apples, red_apple, displayterm, gridsize):
    """Executes an action and updates the environment."""
    vision = agent.get_reduced_state(
        get_snake_vision_simple(snake, green_apples, red_apple, gridsize))
    action = agent.choose_action(vision)

    dx, dy = ACTIONS[action]
    head = (snake[0][0] + dx, snake[0][1] + dy)

    if head in snake[1:] or head[0] < 0 or head[0] >= gridsize\
            or head[1] < 0 or head[1] >= gridsize:
        return vision, RD, False, red_apple

    reward = RN
    snake.insert(0, head)
    if head in green_apples:
        green_apples.remove(head)
        green_apples.append(spawn_apple(gridsize, snake=[snake],
                                        occupied=green_apples + [red_apple]))
        reward = RGA
    elif head == red_apple:
        red_apple = spawn_apple(gridsize, snake=[snake],
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
            snake, green_apples, red_apple, gridsize))
        print(action)
    return vision, reward, True, red_apple


def train_snake(agent, num_episodes=1000, gridsize=10, visual=True, learn=True,
                noepsil=False, displayterm=False):
    """Training loop for the Snake agent."""
    snake_sizes = []
    next_step = False
    step_by_step = True
    if noepsil:
        agent.no_epsilon()
    for episode in range(num_episodes):
        agent.decay_epsilon()
        green_apples, red_apple, snake, running, reward = reset_game(gridsize)
        num_moves = 0
        while running:
            if visual:
                draw_board(screen, snake, green_apples, red_apple, gridsize)
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
                agent, snake, green_apples, red_apple, displayterm, gridsize)
            next_vision = agent.get_reduced_state(get_snake_vision_simple(
                snake, green_apples, red_apple, gridsize))
            num_moves += 1
            if learn:
                agent.update_q_value(vision, agent.last_action, reward,
                                     next_vision, not running)

            if not running:
                snake_sizes.append((len(snake), num_moves))

    return snake_sizes


def main():
    """Main function to handle arguments and run the Snake training."""
    try:
        args = parse_args()

        if args.visual == "on":
            pygame.init()
            global screen
            screen = pygame.display.set_mode(
                (CELL_SIZE * args.grid, CELL_SIZE * args.grid))
            pygame.display.set_caption(f"Snake {args.grid}x{args.grid}")

        agent = Agent()

        if args.load:
            if os.path.exists(args.load):
                agent.import_model(args.load)
            else:
                print(f"⚠️ File {args.load} not found!")

        snake_sizes = train_snake(agent, num_episodes=args.sessions,
                                  gridsize=args.grid,
                                  visual=(args.visual == "on"),
                                  learn=not args.dontlearn,
                                  noepsil=(args.noepsil == "on"),
                                  displayterm=(args.displayterm == "on"))
        if args.visual == "on":
            pygame.quit()

        save = not args.dontsave
        if save:
            agent.export_model(f'{args.sessions}sess')

        # Display stats
        if snake_sizes:
            max_size = max([r[0] for r in snake_sizes])
            max_moves = max([r[1] for r in snake_sizes])
            print(f"Max size reached: {max_size}, Max moves: {max_moves}")
            graph(snake_sizes)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
