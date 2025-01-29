import random
import numpy as np
from settings import ACTIONS, OBJECT_MAPPING, OP_DIR


class Agent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=1.0):
        self.alpha = alpha  # Taux d'apprentissage
        self.gamma = gamma  # Facteur d'actualisation
        self.epsilon = epsilon  # Epsilon diminue à chaque épisode
        self.q_table = np.zeros((4, 4, 4, 4, len(ACTIONS)))  # 4 directions, 4 types d'objets, 4 actions
        self.last_action = None  # Dernière action effectuée

    def show_qtable(self):
        return self.q_table

    def decay_epsilon(self):
        # Réduit epsilon après chaque épisode
        self.epsilon = max(0.01, self.epsilon * 0.99)

    def get_state(self, snake_vision_matrix):
        """
        Retourne l'état sous forme de vecteur numpy.
        """
        tmp = np.array([OBJECT_MAPPING[obj] for obj in snake_vision_matrix])
        print(tmp) # [0 0 3 3]
        return tmp

    def choose_action(self, state):
        # Exploration : Choisir une action aléatoire (en évitant l'action opposée)
        if np.random.uniform(0, 1) < self.epsilon:
            possible_actions = list(ACTIONS.keys())
            if self.last_action is not None:
                # Enlever l'action opposée de la liste des actions possibles
                possible_actions.remove(OP_DIR[self.last_action])
            action = random.choice(possible_actions)
        else:
            # Exploitation : Choisir l'action avec la meilleure valeur Q
            action = list(ACTIONS.keys())[np.argmax(self.q_table[state])]
        self.last_action = action
        return action

    def update_q_value(self, state, action, reward, next_state, done):
        action_idx = list(ACTIONS.keys()).index(action)
        if done:
            self.q_table[state][action_idx] += self.alpha * (reward - self.q_table[state][action_idx])
        else:
            best_next_q = np.max(self.q_table[next_state])
            self.q_table[state][action_idx] += self.alpha * (
                reward + self.gamma * best_next_q - self.q_table[state][action_idx]
            )
