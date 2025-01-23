import random
import numpy as np
from settings import ACTIONS


class Agent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.alpha = alpha  # Taux d'apprentissage
        self.gamma = gamma  # Facteur d'actualisation
        self.epsilon = epsilon  # Exploration vs exploitation
        self.q_table = {}  # Initialisation de la Q-table comme un dictionnaire

    def choose_action(self, state):
        print(state)
        # Exploration : Choisir une action aléatoire
        if np.random.uniform(0, 1) < self.epsilon:
            return random.choice(list(ACTIONS.keys()))
        # Exploitation : Choisir l'action avec la meilleure valeur Q
        if state in self.q_table:
            return max(self.q_table[state], key=self.q_table[state].get)
        else:
            # Si l'état n'est pas dans la Q-table, choisir une action aléatoire
            return random.choice(list(ACTIONS.keys()))

    def update_q_value(self, state, action, reward, next_state):
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in ACTIONS.keys()}
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0.0 for a in ACTIONS.keys()}

        best_next_action = max(self.q_table[next_state], key=self.q_table[next_state].get)

        self.q_table[state][action] = self.q_table[state][action] + self.alpha * (
            reward + self.gamma * self.q_table[next_state][best_next_action] - self.q_table[state][action]
        )
