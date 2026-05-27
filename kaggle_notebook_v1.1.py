# -*- coding: utf-8 -*-
"""
Kaggle Notebook Version - v1.1 - Auto-writes main.py
Orbit Wars Heuristic Agent - Optimized
Target: 900+ Score
"""

import math
from typing import Dict, List, Any, Tuple, Optional
import os


class HeuristicAgentV11:
    """
    Optimized Heuristic Agent for Orbit Wars.
    """
    
    def __init__(self):
        self.min_ships = 5
        self.attack_ratio = 0.85
        self.defense_reserve = 1
        self.player_id = None
    
    def setup(self, player_id: int):
        self.player_id = player_id
    
    def act(self, observation: Dict[str, Any]) -> List[List]:
        if self.player_id is None:
            self.setup(observation.get("player", 0))
            
        player_id = self.player_id
        planets = observation.get("planets", [])
        fleets = observation.get("fleets", [])
        angular_velocity = observation.get("angular_velocity", 0.03)
        
        my_planets = self._get_my_planets(planets, player_id)
        
        moves = []
        used_targets = {}
        
        for my_planet in my_planets:
            planet_id = my_planet[0]
            my_ships = my_planet[5]
            
            available_ships = my_ships - self.defense_reserve
            if available_ships < self.min_ships:
                continue
            
            candidates = self._evaluate_all_targets(
                my_planet, planets, fleets, angular_velocity, available_ships, used_targets
            )
            
            if not candidates:
                continue
            
            best_target, best_score, attack_ships = candidates[0]
            
            if attack_ships < self.min_ships:
                attack_ships = min(self.min_ships, available_ships)
            
            safe_angle = self._calculate_safe_angle(
                my_planet[2], my_planet[3], best_target[2], best_target[3], my_planet[4]
            )
            
            if safe_angle is not None:
                moves.append([planet_id, safe_angle, attack_ships])
                target_key = (best_target[0], planet_id)
                used_targets[target_key] = used_targets.get(target_key, 0) + attack_ships
        
        return moves
    
    def _get_my_planets(self, planets: List[List], player_id: int) -> List[List]:
        return [p for p in planets if p[1] == player_id]
    
    def _evaluate_all_targets(
        self,
        source_planet: List,
        planets: List[List],
        fleets: List[List],
        angular_velocity: float,
        available_ships: int,
        used_targets: Dict
    ) -> List[Tuple[List, float, int]]:
        
        candidates = []
        source_id = source_planet[0]
        source_x, source_y = source_planet[2], source_planet[3]
        player_id = source_planet[1]
        
        for target in planets:
            target_id = target[0]
            target_owner = target[1]
            
            if target_id == source_id:
                continue
            
            score, attack_ships = self._evaluate_single_target(
                source_planet, target, fleets, angular_velocity, available_ships, used_targets
            )
            
            if score > 0:
                candidates.append((target, score, attack_ships))
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates
    
    def _evaluate_single_target(
        self,
        source_planet: List,
        target: List,
        fleets: List[List],
        angular_velocity: float,
        available_ships: int,
        used_targets: Dict
    ) -> Tuple[float, int]:
        
        source_x, source_y = source_planet[2], source_planet[3]
        target_x, target_y = target[2], target[3]
        
        dist = math.sqrt((target_x - source_x) ** 2 + (target_y - source_y) ** 2)
        production = target[6]
        target_ships = target[5]
        target_owner = target[1]
        
        travel_time = self._estimate_travel_time(dist, available_ships)
        predicted_pos = self._predict_planet_position(target, travel_time, angular_velocity)
        adjusted_dist = math.sqrt((predicted_pos[0] - source_x) ** 2 + (predicted_pos[1] - source_y) ** 2)
        
        ships_needed = target_ships + 2
        
        if target_owner != -1:
            ships_needed += 1
        
        attack_ships = int(min(available_ships * self.attack_ratio, ships_needed * 1.5))
        
        if attack_ships < self.min_ships:
            attack_ships = min(self.min_ships, available_ships)
        
        base_score = production * 30
        dist_penalty = adjusted_dist * 0.15
        base_score -= dist_penalty
        
        if target_owner != -1:
            base_score += 30
        else:
            base_score += 50
        
        ships_efficiency = (ships_needed / attack_ships) * 12 if attack_ships > 0 else 0
        base_score += ships_efficiency
        
        if dist < 35:
            base_score += 30
        elif dist < 50:
            base_score += 15
        
        return max(0, base_score), attack_ships
    
    def _estimate_travel_time(self, dist: float, num_ships: int) -> float:
        speed = self._fleet_speed(num_ships)
        return max(1, dist / speed)
    
    def _fleet_speed(self, num_ships: int) -> float:
        if num_ships <= 1:
            return 1.0
        return min(6.0, 1.0 + math.log(num_ships))
    
    def _predict_planet_position(
        self, planet: List, turns: int, angular_velocity: float
    ) -> Tuple[float, float]:
        
        x, y = planet[2], planet[3]
        radius = planet[4]
        
        dist_to_center = math.sqrt((x - 50) ** 2 + (y - 50) ** 2)
        orbit_radius = dist_to_center
        
        if orbit_radius + radius < 50:
            current_angle = math.atan2(y - 50, x - 50)
            new_angle = current_angle + angular_velocity * turns
            new_x = 50 + orbit_radius * math.cos(new_angle)
            new_y = 50 + orbit_radius * math.sin(new_angle)
            return new_x, new_y
        else:
            return x, y
    
    def _calculate_safe_angle(
        self, source_x: float, source_y: float, target_x: float, target_y: float, source_radius: float
    ) -> Optional[float]:
        
        base_angle = math.atan2(target_y - source_y, target_x - source_x)
        
        spawn_dist = source_radius + 1
        spawn_x = source_x + spawn_dist * math.cos(base_angle)
        spawn_y = source_y + spawn_dist * math.sin(base_angle)
        
        if self._is_in_sun(spawn_x, spawn_y):
            return self._find_safe_angle(source_x, source_y, base_angle)
        if self._is_out_of_bounds(spawn_x, spawn_y):
            return self._find_safe_angle(source_x, source_y, base_angle)
        
        if self._line_intersects_sun(source_x, source_y, target_x, target_y):
            return self._find_safe_angle(source_x, source_y, base_angle)
        
        return base_angle
    
    def _find_safe_angle(self, source_x: float, source_y: float, preferred_angle: float) -> Optional[float]:
        
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
            
            if not self._is_in_sun(spawn_x, spawn_y) and not self._is_out_of_bounds(spawn_x, spawn_y):
                return angle
        
        return None
    
    def _is_in_sun(self, x: float, y: float, radius: float = 0) -> bool:
        dist_to_sun = math.sqrt((x - 50) ** 2 + (y - 50) ** 2)
        return dist_to_sun < 10 + radius
    
    def _is_out_of_bounds(self, x: float, y: float, radius: float = 0) -> bool:
        return (x - radius < 0 or x + radius > 100 or y - radius < 0 or y + radius > 100)
    
    def _line_intersects_sun(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        
        dx = x2 - x1
        dy = y2 - y1
        
        fx = x1 - 50
        fy = y1 - 50
        
        a = dx * dx + dy * dy
        b = 2 * (fx * dx + fy * dy)
        c = (fx * fx + fy * fy) - 121
        
        discriminant = b * b - 4 * a * c
        
        if discriminant < 0:
            return False
        
        discriminant = math.sqrt(discriminant)
        
        t1 = (-b - discriminant) / (2 * a)
        t2 = (-b + discriminant) / (2 * a)
        
        if (0 <= t1 <= 1) or (0 <= t2 <= 1):
            return True
        
        return False


_agent_instance = None


def agent(observation: Dict[str, Any], configuration: Dict[str, Any]) -> List[List]:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = HeuristicAgentV11()
    
    return _agent_instance.act(observation)


# --- KAGGLE NOTEBOOK: WRITE main.py TO OUTPUT ---

if __name__ == "__main__":
    print("Orbit Wars Heuristic Agent v1.1 - Kaggle Notebook")
    print("=" * 60)
    
    test_obs = {
        "player": 0,
        "planets": [
            [0, 0, 20.0, 20.0, 2.0, 50, 3],
            [1, 1, 80.0, 80.0, 2.0, 30, 2],
            [2, -1, 50.0, 20.0, 1.5, 20, 1],
        ],
        "fleets": [],
        "angular_velocity": 0.03,
    }
    
    result = agent(test_obs, {})
    print(f"Test result: {result}")
    print("\n✅ Agent is ready for Kaggle submission!")
    
    print("\nWriting main.py to output...")
    
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write('''# -*- coding: utf-8 -*-
"""
Orbit Wars Heuristic Agent v1.1 - Kaggle Submission
Target: 900+ Score
Optimized from v1.0 (287.1 score)
"""

import math
from typing import Dict, List, Any, Tuple, Optional


class HeuristicAgentV11:
    def __init__(self):
        self.min_ships = 5
        self.attack_ratio = 0.85
        self.defense_reserve = 1
        self.player_id = None
    
    def setup(self, player_id: int):
        self.player_id = player_id
    
    def act(self, observation: Dict[str, Any]) -> List[List]:
        if self.player_id is None:
            self.setup(observation.get("player", 0))
            
        player_id = self.player_id
        planets = observation.get("planets", [])
        fleets = observation.get("fleets", [])
        angular_velocity = observation.get("angular_velocity", 0.03)
        
        my_planets = self._get_my_planets(planets, player_id)
        
        moves = []
        used_targets = {}
        
        for my_planet in my_planets:
            planet_id = my_planet[0]
            my_ships = my_planet[5]
            
            available_ships = my_ships - self.defense_reserve
            if available_ships < self.min_ships:
                continue
            
            candidates = self._evaluate_all_targets(
                my_planet, planets, fleets, angular_velocity, available_ships, used_targets
            )
            
            if not candidates:
                continue
            
            best_target, best_score, attack_ships = candidates[0]
            
            if attack_ships < self.min_ships:
                attack_ships = min(self.min_ships, available_ships)
            
            safe_angle = self._calculate_safe_angle(
                my_planet[2], my_planet[3], best_target[2], best_target[3], my_planet[4]
            )
            
            if safe_angle is not None:
                moves.append([planet_id, safe_angle, attack_ships])
                target_key = (best_target[0], planet_id)
                used_targets[target_key] = used_targets.get(target_key, 0) + attack_ships
        
        return moves
    
    def _get_my_planets(self, planets: List[List], player_id: int) -> List[List]:
        return [p for p in planets if p[1] == player_id]
    
    def _evaluate_all_targets(
        self,
        source_planet: List,
        planets: List[List],
        fleets: List[List],
        angular_velocity: float,
        available_ships: int,
        used_targets: Dict
    ) -> List[Tuple[List, float, int]]:
        
        candidates = []
        source_id = source_planet[0]
        source_x, source_y = source_planet[2], source_planet[3]
        player_id = source_planet[1]
        
        for target in planets:
            target_id = target[0]
            target_owner = target[1]
            
            if target_id == source_id:
                continue
            
            score, attack_ships = self._evaluate_single_target(
                source_planet, target, fleets, angular_velocity, available_ships, used_targets
            )
            
            if score > 0:
                candidates.append((target, score, attack_ships))
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates
    
    def _evaluate_single_target(
        self,
        source_planet: List,
        target: List,
        fleets: List[List],
        angular_velocity: float,
        available_ships: int,
        used_targets: Dict
    ) -> Tuple[float, int]:
        
        source_x, source_y = source_planet[2], source_planet[3]
        target_x, target_y = target[2], target[3]
        
        dist = math.sqrt((target_x - source_x) ** 2 + (target_y - source_y) ** 2)
        production = target[6]
        target_ships = target[5]
        target_owner = target[1]
        
        travel_time = self._estimate_travel_time(dist, available_ships)
        predicted_pos = self._predict_planet_position(target, travel_time, angular_velocity)
        adjusted_dist = math.sqrt((predicted_pos[0] - source_x) ** 2 + (predicted_pos[1] - source_y) ** 2)
        
        ships_needed = target_ships + 2
        
        if target_owner != -1:
            ships_needed += 1
        
        attack_ships = int(min(available_ships * 0.85, ships_needed * 1.5))
        
        if attack_ships < 5:
            attack_ships = min(5, available_ships)
        
        base_score = production * 30
        dist_penalty = adjusted_dist * 0.15
        base_score -= dist_penalty
        
        if target_owner != -1:
            base_score += 30
        else:
            base_score += 50
        
        ships_efficiency = (ships_needed / attack_ships) * 12 if attack_ships > 0 else 0
        base_score += ships_efficiency
        
        if dist < 35:
            base_score += 30
        elif dist < 50:
            base_score += 15
        
        return max(0, base_score), attack_ships
    
    def _estimate_travel_time(self, dist: float, num_ships: int) -> float:
        speed = self._fleet_speed(num_ships)
        return max(1, dist / speed)
    
    def _fleet_speed(self, num_ships: int) -> float:
        if num_ships <= 1:
            return 1.0
        return min(6.0, 1.0 + math.log(num_ships))
    
    def _predict_planet_position(
        self, planet: List, turns: int, angular_velocity: float
    ) -> Tuple[float, float]:
        
        x, y = planet[2], planet[3]
        radius = planet[4]
        
        dist_to_center = math.sqrt((x - 50) ** 2 + (y - 50) ** 2)
        orbit_radius = dist_to_center
        
        if orbit_radius + radius < 50:
            current_angle = math.atan2(y - 50, x - 50)
            new_angle = current_angle + angular_velocity * turns
            new_x = 50 + orbit_radius * math.cos(new_angle)
            new_y = 50 + orbit_radius * math.sin(new_angle)
            return new_x, new_y
        else:
            return x, y
    
    def _calculate_safe_angle(
        self, source_x: float, source_y: float, target_x: float, target_y: float, source_radius: float
    ) -> Optional[float]:
        
        base_angle = math.atan2(target_y - source_y, target_x - source_x)
        
        spawn_dist = source_radius + 1
        spawn_x = source_x + spawn_dist * math.cos(base_angle)
        spawn_y = source_y + spawn_dist * math.sin(base_angle)
        
        if self._is_in_sun(spawn_x, spawn_y):
            return self._find_safe_angle(source_x, source_y, base_angle)
        if self._is_out_of_bounds(spawn_x, spawn_y):
            return self._find_safe_angle(source_x, source_y, base_angle)
        
        if self._line_intersects_sun(source_x, source_y, target_x, target_y):
            return self._find_safe_angle(source_x, source_y, base_angle)
        
        return base_angle
    
    def _find_safe_angle(self, source_x: float, source_y: float, preferred_angle: float) -> Optional[float]:
        
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
            
            if not self._is_in_sun(spawn_x, spawn_y) and not self._is_out_of_bounds(spawn_x, spawn_y):
                return angle
        
        return None
    
    def _is_in_sun(self, x: float, y: float, radius: float = 0) -> bool:
        dist_to_sun = math.sqrt((x - 50) ** 2 + (y - 50) ** 2)
        return dist_to_sun < 10 + radius
    
    def _is_out_of_bounds(self, x: float, y: float, radius: float = 0) -> bool:
        return (x - radius < 0 or x + radius > 100 or y - radius < 0 or y + radius > 100)
    
    def _line_intersects_sun(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        
        dx = x2 - x1
        dy = y2 - y1
        
        fx = x1 - 50
        fy = y1 - 50
        
        a = dx * dx + dy * dy
        b = 2 * (fx * dx + fy * dy)
        c = (fx * fx + fy * fy) - 121
        
        discriminant = b * b - 4 * a * c
        
        if discriminant < 0:
            return False
        
        discriminant = math.sqrt(discriminant)
        
        t1 = (-b - discriminant) / (2 * a)
        t2 = (-b + discriminant) / (2 * a)
        
        if (0 <= t1 <= 1) or (0 <= t2 <= 1):
            return True
        
        return False


_agent_instance = None


def agent(observation: Dict[str, Any], configuration: Dict[str, Any]) -> List[List]:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = HeuristicAgentV11()
    
    return _agent_instance.act(observation)

''')
    
    print("✅ main.py written to output! Ready to submit!")
