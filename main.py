"""
Orbit Wars Agent - Main Entry Point
Kaggle Competition Submission File

Contributors: CeaserZhao, PrismScope
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Dict, List, Any
from src.agents.heuristic_agent import HeuristicAgent, agent as heuristic_agent_func


def agent(observation: Dict[str, Any], configuration: Dict[str, Any]) -> List[List]:
    """
    Main agent function for Orbit Wars competition.
    
    This function is called by the Kaggle environment for each game turn.
    
    Args:
        observation: Game state containing:
            - player: Your player ID (0-3)
            - planets: List of planets [id, owner, x, y, radius, ships, production]
            - fleets: List of fleets [id, owner, x, y, angle, from_planet_id, ships]
            - angular_velocity: Angular velocity of inner planets
            - comet_planet_ids: List of planet IDs that are comets
            - comets: Comet data with paths
            - initial_planets: Initial planet positions for orbit prediction
        configuration: Game configuration
    
    Returns:
        List of moves, each move is [from_planet_id, direction_angle, num_ships]
    """
    return heuristic_agent_func(observation, configuration)


def get_agent() -> HeuristicAgent:
    """
    Get a new instance of the HeuristicAgent.
    
    Useful for local testing and evaluation.
    
    Returns:
        HeuristicAgent instance
    """
    return HeuristicAgent()


if __name__ == "__main__":
    print("Orbit Wars Heuristic Agent")
    print("=" * 50)
    
    test_obs = {
        "player": 0,
        "planets": [
            [0, 0, 20.0, 20.0, 2.0, 50, 3],
            [1, 1, 80.0, 80.0, 2.0, 30, 2],
            [2, -1, 50.0, 20.0, 1.5, 20, 1],
            [3, 0, 30.0, 70.0, 2.2, 40, 4],
            [4, 2, 70.0, 30.0, 1.8, 25, 2],
        ],
        "fleets": [
            [0, 1, 60.0, 60.0, 4.5, 1, 15],
        ],
        "angular_velocity": 0.03,
        "comet_planet_ids": [],
        "comets": [],
        "initial_planets": [
            [0, 0, 20.0, 20.0, 2.0, 50, 3],
            [1, 1, 80.0, 80.0, 2.0, 30, 2],
            [2, -1, 50.0, 20.0, 1.5, 20, 1],
            [3, 0, 30.0, 70.0, 2.2, 40, 4],
            [4, 2, 70.0, 30.0, 1.8, 25, 2],
        ],
    }
    
    test_config = {}
    
    agent_instance = get_agent()
    result = agent_instance.act(test_obs)
    print(f"Agent moves: {result}")
    
    direct_result = agent(test_obs, test_config)
    print(f"Direct call result: {direct_result}")
    
    print("\n" + "=" * 50)
    print("Test completed successfully!")
