import random
import numpy as np
from settings import ACTIONS, OBJECT_MAPPING, OP_DIR
import os


class Agent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=1.0):
        self.alpha = alpha  # Taux d'apprentissage
        self.gamma = gamma  # Facteur d'actualisation
        self.epsilon = epsilon  # Epsilon diminue à chaque épisode
        self.q_table = np.zeros((256, len(ACTIONS)))  # Q-table en numpy
        self.last_action = None  # Dernière action effectuée

    def show_qtable(self):
        return self.q_table

    def no_epsilon(self):
        # Réduit epsilon
        self.epsilon = 0.01

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
        return state_index

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

    def update_q_value(self, state, action, reward, next_state, done, learning=True):
        if learning:
            action_idx = list(ACTIONS.keys()).index(action)
            best_next_q = 0 if done else np.max(self.q_table[next_state])
            self.q_table[state, action_idx] += self.alpha * (
                reward + self.gamma * best_next_q - self.q_table[state, action_idx]
            )

    def export_model(self, filename):
        """
        Exporte la Q-table sous forme de fichier .npy
        """
        os.makedirs("models", exist_ok=True)  # Crée le dossier models si inexistant
        np.save(f'models/{filename}.npy', self.q_table)  # Sauvegarde sous format NumPy
        print(f"✅ Modèle sauvegardé dans models/{filename}.npy")

    def import_model(self, filename):
        """
        Importe la Q-table depuis un fichier .npy
        """
        try:
            self.q_table = np.load(filename)  # Charge le fichier NumPy
            print(f"✅ Modèle chargé depuis {filename}")
        except FileNotFoundError:
            print(f"⚠️ Fichier {filename} introuvable, initialisation de la Q-table vide.")
            self.q_table = np.zeros((256, len(ACTIONS)))  # Réinitialisation
