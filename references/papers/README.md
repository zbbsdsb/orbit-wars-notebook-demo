# Reference Papers

A curated collection of research papers relevant to the Orbit Wars Kaggle competition, covering deep reinforcement learning, multi-agent systems, game AI, and world models.

## Quick Reference

| Paper | Year | Algorithm | Relevance | File |
|-------|------|-----------|-----------|------|
| Playing Atari with Deep RL | 2013 | DQN | Foundational | [dqn_2013.md](dqn_2013.md) |
| Mastering the Game of Go | 2016 | AlphaGo | Self-play + Search | [alphago_2016.md](alphago_2016.md) |
| Mastering Chess, Shogi, Go | 2017 | AlphaZero | Self-play from scratch | [alphazero_2017.md](alphazero_2017.md) |
| Multi-Agent Actor-Critic | 2017 | MADDPG | Multi-agent CTDE | [maddpg_2017.md](maddpg_2017.md) |
| StarCraft II: A New Challenge | 2017 | SC2LE | RTS game environment | [sc2le_2017.md](sc2le_2017.md) |
| Proximal Policy Optimization | 2017 | PPO | **Primary algorithm** | [ppo_2017.md](ppo_2017.md) |
| Soft Actor-Critic | 2018 | SAC | Alternative to PPO | [sac_2018.md](sac_2018.md) |
| QMIX | 2018 | QMIX | Cooperative MARL | [qmix_2018.md](qmix_2018.md) |
| Dota 2 with Large Scale Deep RL | 2019 | OpenAI Five | Scaled PPO | [openai_five_2019.md](openai_five_2019.md) |
| AlphaStar | 2019 | AlphaStar | **Most relevant** | [alphastar_2019.md](alphastar_2019.md) |
| Dream to Control | 2020 | Dreamer | World models | [dreamer_2020.md](dreamer_2020.md) |
| Mastering Atari, Go, Chess, Shogi | 2020 | MuZero | Learned model + Search | [muzero_2020.md](muzero_2020.md) |

## Priority for Orbit Wars

### Must Read (Directly Applicable)
1. **PPO** — Our primary RL algorithm
2. **AlphaStar** — Most relevant game AI reference (RTS, multi-agent, entity attention)
3. **OpenAI Five** — Scaled PPO for real-time strategy games
4. **AlphaZero** — Self-play training methodology

### Recommended (Techniques to Adopt)
5. **SC2LE** — Structured action space design
6. **AlphaGo** — MCTS + neural network combination
7. **SAC** — Alternative if using continuous action outputs
8. **MADDPG** — Centralized training with decentralized execution

### Advanced (Phase 4+ Optimizations)
9. **Dreamer** — World models for sample efficiency
10. **MuZero** — Learned environment model + planning
11. **QMIX** — Value decomposition for multi-planet coordination
12. **DQN** — Foundational concepts (experience replay, target networks)

## Key Techniques Summary

| Technique | Source Paper | Application in Orbit Wars |
|-----------|-------------|--------------------------|
| Experience Replay | DQN | Stabilize RL training |
| Target Network | DQN | Prevent value oscillation |
| Self-Play | AlphaGo/Zero | Train against own past versions |
| MCTS + NN | AlphaGo | Plan critical fleet deployments |
| Clipped Objective | PPO | Prevent destructive policy updates |
| GAE | PPO | Reduce variance in advantage estimation |
| League Training | AlphaStar | Prevent overfitting to specific opponents |
| Imitation Learning | AlphaStar | Pretrain on Top-10% replays |
| Entity Attention | AlphaStar | Model planet-fleet relationships |
| CTDE | MADDPG | Use full state in training, local obs in execution |
| Maximum Entropy | SAC | Encourage exploration |
| World Model | Dreamer | Predict game dynamics for planning |
| Learned Dynamics | MuZero | Learn environment model from observations |
| Value Factorization | QMIX | Coordinate multiple planets |

## arXiv Links

- [DQN (1312.5602)](https://arxiv.org/abs/1312.5602)
- [AlphaZero (1712.01815)](https://arxiv.org/abs/1712.01815)
- [MADDPG (1706.02275)](https://arxiv.org/abs/1706.02275)
- [SC2LE (1708.04782)](https://arxiv.org/abs/1708.04782)
- [PPO (1707.06347)](https://arxiv.org/abs/1707.06347)
- [SAC (1801.01290)](https://arxiv.org/abs/1801.01290)
- [QMIX (1803.11485)](https://arxiv.org/abs/1803.11485)
- [AlphaStar (1911.02289)](https://arxiv.org/abs/1911.02289)
- [Dreamer (1912.01603)](https://arxiv.org/abs/1912.01603)
- [MuZero (1911.08265)](https://arxiv.org/abs/1911.08265)
- [AlphaGo (Nature DOI)](https://doi.org/10.1038/nature16961)
- [OpenAI Five (Blog)](https://openai.com/index/openai-five-defeats-dota-2-champions/)
