# Orbit Wars - Kaggle Competition

[![Kaggle Competition](https://img.shields.io/badge/Kaggle-Competition-blue)](https://www.kaggle.com/competitions/orbit-wars)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Multi-agent reinforcement learning competition on Kaggle - Build an AI agent to conquer planets and dominate the galaxy!

## Contributors
- **CeaserZhao**
- **PrismScope**

## Competition Overview

| Attribute | Details |
|-----------|---------|
| **Competition** | Orbit Wars |
| **Type** | Multi-agent Reinforcement Learning / RTS Game AI |
| **Prize Pool** | $50,000 |
| **Deadline** | June 23, 2026 |

### Game Summary
Orbit Wars is a novel multi-agent real-time strategy game where players control fleets to conquer planets in a 100x100 continuous space. Planets orbit around the sun and produce ships over time. The goal is to maximize your total ship count by controlling planets and defeating opponents.

## Project Structure

```
.
├── data/                   # Dataset and game data
│   ├── raw/               # Raw data
│   ├── processed/         # Processed data
│   └── episodes/          # Game episodes
├── notebooks/              # Jupyter notebooks
│   ├── exploration/       # Data exploration
│   ├── analysis/          # Analysis notebooks
│   └── experiments/       # Experiment tracking
├── src/                    # Source code
│   ├── agents/            # Agent implementations
│   ├── models/            # Model definitions
│   ├── training/          # Training scripts
│   ├── evaluation/        # Evaluation tools
│   └── utils/             # Utility functions
├── references/             # References
│   ├── papers/            # Research papers
│   ├── tutorials/         # Tutorials
│   └── notes/             # Notes
├── records/                # Development records
│   ├── daily/             # Daily logs
│   ├── milestones/        # Milestones
│   └── decisions/         # Decision records
├── submissions/            # Submission files
│   ├── archive/           # Archived submissions
│   └── current/           # Current submission
├── tests/                  # Unit tests
├── docs/                   # Documentation
│   ├── competition_rules.md
│   └── api_reference.md
├── main.py                 # Main entry point
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd orbit-wars

# Install dependencies
pip install -r requirements.txt
```

### Running the Agent

```bash
# Test the agent locally
python main.py

# Run with Kaggle environment
python -c "from kaggle_environments import make; env = make('orbit-wars'); env.run(['main.py', 'main.py']); env.render()"
```

## Game Rules (Summary)

### Space
- **Size**: 100×100 continuous 2D space
- **Sun**: Center at (50, 50) with radius 10
- **Symmetry**: 4-way mirror symmetry

### Planets
- Each planet: `[id, owner, x, y, radius, ships, production]`
- **Production**: 1-5 ships per turn
- **Radius**: `1 + ln(production)`
- **Orbiting planets**: Rotate around sun with angular velocity 0.025-0.05

### Fleets
- Speed scales logarithmically with fleet size (1.0 to 6.0)
- Removed when: out of bounds, hit sun, or hit planet

### Combat
- When fleets hit a planet, largest attacker fights second largest
- Winner captures or reinforces the planet

### Victory Conditions
- **Score**: Total ships on owned planets + ships in fleets
- **Win**: Highest score after 500 turns or last player standing

## Documentation

- [Competition Rules](docs/competition_rules.md) - Detailed competition rules
- [API Reference](docs/api_reference.md) - API documentation and utilities

## Timeline

| Date | Event |
|------|-------|
| Apr 16, 2026 | Competition starts |
| Jun 16, 2026 | Entry deadline |
| Jun 23, 2026 | Final submission deadline |
| Jun 24 - Jul 8, 2026 | Matches continue until leaderboard converges |

## Resources

- [Kaggle Competition Page](https://www.kaggle.com/competitions/orbit-wars)
- [Kaggle Environments](https://github.com/Kaggle/kaggle-environments)

## Development

### Adding a New Agent

1. Create a new file in `src/agents/`
2. Inherit from `BaseAgent` in `src/agents/base_agent.py`
3. Implement the `act` method
4. Update `main.py` to use your agent

### Testing

```bash
# Run tests
pytest tests/

# Run specific test
pytest tests/test_agent.py
```

## License

See [LICENSE](LICENSE) file for details.

## Acknowledgments

- Kaggle for hosting the competition
- All contributors and collaborators
