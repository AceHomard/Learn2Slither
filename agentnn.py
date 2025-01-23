import torch
import torch.nn as nn


class DQN(nn.Module):
    def __init__(self, input_size, output_size):
        """
        Initialise un réseau de neurones pour le Deep Q-Learning.

        Args:
            input_size (int): Taille de l'entrée (taille de l'état).
            output_size (int): Taille de la sortie (nombre d'actions).
        """
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_size, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, output_size)

    def forward(self, x):
        """
        Passe l'entrée à travers le réseau.

        Args:
            x (torch.Tensor): Tenseur représentant l'état (entrée).

        Returns:
            torch.Tensor: Tenseur représentant les valeurs Q pour chaque action.
        """
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = self.fc4(x)
        return x
