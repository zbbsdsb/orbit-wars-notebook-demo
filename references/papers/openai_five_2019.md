# Dota 2 with Large Scale Deep Reinforcement Learning

**Authors**: OpenAI (Christopher Berner, Greg Brockman, Brooke Chan, Vicki Cheung, Przemysław Debiak, Christy Dennison, David Farhi, Quirin Fischer, Shariq Hashme, Chris Hesse, Rafal Józefowicz, Scott Gray, Catherine Olsson, Jared Pachocki, Michael Petrov, Henrique Ponde de Oliveira Pinto, Jonathan Raiman, Tim Salimans, Jeremy Schlatter, Jonas Schneider, Szymon Sidor, Ilya Sutskever, Jie Tang, Filip Wolski, Susan Zhang)
**Institution**: OpenAI
**Year**: 2019
**URL**: [OpenAI Blog](https://openai.com/index/openai-five-defeats-dota-2-champions/)

## Core Contribution
Demonstrated that large-scale reinforcement learning with PPO can achieve superhuman performance in Dota 2, a complex real-time strategy game with imperfect information, long time horizons, and large action spaces. OpenAI Five defeated the world champion Dota 2 team OG in a best-of-three exhibition match.

## Key Techniques
- **Scaled PPO**: Applied PPO at unprecedented scale with massive distributed training
- **Self-Play**: Agent trained entirely through self-play starting from random initialization
- **Long Time Horizon**: Games last ~45 minutes (~80,000 time steps), requiring credit assignment over long horizons
- **Large Action Space**: ~20,000 possible actions per timestep (unit selection + ability targeting)
- **Distributed Training**: Used 256 GPUs and 128,000 CPU cores for training
- **LSTM Policy**: Recurrent policy network to handle partial observability
- **Curriculum**: Started with simplified game (1 hero, no items) and progressively added complexity

## Results
- Defeated OG (Dota 2 world champions) in a best-of-three exhibition match (2-0)
- Achieved 99.4% win rate against high-level human players in restricted hero pool
- Demonstrated emergent behaviors: lane positioning, last-hitting, team fighting, Roshan timing
- Training required ~800 years of real-time Dota 2 experience (compressed via distributed training)

## Relevance to Orbit Wars
- **PPO at scale** validates PPO as the primary algorithm choice for Orbit Wars
- **Self-play training** is directly applicable — Orbit Wars agents can train against themselves
- **Long time horizon handling** (500 turns in Orbit Wars) requires similar techniques to Dota 2
- **LSTM for partial observability** — Orbit Wars agents may benefit from recurrent policies to track opponent fleet movements
- **Curriculum approach** — start with simplified scenarios, gradually add complexity
- **Emergent strategies** — expect our agent to discover non-obvious fleet tactics through self-play
- **Compute requirements** — OpenAI Five used massive compute; we need to be efficient with Kaggle GPU resources
