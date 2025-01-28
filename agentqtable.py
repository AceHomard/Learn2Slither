import random
import numpy as np
from settings import ACTIONS, OBJECT_MAPPING, OP_DIR


class Agent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=1.0):
        self.alpha = alpha  # Taux d'apprentissage
        self.gamma = gamma  # Facteur d'actualisation
        self.epsilon = epsilon  # Epsilon diminue à chaque épisode
        self.q_table = np.zeros((256, len(ACTIONS)))  # Q-table en numpy
        self.last_action = None  # Dernière action effectuée

    def show_qtable(self):
        return self.q_table

    def decay_epsilon(self):
        # Réduit epsilon après chaque épisode
        self.epsilon = max(0.01, self.epsilon * 0.98)

    def get_reduced_state(self, snake_vision_matrix):
        """
        Encode la vision du serpent dans un état unique.
        """
        state = [OBJECT_MAPPING[obj] for obj in snake_vision_matrix]
        # Calcul de l'index de l'état en base 4
        state_index = sum(val * (4 ** idx) for idx, val in enumerate(state))

        # Assurer que l'index reste dans la plage [0, 255]
        return state_index % 256

    def choose_action(self, state):
        # Exploration : Choisir une action aléatoire (en évitant l'action opposée)
        if np.random.uniform(0, 1) < self.epsilon:
            # Filtrer les actions opposées
            possible_actions = list(ACTIONS.keys())
            if self.last_action is not None:
                # Enlever l'action opposée de la liste des actions possibles
                possible_actions.remove(OP_DIR[self.last_action])
            action = random.choice(possible_actions)  # Choisir une action au hasard parmi les actions restantes
            print(f'{action} random {self.last_action}')
        else:
            # Exploitation : Choisir l'action avec la meilleure valeur Q
            action = list(ACTIONS.keys())[np.argmax(self.q_table[state])]  # Retourner l'action avec la meilleure valeur Q
        self.last_action = action  # Mettre à jour la dernière action
        return action

    def update_q_value(self, state, action, reward, next_state, done):
        # Trouver l'indice de l'action
        action_idx = list(ACTIONS.keys()).index(action)  # Convertir l'action en son indice
        best_next_q = 0 if done else np.max(self.q_table[next_state])

        # Mise à jour de la Q-table pour l'état et l'action spécifiés
        self.q_table[state, action_idx] += self.alpha * (
            reward + self.gamma * best_next_q - self.q_table[state, action_idx]
        )
