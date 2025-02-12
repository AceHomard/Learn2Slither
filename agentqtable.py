import random
import numpy as np
from settings import ACTIONS, OBJECT_MAPPING, OP_DIR
import os


class Agent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=1.0):
        """
        Initializes the agent with learning parameters.

        Parameters:
        alpha (float): Learning rate, how fast the agent updates its knowledge.
        gamma (float): Discount factor, how much future rewards are considered.
        epsilon (float): The exploration rate, which decays with each episode.
        """
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Epsilon decays each episode
        self.q_table = np.zeros((256, len(ACTIONS)))  # Q-table in numpy
        self.last_action = None  # Last action taken

    def show_qtable(self):
        """Returns the Q-table."""
        return self.q_table

    def no_epsilon(self):
        """Reduces epsilon to a small value."""
        self.epsilon = 0.001

    def decay_epsilon(self):
        """
        Reduces epsilon after each episode,
        ensuring it doesn't go below 0.001.
        """
        self.epsilon = max(0.001, self.epsilon * 0.98)

    def get_reduced_state(self, snake_vision_matrix):
        """Encodes the snake's vision into a unique state."""
        state = [OBJECT_MAPPING[obj] for obj in snake_vision_matrix]
        # Calculating the state index in base 4
        state_index = sum(val * (4 ** idx) for idx, val in enumerate(state))

        return state_index

    def choose_action(self, state):
        """
        Chooses an action based on the epsilon-greedy strategy.
        - With probability epsilon, a random action is chosen.
        - Otherwise, the best action based on the Q-table is chosen.
        """
        if np.random.uniform(0, 1) < self.epsilon:
            possible_actions = list(ACTIONS.keys())
            if self.last_action is not None:  # Exploration
                possible_actions.remove(OP_DIR[self.last_action])
            action = random.choice(possible_actions)
        else:  # Exploitation
            action = list(ACTIONS.keys())[np.argmax(self.q_table[state])]
        self.last_action = action
        return action

    def update_q_value(self, state, action, reward,
                       next_state, done, learning=True):
        """
        Updates the Q-value for the given state-action pair
        using the Q-learning update rule.
        - state: The current state of the agent.
        - action: The action taken in the current state.
        - reward: The reward received after taking the action.
        - next_state: The state resulting from taking the action.
        - done: A flag indicating whether the episode has ended.
        - learning: Whether the Q-value should be updated (default is True).
        """
        if learning:
            action_idx = list(ACTIONS.keys()).index(action)
            # Get the best Q-value for the next state
            best_next_q = 0 if done else np.max(self.q_table[next_state])
            self.q_table[state, action_idx] += self.alpha * (
                reward + self.gamma * best_next_q -  # Update rule for Q-value
                self.q_table[state, action_idx]
            )

    def export_model(self, filename):
        """
        Exports the Q-table to a .npy file.
        - filename: The name of the file where the Q-table will be saved.
        """
        os.makedirs("models", exist_ok=True)
        np.save(f'models/{filename}.npy', self.q_table)
        print(f"✅ Model saved to models/{filename}.npy")

    def import_model(self, filename):
        """
        Imports the Q-table from a .npy file.
        - filename: The file from which the Q-table will be loaded.
        """
        try:
            self.q_table = np.load(filename)
            print(f"✅ Model loaded from {filename}")
        except FileNotFoundError:
            print(f"⚠️ File {filename} not found, Q-table init as empty.")
            self.q_table = np.zeros((256, len(ACTIONS)))
