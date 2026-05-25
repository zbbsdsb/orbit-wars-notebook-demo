"""
Heuristic Agent for Orbit Wars.

A sophisticated rule-based agent that evaluates targets, ensures launch safety,
predicts orbital mechanics, and optimizes fleet deployment.

Contributors: CeaserZhao, PrismScope
"""

import math
from typing import Dict, List, Any, Tuple, Optional
from src.agents.base_agent import BaseAgent
from src.utils.game_utils import (
    distance, planet_distance, angle_between, fleet_speed,
    get_my_planets, get_enemy_planets, get_neutral_planets,
    get_my_fleets, get_enemy_fleets, predict_planet_position,
    calculate_planet_value, is_in_sun, is_out_of_bounds,
    get_total_ships, SUN_POSITION, SUN_RADIUS, GAME_WIDTH, GAME_HEIGHT
)


class HeuristicAgent(BaseAgent):
    """
    Sophisticated heuristic agent for Orbit Wars.
    
    Features:
    - Multi-factor target evaluation
    - Launch safety checking (sun/bounds avoidance)
    - Orbital planet position prediction
    - Fleet size optimization
    - Comet handling
    """

    def __init__(
        self,
        name: str = "HeuristicAgent",
        min_ships: int = 10,
        attack_ratio: float = 0.5,
        defense_reserve: int = 5
    ):
        """
        Initialize the heuristic agent.
        
        Args:
            name: Agent name
            min_ships: Minimum ships required to launch an attack
            attack_ratio: Ratio of ships to send (0.0-1.0)
            defense_reserve: Minimum ships to keep for defense
        """
        super().__init__(name)
        self.min_ships = min_ships
        self.attack_ratio = attack_ratio
        self.defense_reserve = defense_reserve

    def act(self, observation: Dict[str, Any]) -> List[List]:
        """
        Decide actions based on game observation.
        
        Args:
            observation: Game state containing:
                - player: Your player ID
                - planets: List of planets [id, owner, x, y, radius, ships, production]
                - fleets: List of fleets
                - angular_velocity: Angular velocity of inner planets
                - comet_planet_ids: List of comet planet IDs
                - comets: Comet data
                - initial_planets: Initial planet positions for orbit calculation
        
        Returns:
            List of moves [[from_planet_id, angle, num_ships], ...]
        """
        player_id = observation["player"]
        planets = observation["planets"]
        fleets = observation.get("fleets", [])
        angular_velocity = observation.get("angular_velocity", 0.03)
        comet_planet_ids = observation.get("comet_planet_ids", [])
        comets = observation.get("comets", [])

        my_planets = get_my_planets(planets, player_id)
        enemy_planets = get_enemy_planets(planets, player_id)
        neutral_planets = get_neutral_planets(planets)
        my_fleets = get_my_fleets(fleets, player_id)
        enemy_fleets = get_enemy_fleets(fleets, player_id)

        moves = []
        used_targets = {}

        for my_planet in my_planets:
            planet_id = my_planet[0]
            my_x, my_y = my_planet[2], my_planet[3]
            my_ships = my_planet[5]
            my_production = my_planet[6]

            available_ships = my_ships - self.defense_reserve
            if available_ships < self.min_ships:
                continue

            incoming_enemy = self._get_incoming_enemy_fleets(
                my_planet, enemy_fleets, player_id
            )
            if incoming_enemy:
                defense_needed = self._calculate_defense_needed(my_planet, incoming_enemy)
                if available_ships <= defense_needed + self.min_ships:
                    continue

            candidates = self._evaluate_all_targets(
                my_planet, enemy_planets, neutral_planets, 
                my_planets, enemy_fleets, angular_velocity, 
                comet_planet_ids, comets, used_targets
            )

            if not candidates:
                continue

            best_target, best_score, attack_ships = candidates[0]
            
            if attack_ships < self.min_ships:
                continue

            safe_angle = self._calculate_safe_angle(
                my_x, my_y, best_target[2], best_target[3], my_planet[4]
            )

            if safe_angle is None:
                continue

            moves.append([planet_id, safe_angle, attack_ships])
            target_key = (best_target[0], planet_id)
            used_targets[target_key] = used_targets.get(target_key, 0) + attack_ships

        return moves

    def _get_incoming_enemy_fleets(
        self, planet: List, enemy_fleets: List, player_id: int
    ) -> List:
        """
        Get enemy fleets heading toward this planet.
        
        Args:
            planet: My planet
            enemy_fleets: All enemy fleets
        
        Returns:
            List of enemy fleets targeting this planet
        """
        incoming = []
        px, py = planet[2], planet[3]
        planet_radius = planet[4]
        
        for fleet in enemy_fleets:
            fx, fy = fleet[2], fleet[3]
            angle = fleet[4]
            fleet_ships = fleet[6]
            
            dist = distance(fx, fy, px, py)
            if dist < 50:
                dx = px - fx
                dy = py - fy
                fleet_angle = math.atan2(dy, dx)
                angle_diff = abs(self._normalize_angle(fleet_angle - angle))
                if angle_diff < 0.3:
                    incoming.append((fleet, dist))
        
        return sorted(incoming, key=lambda x: x[1])

    def _calculate_defense_needed(
        self, planet: List, incoming: List
    ) -> int:
        """
        Calculate minimum ships needed for defense.
        
        Args:
            planet: My planet
            incoming: Incoming enemy fleets
        
        Returns:
            Minimum ships needed to defend
        """
        if not incoming:
            return 0
        
        max_threat = 0
        for fleet, dist in incoming[:3]:
            threat = fleet[6]
            max_threat = max(max_threat, threat)
        
        return max(0, planet[5] - max_threat + 10)

    def _evaluate_all_targets(
        self,
        source_planet: List,
        enemy_planets: List,
        neutral_planets: List,
        my_planets: List,
        enemy_fleets: List,
        angular_velocity: float,
        comet_planet_ids: List,
        comets: List,
        used_targets: Dict
    ) -> List[Tuple[List, float, int]]:
        """
        Evaluate all potential targets and return sorted by score.
        
        Args:
            source_planet: Source planet for attack
            enemy_planets: Available enemy planets
            neutral_planets: Available neutral planets
            my_planets: All my planets
            enemy_fleets: All enemy fleets
            angular_velocity: Angular velocity for prediction
            comet_planet_ids: Comet planet IDs
            comets: Comet data
            used_targets: Already targeted planets
        
        Returns:
            List of (target, score, attack_ships) tuples sorted by score
        """
        candidates = []
        source_id = source_planet[0]
        source_x, source_y = source_planet[2], source_planet[3]
        available_ships = source_planet[5] - self.defense_reserve

        for target in enemy_planets:
            score, attack_ships = self._evaluate_target(
                source_planet, target, my_planets, enemy_fleets,
                angular_velocity, available_ships, used_targets, is_enemy=True
            )
            if score > 0 and attack_ships >= self.min_ships:
                candidates.append((target, score, attack_ships))

        for target in neutral_planets:
            score, attack_ships = self._evaluate_target(
                source_planet, target, my_planets, enemy_fleets,
                angular_velocity, available_ships, used_targets, is_enemy=False
            )
            if score > 0 and attack_ships >= self.min_ships:
                candidates.append((target, score, attack_ships))

        for comet_id in comet_planet_ids:
            comet = self._find_planet_by_id(comet_id, comets)
            if comet:
                score, attack_ships = self._evaluate_target(
                    source_planet, comet, my_planets, enemy_fleets,
                    angular_velocity, available_ships, used_targets, is_enemy=True
                )
                if score > 0 and attack_ships >= self.min_ships:
                    candidates.append((comet, score, attack_ships))

        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates

    def _find_planet_by_id(self, planet_id: int, planets: List) -> Optional[List]:
        """Find planet by ID from list."""
        for p in planets:
            if p[0] == planet_id:
                return p
        return None

    def _evaluate_target(
        self,
        source: List,
        target: List,
        my_planets: List,
        enemy_fleets: List,
        angular_velocity: float,
        available_ships: int,
        used_targets: Dict,
        is_enemy: bool
    ) -> Tuple[float, int]:
        """
        Evaluate a single target's value.
        
        Returns:
            (target_score, recommended_attack_ships)
        """
        source_id = source[0]
        target_id = target[0]
        
        dist = planet_distance(source, target)
        
        production = target[6]
        target_ships = target[5]
        
        travel_time = self._estimate_travel_time(dist, available_ships)
        predicted_pos = predict_planet_position(target, travel_time, angular_velocity)
        adjusted_dist = distance(source[2], source[3], predicted_pos[0], predicted_pos[1])
        
        ships_needed = target_ships + 1
        if is_enemy:
            ships_needed += 1
        
        incoming_support = self._predict_incoming_support(
            target, enemy_fleets, travel_time
        )
        ships_needed += incoming_support
        
        if ships_needed > available_ships:
            efficiency = available_ships / ships_needed if ships_needed > 0 else 0
            if efficiency < 0.7:
                return 0.0, 0
        
        attack_ships = min(available_ships, int(ships_needed * 1.2))
        
        base_score = production * 15
        
        dist_penalty = adjusted_dist * 0.3
        base_score -= dist_penalty
        
        if is_enemy:
            base_score += 20
        
        ships_efficiency = (ships_needed / attack_ships) * 10
        base_score += ships_efficiency
        
        if dist < 30:
            base_score += 15
        elif dist < 50:
            base_score += 10
        
        reserved = used_targets.get((target_id, source_id), 0)
        if reserved > 0:
            base_score -= reserved * 0.5
        
        return max(0, base_score), attack_ships

    def _estimate_travel_time(self, dist: float, num_ships: int) -> float:
        """Estimate travel time based on distance and fleet size."""
        speed = fleet_speed(num_ships)
        return max(1, dist / speed)

    def _predict_incoming_support(
        self, target: List, enemy_fleets: List, time_horizon: float
    ) -> int:
        """
        Predict how many ships will arrive at target from enemies.
        
        Args:
            target: Target planet
            enemy_fleets: All enemy fleets
            time_horizon: Time to consider
        
        Returns:
            Total ships expected to arrive
        """
        support = 0
        tx, ty = target[2], target[3]
        
        for fleet in enemy_fleets:
            fx, fy = fleet[2], fleet[3]
            fleet_ships = fleet[6]
            
            dist = distance(fx, fy, tx, ty)
            travel_time = dist / fleet_speed(fleet_ships)
            
            if travel_time <= time_horizon + 5:
                support += fleet_ships
        
        return support

    def _calculate_safe_angle(
        self, 
        source_x: float, 
        source_y: float, 
        target_x: float, 
        target_y: float,
        source_radius: float
    ) -> Optional[float]:
        """
        Calculate a safe launch angle avoiding sun and bounds.
        
        Args:
            source_x, source_y: Source planet position
            target_x, target_y: Target position
            source_radius: Source planet radius
        
        Returns:
            Safe angle in radians, or None if no safe path exists
        """
        base_angle = math.atan2(target_y - source_y, target_x - source_x)
        
        spawn_dist = source_radius + 1
        spawn_x = source_x + spawn_dist * math.cos(base_angle)
        spawn_y = source_y + spawn_dist * math.sin(base_angle)
        
        if is_in_sun(spawn_x, spawn_y):
            return None
        if is_out_of_bounds(spawn_x, spawn_y):
            return None
        
        max_dist = max(distance(source_x, source_y, 0, 0),
                      distance(source_x, source_y, GAME_WIDTH, 0),
                      distance(source_x, source_y, 0, GAME_HEIGHT),
                      distance(source_x, source_y, GAME_WIDTH, GAME_HEIGHT))
        
        for t in [0.25, 0.5, 0.75, 1.0]:
            check_dist = distance(source_x, source_y, target_x, target_y) * t
            check_x = spawn_x + (target_x - spawn_x) * t
            check_y = spawn_y + (target_y - spawn_y) * t
            
            if is_in_sun(check_x, check_y):
                return self._find_safe_angle(source_x, source_y, base_angle)
        
        return base_angle

    def _find_safe_angle(
        self, 
        source_x: float, 
        source_y: float, 
        preferred_angle: float
    ) -> Optional[float]:
        """
        Find a safe angle near the preferred angle.
        
        Args:
            source_x, source_y: Source position
            preferred_angle: Desired angle
        
        Returns:
            Safe angle or None
        """
        angles_to_try = [
            preferred_angle,
            preferred_angle + 0.1,
            preferred_angle - 0.1,
            preferred_angle + 0.2,
            preferred_angle - 0.2,
            preferred_angle + math.pi / 2,
            preferred_angle - math.pi / 2,
        ]
        
        for angle in angles_to_try:
            spawn_dist = 3
            spawn_x = source_x + spawn_dist * math.cos(angle)
            spawn_y = source_y + spawn_dist * math.sin(angle)
            
            if not is_in_sun(spawn_x, spawn_y) and not is_out_of_bounds(spawn_x, spawn_y):
                if not self._line_intersects_sun(source_x, source_y, spawn_x, spawn_y):
                    return angle
        
        return None

    def _line_intersects_sun(
        self, 
        x1: float, 
        y1: float, 
        x2: float, 
        y2: float
    ) -> bool:
        """
        Check if a line segment from (x1,y1) to (x2,y2) intersects the sun.
        
        Args:
            x1, y1: Start point
            x2, y2: End point
        
        Returns:
            True if line intersects sun
        """
        sx, sy = SUN_POSITION
        
        dx = x2 - x1
        dy = y2 - y1
        
        fx = x1 - sx
        fy = y1 - sy
        
        a = dx * dx + dy * dy
        b = 2 * (fx * dx + fy * dy)
        c = (fx * fx + fy * fy) - (SUN_RADIUS + 1) * (SUN_RADIUS + 1)
        
        discriminant = b * b - 4 * a * c
        
        if discriminant < 0:
            return False
        
        discriminant = math.sqrt(discriminant)
        
        t1 = (-b - discriminant) / (2 * a)
        t2 = (-b + discriminant) / (2 * a)
        
        if (0 <= t1 <= 1) or (0 <= t2 <= 1):
            return True
        
        return False

    def _normalize_angle(self, angle: float) -> float:
        """Normalize angle to [-pi, pi]."""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle


def create_agent() -> HeuristicAgent:
    """Factory function to create the agent instance."""
    return HeuristicAgent()


def agent(observation: Dict[str, Any], configuration: Dict[str, Any]) -> List[List]:
    """
    Main agent function for Kaggle submission.
    
    Args:
        observation: Game state
        configuration: Game configuration
    
    Returns:
        List of moves
    """
    return create_agent()(observation, configuration)
