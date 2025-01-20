import random
import numpy as np

# Mappage des actions vers les directions
ACTIONS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}


class Agent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1):
        """
        Initialise l'agent.

        Args:
            alpha (float): Taux d'apprentissage.
            gamma (float): Facteur d'actualisation.
            epsilon (float): Facteur d'exploration pour epsilon-greedy.
        """
        self.alpha = alpha  # Taux d'apprentissage
        self.gamma = gamma  # Facteur d'actualisation
        self.epsilon = epsilon  # Exploration vs exploitation
        self.q_table = {}  # Initialisation de la Q-table comme un dictionnaire

    def choose_action(self, state):
        """
        Choisit une action en fonction de l'état actuel et de la stratégie epsilon-greedy.

        Args:
            state (tuple): Représentation de l'état actuel.

        Returns:
            str: Action choisie ("UP", "DOWN", "LEFT", "RIGHT").
        """
        # Exploration : Choisir une action aléatoire
        if np.random.uniform(0, 1) < self.epsilon:
            choice = random.choice(list(ACTIONS.keys()))
            dx, dy = ACTIONS[choice]
            mouv = (dx, dy)
            return mouv
        # Exploitation : Choisir l'action avec la meilleure valeur Q
        if state in self.q_table:
            return max(self.q_table[state], key=self.q_table[state].get)
        else:
            # Si l'état n'est pas dans la Q-table, choisir une action aléatoire
            choice = random.choice(list(ACTIONS.keys()))
            dx, dy = ACTIONS[choice]
            mouv = (dx, dy)
            return mouv

    def update_q_value(self, state, reward, next_state):
        """
        Met à jour la Q-table en fonction de la formule de Q-learning.

        Args:
            state (tuple): État actuel.
            action (str): Action effectuée.
            reward (float): Récompense obtenue.
            next_state (tuple): État suivant après l'action.
        """
        # Initialiser l'état s'il n'existe pas dans la Q-table
        if state not in self.q_table:
            self.q_table[state] = {a: 0 for a in ACTIONS.keys()}

        # Initialiser l'état suivant s'il n'existe pas
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0 for a in ACTIONS.keys()}

        # Formule de mise à jour Q-learning
        best_next_action = max(self.q_table[next_state], key=self.q_table[next_state].get)
        self.q_table[state][ACTIONS.keys()] = self.q_table[state][ACTIONS.keys()] + self.alpha * (
            reward + self.gamma * self.q_table[next_state][best_next_action] - self.q_table[state][ACTIONS.keys()]
        )
