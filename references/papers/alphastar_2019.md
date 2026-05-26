# AlphaStar: Mastering the Real-Time Strategy Game StarCraft II

**Authors**: Oriol Vinyals, Timo Ewalds, Sergey Bartunov, Petko Georgiev, Alexander Vezhnevets, Michelle Yeo, Alireza Makhzani, Heinrich Küttler, John Agapiw, Julian Schrittwieser, Jon Close, Alex Budden, Erich Elsen, Sylvain Gelly, Stephan Gouws, Thomas Hubert, Filip Karczewski, James Molloy, Tom Schaul, Daniel Visentin, Georg Ostrovski, Stig Petersen, Faustino Gomez, Tim Hertel, David Silver
**Institution**: DeepMind Technologies
**Year**: 2019
**arXiv**: [1911.02289](https://arxiv.org/abs/1911.02289)

## Core Contribution
First AI system to achieve Grandmaster level in StarCraft II, defeating 99.8% of active human players. Introduced several key innovations including league training, multi-agent reinforcement learning, and a deep neural network architecture specifically designed for real-time strategy games.

## Key Techniques

### Architecture
- **Transformer torso**: Processes entity (unit/building) features using attention mechanisms, enabling relational reasoning between game entities
- **Auto-regressive policy head**: Predicts actions sequentially (function ID → delay → arguments)
- **LSTM core**: Maintains hidden state across time steps for temporal reasoning
- **Up-center crop**: Spatial input processing that focuses on the screen area around the camera

### Training Methods
- **Imitation Learning**: Pretrained on 971,000 human replays using behavioral cloning + supervised learning
- **RL Fine-tuning**: PPO with V-trace off-policy correction
- **League Training**: Trains against a diverse pool of agents including:
  - **Main Agents**: Trained against all league members
  - **League Exploiters**: Trained specifically to defeat main agents (exploitation)
  - **Main Exploiters**: Trained specifically to defeat league exploiters (anti-exploitation)
- **Multi-Agent Learning**: Handles 1v1, 2v2, and FFA game modes
- **V-trace**: Off-policy correction for stable PPO training with self-play data

### Key Innovations
- **Entity-level attention**: Models relationships between individual units rather than processing spatial maps
- **Dynamic sampling**: Prioritizes training against agents that the main agent performs worst against
- **Strategy diversity**: League training ensures the agent doesn't overfit to a single strategy

## Results
- Achieved Grandmaster level on all three StarCraft II races (Terran, Protoss, Zerg)
- Defeated professional players TLO and MaNa in live matches
- Win rate >99.8% against human players on Battle.net
- Demonstrated qualitatively different strategies from human play

## Relevance to Orbit Wars
- **Most directly relevant paper** — StarCraft II and Orbit Wars share many characteristics:
  - Real-time strategy with resource management
  - Unit (fleet) production and deployment
  - Spatial reasoning on a 2D map
  - Multi-agent competition (1v1 and FFA modes)
- **Entity-level attention** can be applied to model relationships between planets and fleets in Orbit Wars
- **League Training** is critical for Orbit Wars — prevents overfitting to specific opponent strategies
- **Imitation Learning pretraining** — use Top-10% Orbit Wars replays for initial policy
- **PPO + V-trace** is the recommended training algorithm
- **Strategy diversity** — league training ensures our agent can handle various play styles
- **Auto-regressive action head** maps well to Orbit Wars' structured action space (source planet → target → fleet size)
