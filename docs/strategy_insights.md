# Orbit Wars Strategy Insights and Technical Route Analysis

## Mainstream Technical Routes

### 1. Heuristic / Rule-Based Methods

**Applicable Score Range**: 600 - 1200+

**Representative Notebooks**:
- Orbit War 900+ (PANNN666)
- Orbit Wars 1039.2 LB: Launch-Safety Heuristic (Aaron Toderash)
- Orbit Wars With The Barbell Strategy (Bovard)
- Orbit Wars - Aggressive Expander (Hardik Chanana)

**Core Ideas**:
- Rule-based decision making: Evaluate target value → Select optimal target → Allocate fleet
- Launch safety heuristics: Ensure fleets don't crash into the sun or go out of bounds
- Barbell strategy: Balance between conservative and aggressive play
- Aggressive expansion: Prioritize capturing neutral planets and high-production planets

**Pros**: Fast development, strong interpretability, no training required
**Cons**: Limited ceiling, difficult to handle complex situations

### 2. Reinforcement Learning Methods

**Applicable Score Range**: 1000 - 1600+

**Representative Notebooks**:
- [LB 1200+] Orbit Wars - PPO Strategy (Suneet Saini)
- Orbit Wars ES (ACCSCI)
- Sharing our RL lessons so far (Lin Myat Ko, discussion thread)

**Core Ideas**:
- PPO (Proximal Policy Optimization): Most popular policy gradient method
- ES (Evolution Strategy): Evolutionary strategy, optimizing parameters through population evolution
- State design: Encode game observations into RL states
- Action design: Model fleet launch decisions as RL actions
- Reward design: Based on score changes or planet control count

**Pros**: Can discover strategies difficult for humans to design, high ceiling
**Cons**: Long training time, requires significant computational resources, complex hyperparameter tuning

### 3. Simulation Search Methods

**Applicable Score Range**: 1000+

**Representative Notebooks**:
- Orbit Wars: Sim + Value Search Agent (Yash Mohan)

**Core Ideas**:
- Lookahead simulation: Simulate game states for several future turns
- Value search: Evaluate long-term value of each possible action
- Monte Carlo Tree Search (MCTS) style decision making

**Pros**: High decision quality, interpretable
**Cons**: High computational overhead, may time out

### 4. LLM / AI-Assisted Methods

**Representative Notebooks**:
- Just Ask Claude The Ultimate Orbit Wars Agent (SzczepanGrela)
- Day 1 Writeup - Gemini 3.5 Flash (Gemini AI)
- Day 3 Retrospective (Gemini 3.1 Pro)

**Core Ideas**:
- Use LLM (Claude/Gemini) to directly generate agent code
- AI participates in competition and shares lessons learned
- Gemini Pro analyzed mathematical limitations of coordinated strikes

**Observation**: LLM-generated agents can reach entry-level, but still have a gap from top performance

---

## Key Strategy Challenges

### 1. Orbiting Planet Movement Prediction
- Orbiting planets rotate around the sun; when launching fleets, need to predict target planet's future position
- Need to match angular velocity with fleet flight time
- `initial_planets` observation field can be used to calculate orbits

### 2. Comet Timing
- Comets spawn at turns 50, 150, 250, 350, 450
- Garrison disappears when comet leaves, need to evacuate in time
- Comets are removed before fleet launch (turn order step 1 vs step 3)
- `comets` observation field contains path information for prediction

### 3. 2P vs 4P Strategy Adaptation
- Leaderboard includes both 2-player and 4-player matches
- 2P: More focused on 1v1 confrontation
- 4P: Need to consider multi-opponent dynamics, avoid exposing too early

### 4. Fleet Size and Speed Optimization
- Fleet speed grows logarithmically with size (1.0 → 6.0)
- Large fleets reach targets faster, but concentrating too many ships carries risk
- Need to balance speed and risk

### 5. Multi-Attacker Combat Handling
- In combat, largest attacker fights second largest, difference survives
- When tied, all attacking ships are destroyed
- Third-party attackers may "profit from others' conflict"

### 6. Map Symmetry Utilization
- 4-fold mirror symmetry means each position has 3 symmetric positions
- Opponent's homeworld position can be predicted
- Resource distribution is the same at symmetric positions

---

## Known Bottlenecks and Solutions

### 600-Point Bottleneck
- **Phenomenon**: Multiple developers report agents getting stuck at around 600 points
- **Possible Causes**: Basic strategies lack handling for orbiting planets, comets, and combat optimization
- **Breakthrough Directions**: Add target evaluation, launch safety checks, fleet size optimization

### Mathematical Limitations of Coordinated Strikes
- **Source**: Analysis by Gemini 3.1 Pro
- **Conclusion**: Multi-fleet coordinated strikes on the same target have mathematical limitations
- **Reason**: Combat system mechanism where largest attacker fights second largest allows third parties to "pick up the pieces"
- **Insight**: Need to consider multi-party game in combat, not just simple concentrated attacks

### Limitations of Lookahead
- **Source**: Gemini 3.1 Pro's 4th iteration analysis
- **Conclusion**: Excessively deep lookahead search has diminishing returns and high computational cost
- **Insight**: Need to balance search depth and breadth, or use heuristic evaluation functions

---

## Recommended R&D Route

Based on community experience, the recommended R&D route:

1. **Phase 1 (Target 600+)**: Basic heuristic agent
   - Implement target evaluation and fleet allocation
   - Add launch safety checks
   - Handle orbiting planet prediction

2. **Phase 2 (Target 900+)**: Advanced heuristics
   - Optimize target selection strategy
   - Add comet handling logic
   - Fleet size optimization

3. **Phase 3 (Target 1000+)**: Advanced strategies
   - Implement multi-target coordination
   - 2P/4P strategy adaptation
   - Opponent behavior prediction

4. **Phase 4 (Target 1200+)**: RL methods
   - Design RL state and action space
   - Implement PPO or ES training
   - Use replay datasets for training

5. **Phase 5 (Target 1600+)**: Hybrid methods
   - RL + heuristic hybrid
   - Simulation search optimization
   - Ensemble multiple agents
