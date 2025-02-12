import pygame
from settings import CELL_SIZE
import random


def spawn_apples(grid_size=10, snake=[], num_apples=1, occupied=[]):
    """
    Generates multiple random positions for apples
    without overlapping with the snake or each other.
    """
    apples = []
    while len(apples) < num_apples:
        apple = (random.randint(0, grid_size - 1),
                 random.randint(0, grid_size - 1))
        if apple not in snake and apple not in apples \
                and apple not in occupied:
            apples.append(apple)
    return apples


def spawn_apple(grid_size=10, snake=[], occupied=[]):
    """
    Generates a random position for a single apple without overlap.
    """
    if any(isinstance(i, list) for i in snake):
        snake = [pos for segment in snake for pos in segment]
    if any(isinstance(i, list) for i in occupied):
        occupied = [pos for segment in occupied for pos in segment]

    while True:
        apple = (random.randint(0, grid_size - 1),
                 random.randint(0, grid_size - 1))
        if apple not in snake and apple not in occupied:
            return apple


def draw_grid(screen, gridsize):
    """
    Draws the grid on the screen.
    """
    for x in range(0, CELL_SIZE * gridsize, CELL_SIZE):
        for y in range(0, CELL_SIZE * gridsize, CELL_SIZE):
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, 'white', rect, 1)


def draw_board(screen, snake, green_apples, red_apple, gridsize):
    """
    Draws the game board, including the snake, green apples, and red apple.
    """
    screen.fill("black")
    draw_grid(screen, gridsize)

    # Draw the snake
    for index, segment in enumerate(snake):
        rect = pygame.Rect(segment[1] * CELL_SIZE, segment[0] *
                           CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if index == 0:
            pygame.draw.rect(screen, "darkblue", rect)  # Head of the snake
        else:
            pygame.draw.rect(screen, 'blue', rect)  # Body of the snake

    # Draw the green apples
    for green_apple in green_apples:
        green_rect = pygame.Rect(green_apple[1] * CELL_SIZE, green_apple[0] *
                                 CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, 'green', green_rect)

    # Draw the red apple
    red_rect = pygame.Rect(red_apple[1] * CELL_SIZE, red_apple[0] *
                           CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, 'red', red_rect)
