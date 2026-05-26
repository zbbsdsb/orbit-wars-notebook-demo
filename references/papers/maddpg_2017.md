# Multi-Agent Actor-Critic for Mixed Cooperative-Competitive Environments

**Authors**: Ryan Lowe, Yi Wu, Aviv Tamar, Jean Harb, Pieter Abbeel, Igor Mordatch
**Institution**: UC Berkeley, OpenAI
**Year**: 2017
**arXiv**: [1706.02275](https://arxiv.org/abs/1706.02275)

## Core Contribution
An off-policy actor-critic algorithm (MADDPG) for multi-agent reinforcement learning that extends DDPG to multi-agent settings using centralized training with decentralized execution (CTDE). Handles both cooperative and competitive interactions.

## Key Techniques
- **Centralized Training, Decentralized Execution (CTDE)**: During training, each agent has access to all agents' observations and actions; during execution, each agent only uses its own observations
- **Critic Network**: Each agent's critic receives the observations and actions of all agents as input, enabling it to learn about the effects of other agents' behaviors
- **Actor Network**: Each agent's actor only receives its own local observation, ensuring decentralized execution
- **DDPG Extension**: Uses the deterministic policy gradient algorithm (DDPG) as the base for each agent
- **Experience Replay**: Each agent maintains its own replay buffer; during training, samples are drawn from all buffers
- **Soft Target Updates**: Target networks are updated via Polyak averaging (τ=0.01)

## Results
- Outperformed independent DDPG, DQN, and other multi-agent baselines on cooperative, competitive, and mixed tasks
- Solved the cooperative navigation task, the physical deception task, and the keep-away task
- Demonstrated that centralized critics significantly improve learning in multi-agent settings

## Relevance to Orbit Wars
- **CTDE paradigm** is directly applicable — in Orbit Wars, each player only sees their own observation during execution, but during training we can simulate full game state
- **Multi-agent critic** can help our agent learn to account for opponent behaviors
- **Mixed cooperative-competitive** setting matches Orbit Wars (4P FFA has both competitive and temporary cooperative dynamics)
- **Experience replay from multiple agents** is useful for training against diverse opponents
- Less directly applicable than PPO for Orbit Wars (since Orbit Wars uses discrete actions, not continuous), but CTDE principle is valuable
