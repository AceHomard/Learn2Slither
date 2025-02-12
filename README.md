Learn2Slither - Reinforcement Learning Snake Game 🐍
Overview

Learn2Slither is a reinforcement learning project where an agent learns to play Snake through Q-Learning. The agent interacts with an environment, receives rewards, and improves its performance over time by optimizing its policy.
Features

✅ Q-Learning implementation with a reduced state space (256 states).
✅ Customizable grid size via command-line arguments.
✅ Graphical and terminal visualization options.
✅ Training and evaluation modes (with or without learning).
✅ Model saving/loading for training persistence.
Installation
Requirements

    Python 3.8+
    Required libraries:

    pip install pygame numpy matplotlib pandas

Clone the Repository

git clone https://github.com/AceHomard/Learn2Slither.git
cd Learn2Slither

Usage
Train the Snake

Run the script with:

python main.py -sessions 500 -grid 10 -visual on

📌 Available Arguments:
Argument	Description	Default
-visual	Enable (on) or disable (off) the graphical display	on
-load	Load a pre-trained model (.npy file)	None
-sessions	Number of training episodes	250
-dontlearn	Disable learning (evaluation mode)	False
-dontsave	Prevent model saving	False
-noepsil	Disable exploration (always exploit best action)	off
-displayterm	Show the state matrix in terminal	off
-grid	Set the grid size	10
Example Commands

1️⃣ Train for 1000 episodes with a 12x12 grid

python main.py -sessions 1000 -grid 12

2️⃣ Load a pre-trained model and evaluate

python main.py -load models/1000sess.npy -dontlearn

How It Works
State Representation

The Snake's environment is simplified into a 4^4 = 256 state space. The agent "sees" its surroundings as an encoded vector of values.
Q-Learning Algorithm

    Exploration vs Exploitation: Uses epsilon-greedy to balance randomness and optimal moves.
    Q-Table Update: The agent updates its Q-table based on rewards:
    Q(s,a)←Q(s,a)+α[r+γmax⁡Q(s′,a′)−Q(s,a)]
    Q(s,a)←Q(s,a)+α[r+γmaxQ(s′,a′)−Q(s,a)]

Rewards System
Action	Reward
Eating a green apple	+50
Eating a red apple	-5
Hitting a wall or itself	-50
Normal move	0
Results Visualization

The script generates graphs to analyze learning progress:
📈 Snake length evolution over episodes.
📉 Number of moves per episode.
Model Saving & Loading

The model is stored as a .npy file in the models/ directory.

    Save after training: models/{sessions}sess.npy
    Load an existing model: Use -load with the filename.