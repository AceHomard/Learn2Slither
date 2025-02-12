import random


def spawn_snake(length=3, grid_size=10, green_apples=[], red_apple=None):
    """
    Generates a random snake starting from the head and constructing the body.
    """
    while True:
        # Choose a random starting position for the head
        head_x = random.randint(0, grid_size - 1)
        head_y = random.randint(0, grid_size - 1)
        head = (head_x, head_y)

        # Check that the head is not on an apple
        all_apples = green_apples + ([red_apple] if red_apple else [])
        if head in all_apples:
            continue

        # Initialize the snake with the head
        snake = [head]

        # Possible directions: UP, DOWN, LEFT, RIGHT
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # Generate the body segments
        for _ in range(length - 1):
            possible_directions = []
            for dx, dy in directions:
                new_x = snake[-1][0] + dx
                new_y = snake[-1][1] + dy
                new_pos = (new_x, new_y)

                # Check if the position is valid
                if (
                    0 <= new_x < grid_size and  # Inside the grid
                    0 <= new_y < grid_size and  # Inside the grid
                    new_pos not in snake and  # Not on the snake's body
                    new_pos not in all_apples  # Not on an apple
                ):
                    possible_directions.append((dx, dy))

            # If no valid direction is found, the placement fails
            if not possible_directions:
                break

            # Choose a random direction from the possible ones
            dx, dy = random.choice(possible_directions)
            new_segment = (snake[-1][0] + dx, snake[-1][1] + dy)
            snake.append(new_segment)

        # If the snake has the correct length, return it
        if len(snake) == length:
            return snake


def get_snake_vision_simple(snake, green_apples, red_apple, grid_size):
    """
    Returns a simplified vision of the 4 directions around the snake.
    Directions with no obstacles ('S', 'G', 'R') are considered neutral (0),
    unless they are near the wall within 1 tile of distance.
    """
    head_x, head_y = snake[0]  # Position of the snake's head

    # Directions: UP, DOWN, LEFT, RIGHT
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    vision = []

    for dx, dy in directions:
        x, y = head_x, head_y
        found = False  # Flag to indicate if an obstacle is found

        while 0 <= x < grid_size and 0 <= y < grid_size:
            x += dx
            y += dy

            # Check for obstacles
            if (x, y) in snake:
                vision.append("W")  # Snake's body
                found = True
                break
            elif (x, y) in green_apples:
                vision.append("G")  # Green apple
                found = True
                break
            elif (x, y) == red_apple:
                vision.append("R")  # Red apple
                found = True
                break

        if not found:  # If no obstacle is found
            # Check if the head is near the wall within 1 tile
            if head_x + dx < 0 or head_x + dx >= grid_size or head_y + dy < 0 \
                    or head_y + dy >= grid_size:
                vision.append("W")  # If near the wall, mark as 'W'
            else:
                vision.append("0")  # Otherwise, neutral direction
    return vision


def get_snake_vision_matrix(snake, green_apples, red_apple, grid_size):
    """
    Returns a matrix representing the snake's vision.
    """
    head_x, head_y = snake[0]  # Position of the snake's head

    # Initialize the empty matrix
    matrix = [[" " for _ in range(grid_size + 2)]
              for _ in range(grid_size + 2)]

    # Place the head
    matrix[head_x + 1][head_y + 1] = "H"

    # Directions: UP, DOWN, LEFT, RIGHT
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dx, dy in directions:
        x, y = head_x, head_y
        while 0 <= x < grid_size and 0 <= y < grid_size:
            x += dx
            y += dy
            if not (0 <= x < grid_size and 0 <= y < grid_size):
                break  # Out of bounds
            if (x, y) in snake:
                matrix[x + 1][y + 1] = "S"
            elif (x, y) in green_apples:
                matrix[x + 1][y + 1] = "G"
            elif (x, y) == red_apple:
                matrix[x + 1][y + 1] = "R"
            else:
                matrix[x + 1][y + 1] = "0"
        matrix[x + 1][y + 1] = "W"
    return matrix


def display_matrix(matrix):
    """
    Displays the matrix as a string.
    """
    for row in matrix:
        print("".join(row))  # Convert each row to a string and print it
    print()
