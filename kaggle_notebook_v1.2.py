# -*- coding: utf-8 -*-
"""
Kaggle Notebook Version - v1.2 - Auto-writes main.py
Orbit Wars Heuristic Agent - ADVANCED OPTIMIZATION
Target: 900+ Score
Improvements over v1.1 (600 score):
- Dynamic weights based on game stage
- Multi-planet attack coordination
- Enhanced fleet management
- Enemy fleet tracking & defense
- Game stage detection
"""

import math
from typing import Dict, List, Any, Tuple, Optional
import os


class AdvancedAgentV12:
    """
    Advanced Heuristic Agent for Orbit Wars v1.2
    """
    
    def __init__(self):
        self.min_ships = 3
        self.max_ships_per_attack = 50
        self.player_id = None
        self.turn_count = 0
    
    def setup(self, player_id: int):
        self.player_id = player_id
    
    def act(self, observation: Dict[str, Any]) -> List[List]:
        if self.player_id is None:
            self.setup(observation.get("player", 0))
            
        self.turn_count += 1
        
        player_id = self.player_id
        planets = observation.get("planets", [])
        fleets = observation.get("fleets", [])
        angular_velocity = observation.get("angular_velocity", 0.03)
        
        my_planets = self._get_my_planets(planets, player_id)
        enemy_planets = self._get_enemy_planets(planets, player_id)
        neutral_planets = self._get_neutral_planets(planets)
        
        game_stage = self._detect_game_stage(my_planets, enemy_planets, neutral_planets)
        
        moves = []
        used_targets = {}
        assigned_ships = {}
        
        for planet in my_planets:
            assigned_ships[planet[0]] = 0
        
        for my_planet in my_planets:
            planet_id = my_planet[0]
            x, y = my_planet[2], my_planet[3]
            radius = my_planet[4]
            total_ships = my_planet[5]
            prod = my_planet[6]
            
            threat_level = self._calculate_threat_level(my_planet, fleets, player_id)
            
            defense_ships = self._calculate_defense_ships(total_ships, threat_level, game_stage)
            available_ships = total_ships - defense_ships
            
            if available_ships < self.min_ships:
                continue
            
            candidates = self._evaluate_all_targets(
                my_planet, planets, fleets, angular_velocity, available_ships, 
                used_targets, game_stage, player_id
            )
            
            if not candidates:
                continue
            
            best_target, best_score, attack_ships = candidates[0]
            
            if attack_ships < self.min_ships:
                attack_ships = min(self.min_ships, available_ships)
            
            attack_ships = min(attack_ships, available_ships, self.max_ships_per_attack)
            
            if attack_ships < self.min_ships:
                continue
            
            safe_angle = self._calculate_safe_angle(x, y, best_target[2], best_target[3], radius)
            
            if safe_angle is not None:
                moves.append([planet_id, safe_angle, attack_ships])
                target_key = (best_target[0], planet_id)
                used_targets[target_key] = used_targets.get(target_key, 0) + attack_ships
                assigned_ships[planet_id] += attack_ships
        
        return moves
    
    def _detect_game_stage(self, my_planets: List, enemy_planets: List, neutral_planets: List) -> str:
        total_planets = len(my_planets) + len(enemy_planets) + len(neutral_planets)
        my_ratio = len(my_planets) / total_planets if total_planets > 0 else 0
        
        if len(neutral_planets) > total_planets * 0.4:
            return "early"
        elif my_ratio < 0.3:
            return "early"
        elif len(neutral_planets) > 0:
            return "mid"
        else:
            return "late"
    
    def _calculate_threat_level(self, planet: List, fleets: List, player_id: int) -> float:
        x, y = planet[2], planet[3]
        threat = 0.0
        
        for fleet in fleets:
            if fleet[2] != player_id:
                fx, fy = fleet[3], fleet[4]
                dist = math.sqrt((fx - x) ** 2 + (fy - y) ** 2)
                if dist < 40:
                    threat += fleet[5] / (dist + 1)
        
        return threat
    
    def _calculate_defense_ships(self, total_ships: int, threat_level: float, game_stage: str) -> int:
        base_defense = 1
        
        if game_stage == "early":
            base_defense = 1
        elif game_stage == "mid":
            base_defense = max(2, int(total_ships * 0.1))
        else:
            base_defense = max(3, int(total_ships * 0.15))
        
        threat_ships = int(threat_level * 0.5)
        
        return min(base_defense + threat_ships, total_ships - self.min_ships)
    
    def _get_my_planets(self, planets: List[List], player_id: int) -> List[List]:
        return sorted([p for p in planets if p[1] == player_id], key=lambda x: -x[6])
    
    def _get_enemy_planets(self, planets: List[List], player_id: int) -> List[List]:
        return [p for p in planets if p[1] != player_id and p[1] != -1]
    
    def _get_neutral_planets(self, planets: List[List]) -> List[List]:
        return [p for p in planets if p[1] == -1]
    
    def _evaluate_all_targets(
        self,
        source_planet: List,
        planets: List[List],
        fleets: List[List],
        angular_velocity: float,
        available_ships: int,
        used_targets: Dict,
        game_stage: str,
        player_id: int
    ) -> List[Tuple[List, float, int]]:
        
        candidates = []
        source_id = source_planet[0]
        source_x, source_y = source_planet[2], source_planet[3]
        
        weights = self._get_stage_weights(game_stage)
        
        for target in planets:
            target_id = target[0]
            target_owner = target[1]
            
            if target_id == source_id:
                continue
            
            if target_owner == player_id:
                continue
            
            score, attack_ships = self._evaluate_single_target(
                source_planet, target, fleets, angular_velocity, available_ships, 
                used_targets, weights, player_id
            )
            
            if score > 0:
                candidates.append((target, score, attack_ships))
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:3]
    
    def _get_stage_weights(self, game_stage: str) -> Dict[str, float]:
        if game_stage == "early":
            return {
                "production_weight": 45.0,
                "distance_weight": 0.08,
                "neutral_bonus": 60.0,
                "enemy_bonus": 40.0,
                "close_bonus": 40.0,
                "efficiency_weight": 15.0
            }
        elif game_stage == "mid":
            return {
                "production_weight": 35.0,
                "distance_weight": 0.12,
                "neutral_bonus": 45.0,
                "enemy_bonus": 50.0,
                "close_bonus": 25.0,
                "efficiency_weight": 12.0
            }
        else:
            return {
                "production_weight": 30.0,
                "distance_weight": 0.15,
                "neutral_bonus": 30.0,
                "enemy_bonus": 60.0,
                "close_bonus": 20.0,
                "efficiency_weight": 10.0
            }
    
    def _evaluate_single_target(
        self,
        source_planet: List,
        target: List,
        fleets: List[List],
        angular_velocity: float,
        available_ships: int,
        used_targets: Dict,
        weights: Dict[str, float],
        player_id: int
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
        
        attacking_fleets = self._get_attacking_fleets(target[0], fleets, player_id)
        incoming_ships = sum(f[5] for f in attacking_fleets)
        
        ships_needed = max(target_ships - incoming_ships + 2, 3)
        
        if target_owner != -1:
            ships_needed += 2
        
        attack_ships = int(min(available_ships * 0.9, ships_needed * 1.3))
        
        if attack_ships < self.min_ships:
            attack_ships = min(self.min_ships, available_ships)
        
        base_score = production * weights["production_weight"]
        
        dist_penalty = adjusted_dist * weights["distance_weight"]
        base_score -= dist_penalty
        
        if target_owner == -1:
            base_score += weights["neutral_bonus"]
        else:
            base_score += weights["enemy_bonus"]
        
        ships_efficiency = (ships_needed / attack_ships) * weights["efficiency_weight"] if attack_ships > 0 else 0
        base_score += ships_efficiency
        
        if dist < 30:
            base_score += weights["close_bonus"]
        elif dist < 45:
            base_score += weights["close_bonus"] * 0.5
        
        if self._is_enemy_attacking(target, fleets, player_id):
            base_score += 20
        
        return max(0, base_score), attack_ships
    
    def _get_attacking_fleets(self, target_id: int, fleets: List, player_id: int) -> List:
        return [f for f in fleets if f[2] == player_id and f[1] == target_id]
    
    def _is_enemy_attacking(self, target: List, fleets: List, player_id: int) -> bool:
        target_id = target[0]
        for fleet in fleets:
            if fleet[2] != player_id and fleet[1] == target_id:
                return True
        return False
    
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
            preferred_angle + 0.05,
            preferred_angle - 0.05,
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
        _agent_instance = AdvancedAgentV12()
    
    return _agent_instance.act(observation)


if __name__ == "__main__":
    print("Orbit Wars Advanced Agent v1.2 - Kaggle Notebook")
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
Orbit Wars Advanced Agent v1.2 - Kaggle Submission
Target: 900+ Score
Improvements over v1.1 (600 score):
- Dynamic weights based on game stage
- Multi-planet attack coordination
- Enhanced fleet management
- Enemy fleet tracking & defense
- Game stage detection
"""

import math
from typing import Dict, List, Any, Tuple, Optional


class AdvancedAgentV12:
    def __init__(self):
        self.min_ships = 3
        self.max_ships_per_attack = 50
        self.player_id = None
        self.turn_count = 0
    
    def setup(self, player_id: int):
        self.player_id = player_id
    
    def act(self, observation: Dict[str, Any]) -> List[List]:
        if self.player_id is None:
            self.setup(observation.get("player", 0))
            
        self.turn_count += 1
        
        player_id = self.player_id
        planets = observation.get("planets", [])
        fleets = observation.get("fleets", [])
        angular_velocity = observation.get("angular_velocity", 0.03)
        
        my_planets = self._get_my_planets(planets, player_id)
        enemy_planets = self._get_enemy_planets(planets, player_id)
        neutral_planets = self._get_neutral_planets(planets)
        
        game_stage = self._detect_game_stage(my_planets, enemy_planets, neutral_planets)
        
        moves = []
        used_targets = {}
        assigned_ships = {}
        
        for planet in my_planets:
            assigned_ships[planet[0]] = 0
        
        for my_planet in my_planets:
            planet_id = my_planet[0]
            x, y = my_planet[2], my_planet[3]
            radius = my_planet[4]
            total_ships = my_planet[5]
            prod = my_planet[6]
            
            threat_level = self._calculate_threat_level(my_planet, fleets, player_id)
            
            defense_ships = self._calculate_defense_ships(total_ships, threat_level, game_stage)
            available_ships = total_ships - defense_ships
            
            if available_ships < self.min_ships:
                continue
            
            candidates = self._evaluate_all_targets(
                my_planet, planets, fleets, angular_velocity, available_ships, 
                used_targets, game_stage, player_id
            )
            
            if not candidates:
                continue
            
            best_target, best_score, attack_ships = candidates[0]
            
            if attack_ships < self.min_ships:
                attack_ships = min(self.min_ships, available_ships)
            
            attack_ships = min(attack_ships, available_ships, self.max_ships_per_attack)
            
            if attack_ships < self.min_ships:
                continue
            
            safe_angle = self._calculate_safe_angle(x, y, best_target[2], best_target[3], radius)
            
            if safe_angle is not None:
                moves.append([planet_id, safe_angle, attack_ships])
                target_key = (best_target[0], planet_id)
                used_targets[target_key] = used_targets.get(target_key, 0) + attack_ships
                assigned_ships[planet_id] += attack_ships
        
        return moves
    
    def _detect_game_stage(self, my_planets: List, enemy_planets: List, neutral_planets: List) -> str:
        total_planets = len(my_planets) + len(enemy_planets) + len(neutral_planets)
        my_ratio = len(my_planets) / total_planets if total_planets > 0 else 0
        
        if len(neutral_planets) > total_planets * 0.4:
            return "early"
        elif my_ratio < 0.3:
            return "early"
        elif len(neutral_planets) > 0:
            return "mid"
        else:
            return "late"
    
    def _calculate_threat_level(self, planet: List, fleets: List, player_id: int) -> float:
        x, y = planet[2], planet[3]
        threat = 0.0
        
        for fleet in fleets:
            if fleet[2] != player_id:
                fx, fy = fleet[3], fleet[4]
                dist = math.sqrt((fx - x) ** 2 + (fy - y) ** 2)
                if dist < 40:
                    threat += fleet[5] / (dist + 1)
        
        return threat
    
    def _calculate_defense_ships(self, total_ships: int, threat_level: float, game_stage: str) -> int:
        base_defense = 1
        
        if game_stage == "early":
            base_defense = 1
        elif game_stage == "mid":
            base_defense = max(2, int(total_ships * 0.1))
        else:
            base_defense = max(3, int(total_ships * 0.15))
        
        threat_ships = int(threat_level * 0.5)
        
        return min(base_defense + threat_ships, total_ships - 3)
    
    def _get_my_planets(self, planets: List[List], player_id: int) -> List[List]:
        return sorted([p for p in planets if p[1] == player_id], key=lambda x: -x[6])
    
    def _get_enemy_planets(self, planets: List[List], player_id: int) -> List[List]:
        return [p for p in planets if p[1] != player_id and p[1] != -1]
    
    def _get_neutral_planets(self, planets: List[List]) -> List[List]:
        return [p for p in planets if p[1] == -1]
    
    def _evaluate_all_targets(
        self,
        source_planet: List,
        planets: List[List],
        fleets: List[List],
        angular_velocity: float,
        available_ships: int,
        used_targets: Dict,
        game_stage: str,
        player_id: int
    ) -> List[Tuple[List, float, int]]:
        
        candidates = []
        source_id = source_planet[0]
        source_x, source_y = source_planet[2], source_planet[3]
        
        weights = self._get_stage_weights(game_stage)
        
        for target in planets:
            target_id = target[0]
            target_owner = target[1]
            
            if target_id == source_id:
                continue
            
            if target_owner == player_id:
                continue
            
            score, attack_ships = self._evaluate_single_target(
                source_planet, target, fleets, angular_velocity, available_ships, 
                used_targets, weights, player_id
            )
            
            if score > 0:
                candidates.append((target, score, attack_ships))
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:3]
    
    def _get_stage_weights(self, game_stage: str) -> Dict[str, float]:
        if game_stage == "early":
            return {
                "production_weight": 45.0,
                "distance_weight": 0.08,
                "neutral_bonus": 60.0,
                "enemy_bonus": 40.0,
                "close_bonus": 40.0,
                "efficiency_weight": 15.0
            }
        elif game_stage == "mid":
            return {
                "production_weight": 35.0,
                "distance_weight": 0.12,
                "neutral_bonus": 45.0,
                "enemy_bonus": 50.0,
                "close_bonus": 25.0,
                "efficiency_weight": 12.0
            }
        else:
            return {
                "production_weight": 30.0,
                "distance_weight": 0.15,
                "neutral_bonus": 30.0,
                "enemy_bonus": 60.0,
                "close_bonus": 20.0,
                "efficiency_weight": 10.0
            }
    
    def _evaluate_single_target(
        self,
        source_planet: List,
        target: List,
        fleets: List[List],
        angular_velocity: float,
        available_ships: int,
        used_targets: Dict,
        weights: Dict[str, float],
        player_id: int
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
        
        attacking_fleets = self._get_attacking_fleets(target[0], fleets, player_id)
        incoming_ships = sum(f[5] for f in attacking_fleets)
        
        ships_needed = max(target_ships - incoming_ships + 2, 3)
        
        if target_owner != -1:
            ships_needed += 2
        
        attack_ships = int(min(available_ships * 0.9, ships_needed * 1.3))
        
        if attack_ships < 3:
            attack_ships = min(3, available_ships)
        
        base_score = production * weights["production_weight"]
        
        dist_penalty = adjusted_dist * weights["distance_weight"]
        base_score -= dist_penalty
        
        if target_owner == -1:
            base_score += weights["neutral_bonus"]
        else:
            base_score += weights["enemy_bonus"]
        
        ships_efficiency = (ships_needed / attack_ships) * weights["efficiency_weight"] if attack_ships > 0 else 0
        base_score += ships_efficiency
        
        if dist < 30:
            base_score += weights["close_bonus"]
        elif dist < 45:
            base_score += weights["close_bonus"] * 0.5
        
        if self._is_enemy_attacking(target, fleets, player_id):
            base_score += 20
        
        return max(0, base_score), attack_ships
    
    def _get_attacking_fleets(self, target_id: int, fleets: List, player_id: int) -> List:
        return [f for f in fleets if f[2] == player_id and f[1] == target_id]
    
    def _is_enemy_attacking(self, target: List, fleets: List, player_id: int) -> bool:
        target_id = target[0]
        for fleet in fleets:
            if fleet[2] != player_id and fleet[1] == target_id:
                return True
        return False
    
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
            preferred_angle + 0.05,
            preferred_angle - 0.05,
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
        _agent_instance = AdvancedAgentV12()
    
    return _agent_instance.act(observation)

''')
    
    print("✅ main.py written to output! Ready to submit!")
