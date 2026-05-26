# Mastering the Game of Go with Deep Neural Networks and Tree Search

**Authors**: David Silver, Aja Huang, Chris J. Maddison, Arthur Guez, Laurent Sifre, George van den Driessche, Julian Schrittwieser, Ioannis Antonoglou, Veda Panneershelvam, Marc Lanctot, Sander Dieleman, Dominik Grewe, John Nham, Nal Kalchbrenner, Ilya Sutskever, Timothy Lillicrap, Madeleine Leach, Koray Kavukcuoglu, Thore Graepel, Demis Hassabis
**Institution**: DeepMind Technologies
**Year**: 2016
**DOI**: [Nature, 529, 484-489](https://doi.org/10.1038/nature16961)

## Core Contribution
First AI system to defeat a professional human Go player, combining deep neural networks with Monte Carlo tree search (MCTS). Introduced a new era of AI capabilities in board games previously thought to be decades away from being solved.

## Key Techniques
- **Policy Network**: Supervised learning from human expert games to predict next moves (accuracy ~57%)
- **Value Network**: Trained via self-play to predict game outcome from board positions
- **Monte Carlo Tree Search (MCTS)**: Combined with policy and value networks for look-ahead search
- **Rollout Policy**: Fast lightweight policy for quick position evaluation during search
- **Two-Stage Training**: First supervised learning from human data, then reinforcement learning via self-play
- **Residual CNN**: 13-layer convolutional network processing 19x19 board state

## Results
- Defeated European Go champion Fan Hui 5-0
- Defeated world champion Lee Sedol 4-1
- Estimated Elo rating of ~3100 (professional level is ~2900-3100)
- Reduced search tree by ~1000x compared to traditional MCTS

## Relevance to Orbit Wars
- **Self-play training** is directly applicable — Orbit Wars agents can improve by playing against themselves
- **MCTS + Neural Network** combination could be used for critical decision-making in Orbit Wars (e.g., which planet to attack)
- **Value Network** concept maps to estimating game-winning probability from current state
- **Two-stage training** (supervised pretraining + RL fine-tuning) is the recommended approach for Orbit Wars
- Demonstrates that combining search with learned policies is more powerful than either alone
