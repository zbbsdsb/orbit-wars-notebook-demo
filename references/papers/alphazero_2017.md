# Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm

**Authors**: David Silver, Thomas Hubert, Julian Schrittwieser, Ioannis Antonoglou, Matthew Lai, Arthur Guez, Marc Lanctot, Laurent Sifre, Dharshan Kumaran, Thore Graepel, Demis Hassabis
**Institution**: DeepMind Technologies
**Year**: 2017
**arXiv**: [1712.01815](https://arxiv.org/abs/1712.01815)

## Core Contribution
A single general-purpose reinforcement learning algorithm (AlphaZero) that achieves superhuman performance in Chess, Shogi, and Go without any human knowledge beyond the basic rules. Eliminates the need for supervised pretraining from human expert data.

## Key Techniques
- **No Human Data**: Trained entirely from self-play, starting from random play
- **Residual Network**: Single network outputs both policy (move probabilities) and value (win probability)
- **MCTS with Learned Policy**: Uses the neural network to guide Monte Carlo tree search
- **Self-Play Training Loop**: Agent plays against itself; MCTS generates improved policy targets; network is updated to match
- **Temperature Parameter**: Controls exploration during early self-play (high temperature = more exploration)
- **Tensor Processing Units (TPUs)**: Used 5000 TPUs for training in Chess/Shogi, 64 TPUs for Go

## Results
- **Chess**: Defeated Stockfish (previous world champion engine) after just 4 hours of self-play training
- **Shogi**: Defeated Elmo (world champion program) after 2 hours of training
- **Go**: Defeated AlphaGo Lee (the version that beat Lee Sedol) after 8 hours of training
- Learned novel strategies not seen in human play (e.g., unusual Chess openings)

## Relevance to Orbit Wars
- **Self-play from scratch** is the most relevant technique — Orbit Wars agents can be trained without any human data
- **Single network for policy + value** is an efficient architecture design for our agent
- **MCTS-guided search** can be applied to fleet deployment decisions in Orbit Wars
- **Rapid convergence** (hours, not days) suggests that with sufficient compute, strong Orbit Wars agents can be trained quickly
- **Novel strategy discovery** — AlphaZero found strategies humans never considered; our agent may discover unexpected fleet tactics
- **No domain-specific features needed** — the network learns everything from raw game state
