"""
Base agent class for Orbit Wars.

Contributors: CeaserZhao, PrismScope
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BaseAgent(ABC):
    """
    Abstract base class for Orbit Wars agents.
    
    All custom agents should inherit from this class and implement
    the `act` method.
    """
    
    def __init__(self, name: str = "BaseAgent"):
        """
        Initialize the agent.
        
        Args:
            name: Agent name
        """
        self.name = name
        self.player_id = None
    
    def setup(self, player_id: int):
        """
        Setup agent with player ID.
        
        Args:
            player_id: Assigned player ID (0-3)
        """
        self.player_id = player_id
    
    @abstractmethod
    def act(self, observation: Dict[str, Any]) -> List[List]:
        """
        Decide actions based on observation.
        
        Args:
            observation: Game state containing:
                - player: Your player ID
                - planets: List of planets
                - fleets: List of fleets
                - angular_velocity: Angular velocity
        
        Returns:
            List of moves [[from_planet_id, angle, num_ships], ...]
        """
        pass
    
    def __call__(self, observation: Dict[str, Any], configuration: Dict[str, Any]) -> List[List]:
        """
        Callable interface for Kaggle environment.
        
        Args:
            observation: Game state
            configuration: Game configuration
        
        Returns:
            List of moves
        """
        if self.player_id is None:
            self.setup(observation["player"])
        return self.act(observation)


class RandomAgent(BaseAgent):
    """
    Random agent that makes random valid moves.
    """
    
    import random
    import math
    
    def __init__(self, name: str = "RandomAgent"):
        super().__init__(name)
    
    def act(self, observation: Dict[str, Any]) -> List[List]:
        """
        Make random moves.
        """
        import random
        import math
        
        player_id = observation["player"]
        planets = observation["planets"]
        
        # Get my planets
        my_planets = [p for p in planets if p[1] == player_id]
        
        moves = []
        for planet in my_planets:
            planet_id = planet[0]
            ships = planet[5]
            
            # Randomly decide to send ships (50% chance)
            if ships > 5 and random.random() < 0.5:
                angle = random.uniform(0, 2 * math.pi)
                num_ships = random.randint(1, ships // 2)
                moves.append([planet_id, angle, num_ships])
        
        return moves


class GreedyAgent(BaseAgent):
    """
    Greedy agent that attacks the nearest enemy/neutral planet.
    """
    
    def __init__(self, name: str = "GreedyAgent", min_ships: int = 10):
        super().__init__(name)
        self.min_ships = min_ships
    
    def act(self, observation: Dict[str, Any]) -> List[List]:
        """
        Attack nearest targets.
        """
        import math
        
        player_id = observation["player"]
        planets = observation["planets"]
        
        my_planets = [p for p in planets if p[1] == player_id]
        enemy_planets = [p for p in planets if p[1] != player_id and p[1] != -1]
        neutral_planets = [p for p in planets if p[1] == -1]
        
        moves = []
        
        for my_planet in my_planets:
            planet_id = my_planet[0]
            x, y = my_planet[2], my_planet[3]
            ships = my_planet[5]
            
            if ships <= self.min_ships:
                continue
            
            # Find nearest target
            target = None
            min_dist = float('inf')
            
            # Prioritize enemies
            for enemy in enemy_planets:
                dist = math.sqrt((enemy[2] - x) ** 2 + (enemy[3] - y) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    target = enemy
            
            # Then neutrals
            if target is None:
                for neutral in neutral_planets:
                    dist = math.sqrt((neutral[2] - x) ** 2 + (neutral[3] - y) ** 2)
                    if dist < min_dist:
                        min_dist = dist
                        target = neutral
            
            if target:
                dx = target[2] - x
                dy = target[3] - y
                angle = math.atan2(dy, dx)
                num_ships = ships // 2
                moves.append([planet_id, angle, num_ships])
        
        return moves
