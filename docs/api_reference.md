# Orbit Wars API Reference

## Observation Space

The observation received by the agent each turn is a dictionary containing the following keys:

### player
- **Type**: `int`
- **Range**: 0-3
- **Description**: Current agent's player ID

### planets
- **Type**: `List[List[Union[int, float]]]`
- **Format**: `[id, owner, x, y, radius, ships, production]`
- **Description**: List of all planet states

| Index | Name | Type | Description |
|-------|------|------|-------------|
| 0 | id | int | Unique planet identifier |
| 1 | owner | int | Owner ID (-1=neutral, 0-3=player) |
| 2 | x | float | X coordinate (0-100) |
| 3 | y | float | Y coordinate (0-100) |
| 4 | radius | float | Planet radius |
| 5 | ships | int | Current garrison size |
| 6 | production | int | Production level (1-5) |

### fleets
- **Type**: `List[List[Union[int, float]]]`
- **Format**: `[id, owner, x, y, angle, from_planet_id, ships]`
- **Description**: List of all fleet states

| Index | Name | Type | Description |
|-------|------|------|-------------|
| 0 | id | int | Unique fleet identifier |
| 1 | owner | int | Owner ID (0-3) |
| 2 | x | float | X coordinate |
| 3 | y | float | Y coordinate |
| 4 | angle | float | Flight direction (radians) |
| 5 | from_planet_id | int | Origin planet ID |
| 6 | ships | int | Fleet ship count |

### angular_velocity
- **Type**: `float`
- **Range**: 0.025-0.05
- **Description**: Rotation angular velocity of inner planets (orbiting planets) in radians/turn

### comet_planet_ids
- **Type**: `List[int]`
- **Description**: List of planet IDs that are comets. Use this to distinguish comets from regular planets in the `planets` list.

### comets
- **Type**: `dict` (structured data)
- **Description**: Comet group data containing:
  - `paths`: List of paths for each comet group. Each path is a list of (x, y) coordinates the comet will follow.
  - `path_index`: Current position index along the path for each comet group.
- **Usage**: Can be used to predict future comet positions by looking ahead in the paths array.

### initial_planets
- **Type**: `List[List]`
- **Description**: Initial planet positions at the start of the game. Useful for predicting orbital planet positions by calculating the orbit from the initial position.

## Action Space

The action returned by the agent is a list, where each element is a move command:

### Move Format
```python
[from_planet_id, direction_angle, num_ships]
```

| Parameter | Type | Range/Description |
|-----------|------|-------------------|
| from_planet_id | int | ID of the departure planet (must be a planet you own) |
| direction_angle | float | Launch direction in radians (0 = right, π/2 = down) |
| num_ships | int | Number of ships to dispatch (must ≤ current garrison) |

### Examples
```python
# Launch 10 ships from planet 0 to the right
[0, 0.0, 10]

# Launch 20 ships from planet 1 to the lower-left (approximately 225 degrees)
[1, 3.92699, 20]

# Multiple moves
[[0, 0.0, 10], [1, 1.57, 15], [2, 3.14, 20]]
```

## Game Constants

### Space Boundaries
- **Width**: 100
- **Height**: 100
- **Sun Position**: (50, 50)
- **Sun Radius**: 10

### Fleet Speed
- **Minimum Speed**: 1.0 (1 ship)
- **Maximum Speed**: 6.0 (approximately 1000 ships)
- **Speed Formula**: `speed = min(6.0, 1.0 + log(ships))`

### Planet Attributes
- **Production Range**: 1-5
- **Radius Formula**: `radius = 1.0 + ln(production)`
- **Initial Garrison Range**: 5-99

### Game Parameters
- **Maximum Turns**: 500
- **Comet Spawn Turns**: 50, 150, 250, 350, 450
- **Comet Speed**: 4.0
- **Comet Radius**: 1.0

## Angle Reference

| Angle (Radians) | Angle (Degrees) | Direction |
|-----------------|-----------------|-----------|
| 0 | 0° | Right → |
| π/4 | 45° | Lower-right ↘ |
| π/2 | 90° | Down ↓ |
| 3π/4 | 135° | Lower-left ↙ |
| π | 180° | Left ← |
| 5π/4 | 225° | Upper-left ↖ |
| 3π/2 | 270° | Up ↑ |
| 7π/4 | 315° | Upper-right ↗ |

### Common Angle Calculations
```python
import math

# Calculate angle from (x1, y1) to (x2, y2)
dx = x2 - x1
dy = y2 - y1
angle = math.atan2(dy, dx)  # Result range: [-π, π]

# Ensure angle is in [0, 2π] range
if angle < 0:
    angle += 2 * math.pi
```

## Utility Functions

### Distance Calculation
```python
import math

def distance(p1, p2):
    """Calculate the distance between two points"""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def planet_distance(planet1, planet2):
    """Calculate the distance between two planets"""
    return math.sqrt((planet1[2] - planet2[2])**2 + (planet1[3] - planet2[3])**2)
```

### Angle Calculation
```python
import math

def angle_between(from_pos, to_pos):
    """Calculate the angle from from_pos to to_pos"""
    dx = to_pos[0] - from_pos[0]
    dy = to_pos[1] - from_pos[1]
    return math.atan2(dy, dx)

def normalize_angle(angle):
    """Normalize angle to [0, 2π] range"""
    while angle < 0:
        angle += 2 * math.pi
    while angle >= 2 * math.pi:
        angle -= 2 * math.pi
    return angle
```

### Fleet Arrival Time Estimation
```python
import math

def fleet_speed(num_ships):
    """Calculate fleet speed"""
    return min(6.0, 1.0 + math.log(max(1, num_ships)))

def estimated_arrival_time(distance, num_ships):
    """Estimate fleet arrival time"""
    speed = fleet_speed(num_ships)
    return distance / speed
```

## Agent Interface

### Basic Template
```python
def agent(observation, configuration):
    """
    Main agent function.

    Args:
        observation: Game state
        configuration: Game configuration

    Returns:
        List of moves
    """
    player = observation["player"]
    planets = observation["planets"]
    fleets = observation.get("fleets", [])
    angular_velocity = observation.get("angular_velocity", 0.03)

    # Your strategy here
    moves = []

    return moves
```

## Configuration Parameters

The `configuration` dictionary passed to the agent function may contain:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cometSpeed` | float | 4.0 | Speed of comets (units/turn) |
| `episodeSteps` | int | 500 | Maximum number of turns per episode |
| `agentTimeout` | int | — | Time limit for agent execution (seconds) |

## Kaggle CLI Commands

### Submit an Agent
```bash
kaggle competitions submit -c orbit-wars -f main.py -m "Submission description"
```

### List Submissions
```bash
kaggle competitions submissions -c orbit-wars
```

### View Episode Details
```bash
kaggle competitions episodes -c orbit-wars -s <submission-id>
```

### Download Leaderboard
```bash
kaggle competitions leaderboard -c orbit-wars
```

### Download Competition Data
```bash
kaggle competitions download -c orbit-wars
```

## Environment Setup

```bash
pip install kaggle-environments>=1.28.0
```

### Local Testing
```python
from kaggle_environments import make

# Create environment
env = make("orbit-wars", debug=True)

# Run a match
result = env.run([agent1, agent2])

# View results
print(result)
```
