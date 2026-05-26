# Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model

**Authors**: Julian Schrittwieser, Ioannis Antonoglou, Thomas Hubert, Karen Simonyan, Laurent Sifre, Simon Schmitt, Arthur Guez, Edward Lockhart, Vladimir Lobanov, Steven Hansen, Timothy Lillicrap, Matthew Lai, Adrià Puigdomènech, Maximilian Ershevsky, Timo Ewalds, Will Dabney, Remi Munos, David Silver
**Institution**: DeepMind Technologies
**Year**: 2020
**arXiv**: [1911.08265](https://arxiv.org/abs/1911.08265)

## Core Contribution
A reinforcement learning algorithm (MuZero) that achieves superhuman performance in Atari, Go, Chess, and Shogi without knowing the rules of the game. MuZero learns a model of the environment dynamics, value function, and policy directly from experience, then uses MCTS with the learned model for planning.

## Key Techniques
- **Learned Dynamics Model**: Unlike AlphaZero (which requires known game rules), MuZero learns to predict:
  - **Reward function**: r(s, a) — predicts immediate reward
  - **Value function**: v(s) — predicts expected future return
  - **Policy**: p(s) — predicts best action distribution
  - **Next state representation**: s' = f(s, a) — predicts next state in latent space
- **MCTS with Learned Model**: Uses Monte Carlo tree search in the learned latent space, not the actual game state
- **Representation Function**: Encodes raw observations into a hidden state used by the dynamics model
- **Prediction Network**: Given a hidden state, outputs policy and value predictions
- **Dynamics Network**: Given a hidden state and action, outputs reward and next hidden state
- **Reanalyze**: Periodically replays past experiences with updated (stronger) MCTS to improve the policy targets

## Architecture
```
Observation o_t
    ↓ [Representation Network]
Hidden state s_0
    ↓ [Prediction Network]
Policy p(s_0), Value v(s_0)

MCTS Planning:
s_0 --(a_1)--> s_1 --(a_2)--> s_2 --(a_3)--> ...
         ↓           ↓           ↓
       r_1         r_2         r_3
    [Dynamics Network at each step]
```

## Results
- **Atari**: Matched AlphaZero performance on 57 games without knowing game rules
- **Go**: Matched AlphaZero performance
- **Chess**: Matched AlphaZero performance
- **Shogi**: Matched AlphaZero performance
- First algorithm to achieve superhuman performance across multiple game domains without knowledge of game rules
- More sample-efficient than AlphaZero (especially on Atari)

## Relevance to Orbit Wars
- **No need to implement game rules** — MuZero learns environment dynamics from observations alone
- **Planning in latent space** — MCTS can be used to plan fleet deployments without simulating the full game
- **Reanalysis** — past game experiences can be re-evaluated with stronger policies, improving sample efficiency
- **Representation learning** — learning compact state representations is valuable for Orbit Wars' complex observations
- **Most ambitious approach** — implementing MuZero is significantly more complex than PPO, but could yield superior results
- **Practical consideration**: MuZero requires substantial compute and engineering effort; recommended as a Phase 4 optimization after establishing a strong PPO baseline
- **Hybrid potential**: Use MuZero's learned model component to improve orbital planet prediction and battle outcome estimation
