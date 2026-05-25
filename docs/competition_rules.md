# Orbit Wars Competition Rules Summary

## Competition Overview

| Item | Details |
|------|---------|
| **Competition Name** | Orbit Wars |
| **Platform** | Kaggle (Featured Simulation Competition) |
| **Type** | Multi-agent Reinforcement Learning / Game AI |
| **Organizer** | Kaggle (Sponsor: Google LLC) |
| **Prize Pool** | $50,000 |
| **Participation Scale** | 7,853 registrants / 3,423 participants / 3,207 teams / 6,082 submissions |
| **Citation** | Bovard Doerschuk-Tiberi, Walter Reade, and Addison Howard. Orbit Wars. 2026. Kaggle. |
| **Tags** | Games, Artificial Intelligence, Reinforcement Learning |

## Timeline

| Date (UTC 23:59) | Event |
|-------------------|-------|
| 2026-04-16 | Competition starts |
| 2026-06-16 | Registration deadline (must accept rules before this) |
| 2026-06-16 | Team merge deadline |
| 2026-06-23 | Final submission deadline |
| 2026-06-24 ~ 07-08 | Matches continue running until leaderboard converges, after which the leaderboard is final |

## Game Rules

### Game Background
Orbit Wars revives the brutal strategic gameplay of the 2010 Planet Wars challenge with entirely new mechanics. Players need to launch massive fleets to conquer planets orbiting around the sun. This is a real-time strategy game in 1v1 or 4-player Free-For-All (FFA) format.

### Game Area
- **Space Size**: 100×100 continuous 2D space
- **Coordinate Origin**: Top-left corner (0, 0)
- **Sun Position**: Center (50, 50), radius 10. Fleets crossing the sun are destroyed
- **Symmetry**: All planets and comets are placed with 4-way mirror symmetry: (x, y), (100-x, y), (x, 100-y), (100-x, 100-y)

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
  - Angular velocity: 0.025-0.05 radians/turn (randomized per game)
- **Static Planets**: Planets far from the center do not rotate
- **Map Scale**: 20-40 planets (5-10 groups of 4 symmetric planets)
  - At least 3 groups guaranteed to be static planets
  - At least 1 group guaranteed to be orbiting planets

**Initial State:**
- Garrison: 5-99 ships (biased toward low values)
- Production: 1-5

**Home Planets:**
- **2-player game**: Players start from diagonal positions (Q1 and Q4)
- **4-player game**: Each player gets 1 planet from each of the 4 symmetric groups

### Fleet System

Each fleet is represented as: `[id, owner, x, y, angle, from_planet_id, ships]`

**Movement Rules:**
- **Speed**: Scales logarithmically with fleet size
  - 1 ship: 1.0 units/turn
  - ~500 ships: ~5 units/turn
  - ~1000 ships: Maximum 6.0 units/turn
- **Path**: Straight-line flight
- **Collision Detection**: Continuous detection (checks entire path segment, not just endpoints)
- **Removal Conditions**: Out of bounds, hits sun, hits planet (triggers combat)

**Fleet Launching:**
- Return a move list each turn: `[from_planet_id, direction_angle, num_ships]`
- Can only launch from owned planets
- Launch amount cannot exceed current planet garrison
- Fleet is spawned outside the planet radius in the given direction
- Multiple launches from same or different planets are allowed in the same turn

### Comet System

Comets are temporary celestial bodies that fly across the board on highly elliptical orbits.

| Attribute | Value |
|-----------|-------|
| Radius | 1.0 (fixed) |
| Production | 1 ship/turn |
| Initial Ships | Random (4 rolls of 1-99, take minimum; same for all 4 comets in a group) |
| Speed | Default 4.0 units/turn (configurable via `cometSpeed`) |
| Spawn Turns | 50, 150, 250, 350, 450 (4 comets each time, 1 per quadrant) |

**Key Rules:**
- Comets are removed when leaving the board, along with their garrison
- Comets are removed before fleet launch, so fleets cannot be launched from departing comets
- `comet_planet_ids` observation field identifies which planet IDs are comets
- `comets` observation field contains paths and current position index (`path_index`), which can be used for future position prediction

### Turn Execution Order

Each turn executes the following 7 steps in order:

1. **Comet Expiration**: Remove comets that have left the board (and their garrisons)
2. **Comet Spawn**: Generate new comet groups at specified turns (50, 150, 250, 350, 450)
3. **Fleet Launch**: Process all player actions, create new fleets
4. **Production**: All owned planets (including comets) generate ships
5. **Fleet Movement**: Move all fleets, check out-of-bounds/sun collision/planet collision, fleets hitting planets queue for combat
6. **Planet Rotation and Comet Movement**: Orbiting planets rotate, comets advance along paths, fleets captured by moving celestial bodies enter combat
7. **Combat Resolution**: Resolve all queued planetary combats

**Strategic Impact**: Step 1 executes before Step 3, meaning departing comets cannot be used to launch fleets.

### Combat System

When one or more fleets hit a planet:

1. **Force Merging**: All arriving fleets are grouped by owner, ship counts of the same owner are summed
2. **Combat Resolution**: The largest attacking force fights the second largest, the difference survives
3. **Tie Rule**: If two attackers tie, all attacking ships are destroyed (no survivors)
4. **Planet Control**:
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

Win/loss updates:
- Winner μ increases, loser μ decreases
- Both μ are slightly adjusted for ties

### Evaluation Process
1. Up to 5 agents can be submitted per day
2. Each submission plays matches against agents with similar skill ratings on the leaderboard
3. Newly submitted agents undergo validation matches (playing against copies of themselves)
4. Submissions that fail validation are marked as errors
5. All submitted agents continue playing matches until the competition ends
6. The leaderboard only displays the agent with the best score

## Competition-Specific Rules

| Rule | Content |
|------|---------|
| **Team Limit** | Maximum 5 people/team |
| **Daily Submission Limit** | Maximum 5 submissions/day |
| **Final Submission Selection** | Maximum 2 final submissions |
| **Data License** | Apache 2.0 |
| **Winner License** | CC-BY 4.0 (winning solution must be open source) |
| **External Data** | Allowed, but must be publicly and equally accessible |
| **AMLT** | Automated ML tools allowed |
| **Runtime Restrictions** | No external information or sending messages during episode evaluation |

### Eligibility Requirements
- Must be 18 years old (or majority age in your jurisdiction)
- Cannot be residents of Crimea, DNR, LNR, Cuba, Iran, North Korea
- Cannot be individuals or entities under US export control/sanctions
- Kaggle employees and their immediate families are not eligible to participate

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
    "player": int,                  # Your player ID (0-3)
    "planets": List[List],          # Planet list [id, owner, x, y, radius, ships, production]
    "fleets": List[List],           # Fleet list [id, owner, x, y, angle, from_planet_id, ships]
    "angular_velocity": float,      # Inner planet rotation speed (radians/turn)
    "comet_planet_ids": List[int],  # List of planet IDs that are comets
    "comets": ...,                  # Comet group data (paths, path_index)
    "initial_planets": ...,         # Initial planet positions (for orbit prediction)
}
```

## Action Format

Return a list of moves, each move being `[from_planet_id, direction_angle, num_ships]`:

| Parameter | Description |
|-----------|-------------|
| `from_planet_id` | Your planet's ID |
| `direction_angle` | Angle in radians (0 = right, π/2 = down) |
| `num_ships` | Number of ships to dispatch |

Return an empty list `[]` to take no action.

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

## Dataset

The dataset page provides 3 files, total size 16.81 kB, license Apache 2.0:

| Filename | Size | Description |
|----------|------|-------------|
| `README.md` | 8.24 kB | Complete game rules document |
| `agents.md` | — | Agent development guide (Getting Started) |
| `main.py` | — | Starter kit example code |

## Related Resources

- **Competition Homepage**: https://www.kaggle.com/competitions/orbit-wars
- **Dataset**: Includes starter kit and example code
- **Discussion Forum**: Tutorials, strategy sharing, and Q&A
- **Official Discord**: Get link from "How to Get Started" discussion thread
