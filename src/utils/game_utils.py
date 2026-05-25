"""
Game utility functions for Orbit Wars.

Contributors: CeaserZhao, PrismScope
"""

import math
from typing import List, Dict, Any, Tuple, Optional


# Game constants
GAME_WIDTH = 100
GAME_HEIGHT = 100
SUN_POSITION = (50, 50)
SUN_RADIUS = 10
MAX_TURNS = 500
MAX_FLEET_SPEED = 6.0
MIN_FLEET_SPEED = 1.0


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculate Euclidean distance between two points.
    
    Args:
        x1, y1: First point coordinates
        x2, y2: Second point coordinates
    
    Returns:
        Euclidean distance
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def planet_distance(planet1: List, planet2: List) -> float:
    """
    Calculate distance between two planets.
    
    Args:
        planet1: Planet data [id, owner, x, y, ...]
        planet2: Planet data [id, owner, x, y, ...]
    
    Returns:
        Distance between planet centers
    """
    return distance(planet1[2], planet1[3], planet2[2], planet2[3])


def angle_between(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculate angle from point 1 to point 2.
    
    Args:
        x1, y1: Starting point
        x2, y2: Target point
    
    Returns:
        Angle in radians [-π, π]
    """
    return math.atan2(y2 - y1, x2 - x1)


def normalize_angle(angle: float) -> float:
    """
    Normalize angle to [0, 2π] range.
    
    Args:
        angle: Angle in radians
    
    Returns:
        Normalized angle in [0, 2π]
    """
    while angle < 0:
        angle += 2 * math.pi
    while angle >= 2 * math.pi:
        angle -= 2 * math.pi
    return angle


def fleet_speed(num_ships: int) -> float:
    """
    Calculate fleet speed based on number of ships.
    
    Args:
        num_ships: Number of ships in fleet
    
    Returns:
        Fleet speed (1.0 to 6.0)
    """
    if num_ships <= 1:
        return MIN_FLEET_SPEED
    return min(MAX_FLEET_SPEED, MIN_FLEET_SPEED + math.log(num_ships))


def estimated_arrival_time(distance: float, num_ships: int) -> float:
    """
    Estimate fleet arrival time.
    
    Args:
        distance: Distance to travel
        num_ships: Number of ships in fleet
    
    Returns:
        Estimated turns to arrive
    """
    speed = fleet_speed(num_ships)
    return distance / speed


def get_my_planets(planets: List[List], player_id: int) -> List[List]:
    """
    Get list of planets owned by player.
    
    Args:
        planets: List of all planets
        player_id: Player ID
    
    Returns:
        List of player's planets
    """
    return [p for p in planets if p[1] == player_id]


def get_enemy_planets(planets: List[List], player_id: int) -> List[List]:
    """
    Get list of planets owned by enemies.
    
    Args:
        planets: List of all planets
        player_id: Player ID
    
    Returns:
        List of enemy planets
    """
    return [p for p in planets if p[1] != player_id and p[1] != -1]


def get_neutral_planets(planets: List[List]) -> List[List]:
    """
    Get list of neutral planets.
    
    Args:
        planets: List of all planets
    
    Returns:
        List of neutral planets
    """
    return [p for p in planets if p[1] == -1]


def get_my_fleets(fleets: List[List], player_id: int) -> List[List]:
    """
    Get list of fleets owned by player.
    
    Args:
        fleets: List of all fleets
        player_id: Player ID
    
    Returns:
        List of player's fleets
    """
    return [f for f in fleets if f[1] == player_id]


def get_enemy_fleets(fleets: List[List], player_id: int) -> List[List]:
    """
    Get list of fleets owned by enemies.
    
    Args:
        fleets: List of all fleets
        player_id: Player ID
    
    Returns:
        List of enemy fleets
    """
    return [f for f in fleets if f[1] != player_id]


def find_nearest_planet(source_planet: List, target_planets: List[List]) -> Optional[List]:
    """
    Find nearest planet from source.
    
    Args:
        source_planet: Source planet
        target_planets: List of target planets
    
    Returns:
        Nearest planet or None if empty list
    """
    if not target_planets:
        return None
    
    min_dist = float('inf')
    nearest = None
    
    for planet in target_planets:
        dist = planet_distance(source_planet, planet)
        if dist < min_dist:
            min_dist = dist
            nearest = planet
    
    return nearest


def calculate_planet_value(planet: List) -> float:
    """
    Calculate strategic value of a planet.
    
    Value considers production and current ships.
    
    Args:
        planet: Planet data
    
    Returns:
        Strategic value score
    """
    production = planet[6]
    ships = planet[5]
    # Higher production is better, fewer ships needed to capture is better
    return production * 10 - ships * 0.1


def is_in_sun(x: float, y: float, radius: float = 0) -> bool:
    """
    Check if position is inside or too close to sun.
    
    Args:
        x, y: Position
        radius: Object radius (optional)
    
    Returns:
        True if position would hit sun
    """
    dist_to_sun = distance(x, y, SUN_POSITION[0], SUN_POSITION[1])
    return dist_to_sun < SUN_RADIUS + radius


def is_out_of_bounds(x: float, y: float, radius: float = 0) -> bool:
    """
    Check if position is out of game bounds.
    
    Args:
        x, y: Position
        radius: Object radius (optional)
    
    Returns:
        True if position is out of bounds
    """
    return (x - radius < 0 or x + radius > GAME_WIDTH or
            y - radius < 0 or y + radius > GAME_HEIGHT)


def predict_planet_position(planet: List, turns: int, angular_velocity: float) -> Tuple[float, float]:
    """
    Predict planet position after N turns.
    
    Args:
        planet: Planet data
        turns: Number of turns to predict
        angular_velocity: Angular velocity of inner planets
    
    Returns:
        Predicted (x, y) position
    """
    x, y = planet[2], planet[3]
    radius = planet[4]
    
    # Check if it's an orbiting planet
    dist_to_center = distance(x, y, SUN_POSITION[0], SUN_POSITION[1])
    orbit_radius = dist_to_center
    
    # Orbiting planets: orbit_radius + planet_radius < 50
    if orbit_radius + radius < 50:
        # Calculate current angle
        current_angle = math.atan2(y - SUN_POSITION[1], x - SUN_POSITION[0])
        # Predict new angle
        new_angle = current_angle + angular_velocity * turns
        # Calculate new position
        new_x = SUN_POSITION[0] + orbit_radius * math.cos(new_angle)
        new_y = SUN_POSITION[1] + orbit_radius * math.sin(new_angle)
        return new_x, new_y
    else:
        # Static planet
        return x, y


def format_move(from_planet_id: int, angle: float, num_ships: int) -> List:
    """
    Format a move for submission.
    
    Args:
        from_planet_id: Source planet ID
        angle: Direction angle in radians
        num_ships: Number of ships to send
    
    Returns:
        Formatted move
    """
    return [from_planet_id, angle, num_ships]


def get_total_ships(planets: List[List], fleets: List[List], player_id: int) -> int:
    """
    Calculate total ships owned by player.
    
    Args:
        planets: List of all planets
        fleets: List of all fleets
        player_id: Player ID
    
    Returns:
        Total ship count
    """
    planet_ships = sum(p[5] for p in planets if p[1] == player_id)
    fleet_ships = sum(f[6] for f in fleets if f[1] == player_id)
    return planet_ships + fleet_ships


def get_game_state_summary(observation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a summary of the current game state.
    
    Args:
        observation: Game observation
    
    Returns:
        Game state summary
    """
    player = observation["player"]
    planets = observation["planets"]
    fleets = observation.get("fleets", [])
    
    my_planets = get_my_planets(planets, player)
    enemy_planets = get_enemy_planets(planets, player)
    neutral_planets = get_neutral_planets(planets)
    
    my_fleets = get_my_fleets(fleets, player)
    enemy_fleets = get_enemy_fleets(fleets, player)
    
    return {
        "player": player,
        "my_planets_count": len(my_planets),
        "enemy_planets_count": len(enemy_planets),
        "neutral_planets_count": len(neutral_planets),
        "my_fleets_count": len(my_fleets),
        "enemy_fleets_count": len(enemy_fleets),
        "my_total_ships": get_total_ships(planets, fleets, player),
        "my_planets": my_planets,
        "enemy_planets": enemy_planets,
        "neutral_planets": neutral_planets,
    }
