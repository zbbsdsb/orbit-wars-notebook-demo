"""
Orbit Wars Agent - Main Entry Point
Kaggle Competition Submission File

Contributors: CeaserZhao, PrismScope
"""

import random
import math
from typing import Dict, List, Any, Tuple


def agent(observation: Dict[str, Any], configuration: Dict[str, Any]) -> List[List[float]]:
    """
    Main agent function for Orbit Wars competition.
    
    Args:
        observation: Game state containing:
            - player: Your player ID (0-3)
            - planets: List of planets [id, owner, x, y, radius, ships, production]
            - fleets: List of fleets [id, owner, x, y, angle, from_planet_id, ships]
            - angular_velocity: Angular velocity of inner planets
        configuration: Game configuration
    
    Returns:
        List of moves, each move is [from_planet_id, direction_angle, num_ships]
    """
    player_id = observation["player"]
    planets = observation["planets"]
    fleets = observation.get("fleets", [])
    
    # Get my planets
    my_planets = [p for p in planets if p[1] == player_id]
    
    # Get enemy and neutral planets
    enemy_planets = [p for p in planets if p[1] != player_id and p[1] != -1]
    neutral_planets = [p for p in planets if p[1] == -1]
    
    moves = []
    
    # Simple strategy: Attack nearest enemy or neutral planet
    for my_planet in my_planets:
        planet_id = my_planet[0]
        x, y = my_planet[2], my_planet[3]
        ships = my_planet[5]
        
        # Find target (prioritize enemy, then neutral)
        target = None
        min_dist = float('inf')
        
        # Check enemy planets
        for enemy in enemy_planets:
            dist = math.sqrt((enemy[2] - x) ** 2 + (enemy[3] - y) ** 2)
            if dist < min_dist:
                min_dist = dist
                target = enemy
        
        # Check neutral planets if no enemy found
        if target is None:
            for neutral in neutral_planets:
                dist = math.sqrt((neutral[2] - x) ** 2 + (neutral[3] - y) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    target = neutral
        
        # Send ships if we have enough and found a target
        if target and ships > 10:
            target_x, target_y = target[2], target[3]
            dx = target_x - x
            dy = target_y - y
            angle = math.atan2(dy, dx)
            
            # Send half of the ships
            num_ships = ships // 2
            moves.append([planet_id, angle, num_ships])
    
    return moves


# For local testing
if __name__ == "__main__":
    # Test observation
    test_obs = {
        "player": 0,
        "planets": [
            [0, 0, 20.0, 20.0, 2.0, 50, 3],   # My planet
            [1, 1, 80.0, 80.0, 2.0, 30, 2],   # Enemy planet
            [2, -1, 50.0, 20.0, 1.5, 20, 1],  # Neutral planet
        ],
        "fleets": [],
        "angular_velocity": 0.03
    }
    
    test_config = {}
    
    result = agent(test_obs, test_config)
    print("Agent moves:", result)
