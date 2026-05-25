# Orbit Wars Competition Rules Summary

## Competition Overview

| Item | Details |
|------|---------|
| **Competition Name** | Orbit Wars |
| **Platform** | Kaggle |
| **Type** | Multi-agent Reinforcement Learning / Game AI |
| **Prize Pool** | $50,000 |
| **Participation Scale** | 7,851 registrants / 3,422 participants / 3,206 teams / 6,081 submissions |

## Timeline

| Date (UTC) | Event |
|------------|-------|
| 2026-04-16 | Competition starts |
| 2026-06-16 23:59 | Registration deadline (must accept rules before this) |
| 2026-06-16 23:59 | Team merge deadline |
| 2026-06-23 23:59 | Final submission deadline |
| 2026-06-24 ~ 07-08 | Matches continue running until leaderboard converges |

## Game Rules

### Game Background
Orbit Wars recreates the strategic gameplay of the 2010 Planet Wars challenge with new mechanics added. Players command fleets to conquer planets orbiting around the sun.

### Game Area
- **Space Size**: 100×100 continuous 2D space
- **Coordinate Origin**: Top-left corner (0, 0)
- **Sun Position**: Center (50, 50), radius 10
- **Symmetry**: 4-way mirror symmetry - (x, y), (100-x, y), (x, 100-y), (100-x, 100-y)

### Planet System

Each planet is represented as: `[id, owner, x, y, radius, ships, production]`

| Attribute | Description |
|-----------|-------------|
| `id` | Unique planet identifier |
| `owner` | Owner player ID (0-3) or -1 (neutral) |
| `x, y` | Planet center coordinates |
| `radius` | Planet radius = 1 + ln(production) |
| `ships` | Current garrison size |
| `production` | Production level (1-5), generates that many ships per turn |

**Planet Types:**
- **Orbiting Planets**: Planets with orbit radius + planet radius < 50 orbit around the sun
  - Angular velocity: 0.025-0.05 radians/turn
- **Static Planets**: Planets far from the center do not rotate
- **Map Scale**: 20-40 planets (5-10 groups of 4 symmetric planets)

**Initial State:**
- Garrison: 5-99 ships
- Production: 1-5

### Fleet System

Each fleet is represented as: `[id, owner, x, y, angle, from_planet_id, ships]`

**Movement Rules:**
- **Speed**: Scales logarithmically with fleet size
  - 1 ship: 1.0 units/turn
  - ~500 ships: ~5 units/turn
  - ~1000 ships: Maximum 6.0 units/turn
- **Path**: Straight-line flight
- **Collision Detection**: Continuous detection (checks entire path segment)
- **Removal Conditions**: Out of bounds, hits sun, or hits planet

### Comet System

- **Spawn Turns**: 50, 150, 250, 350, 450
- **Radius**: 1.0
- **Production**: 1 ship/turn
- **Speed**: 4.0 units/turn
- **Removal**: When leaving the game board

### Combat System

Combat is triggered when a fleet hits a planet:

1. **Force Merging**: All arriving fleets are grouped by owner, ship counts of the same owner are summed
2. **Combat Resolution**: The largest attacking force fights the second largest, the difference survives
3. **Planet Control**:
   - If the surviving attacker shares the same owner as the planet → reinforces the garrison
   - If different owners → fights the garrison, captures the planet if exceeding the garrison

## Evaluation Metrics

### Scoring System
- **Final Score** = Total ships on owned planets + Total ships in owned fleets

### Game End Conditions
1. Reaching the 500-turn limit
2. Only one player (or zero) has planets or fleets remaining

### Victory Conditions
- The player with the highest score wins
- Or the last surviving player wins

### Skill Rating System
Each submitted agent is modeled using a **Gaussian distribution N(μ, σ²)**:
- μ: Estimated skill value
- σ: Estimated uncertainty (decreases over time)

### Evaluation Process
1. Up to 5 agents can be submitted per day
2. Each submission plays matches against agents with similar skill ratings on the leaderboard
3. Newly submitted agents undergo validation matches (playing against copies of themselves)
4. All submitted agents continue playing matches until the competition ends
5. The leaderboard only displays the agent with the best score

## Submission Requirements

### Code Structure
- Must have a `main.py` file in the root directory
- Must contain an `agent` function

### Submission Methods
1. **Single-file Agent**: Submit main.py directly
2. **Multi-file Agent**: Package as tar.gz with main.py in the root directory
3. **Notebook Submission**: Submit via Kaggle Notebook

### Local Testing
```bash
pip install kaggle-environments>=1.28.0
```

## Observation Space

The observation received by the agent contains the following fields:

```python
{
    "player": int,              # Your player ID (0-3)
    "planets": List[List],      # Planet list [id, owner, x, y, radius, ships, production]
    "fleets": List[List],       # Fleet list [id, owner, x, y, angle, from_planet_id, ships]
    "angular_velocity": float   # Inner planet rotation speed (radians/turn)
}
```

## Action Format

Return a list of moves, each move being `[from_planet_id, direction_angle, num_ships]`:

| Parameter | Description |
|-----------|-------------|
| `from_planet_id` | Your planet's ID |
| `direction_angle` | Angle in radians (0 = right, π/2 = down) |
| `num_ships` | Number of ships to dispatch |

## Prize Distribution

| Rank | Prize |
|------|-------|
| 1st Place | $5,000 |
| 2nd Place | $5,000 |
| 3rd Place | $5,000 |
| 4th Place | $5,000 |
| 5th Place | $5,000 |
| 6th Place | $5,000 |
| 7th Place | $5,000 |
| 8th Place | $5,000 |
| 9th Place | $5,000 |
| 10th Place | $5,000 |

**Total**: $50,000

## Related Resources

- **Competition Homepage**: https://www.kaggle.com/competitions/orbit-wars
- **Dataset**: Includes starter kit and example code
- **Discussion Forum**: Tutorials, strategy sharing, and Q&A

## Community Contributions

- "Orbit Wars - Reinforcement Learning Tutorial" - Reinforcement learning tutorial
- "Orbit Wars 2026 - Starter" - Multiple starter code examples
- "Orbit Wars: Structured Baseline" - Structured baseline code
- "Orbit Wars Daily Episode Datasets" - Daily match datasets
