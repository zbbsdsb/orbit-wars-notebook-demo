"""
Visualization tools for Orbit Wars.

Provides game state visualization, fleet trajectory plotting, and score tracking.

Contributors: CeaserZhao, PrismScope
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Any, Optional
import numpy as np


class GameVisualizer:
    """
    Visualize Orbit Wars game states.
    
    Features:
    - Planet positions and ownership
    - Fleet trajectories
    - Sun and game boundaries
    """

    def __init__(self, figsize=(10, 10)):
        self.figsize = figsize
        self.fig, self.ax = None, None

    def _init_plot(self):
        """Initialize plot canvas."""
        self.fig, self.ax = plt.subplots(figsize=self.figsize)
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_title('Orbit Wars Game State')

    def visualize_state(
        self,
        observation: Dict[str, Any],
        save_path: Optional[str] = None,
        show: bool = True
    ):
        """
        Visualize a single game state.
        
        Args:
            observation: Game state observation
            save_path: Path to save figure
            show: Show plot
        """
        if self.fig is None:
            self._init_plot()
        
        self.ax.clear()
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        
        sun = patches.Circle((50, 50), 10, color='gold', alpha=0.5)
        self.ax.add_patch(sun)
        self.ax.text(50, 50, 'SUN', ha='center', va='center')
        
        planets = observation.get('planets', [])
        for planet in planets:
            planet_id, owner, x, y, radius, ships, production = planet
            
            color = self._get_owner_color(owner)
            circle = patches.Circle((x, y), radius, color=color, alpha=0.7)
            self.ax.add_patch(circle)
            
            label = f"P{planet_id}\nS:{ships}\nP:{production}"
            self.ax.text(x, y, label, ha='center', va='center', fontsize=8)
        
        fleets = observation.get('fleets', [])
        for fleet in fleets:
            fleet_id, owner, x, y, angle, from_id, ships = fleet
            
            color = self._get_owner_color(owner)
            self.ax.plot(x, y, 'o', color=color, markersize=6)
            
            dx = 3 * np.cos(angle)
            dy = 3 * np.sin(angle)
            self.ax.arrow(x, y, dx, dy, head_width=1, color=color, alpha=0.8)
        
        if save_path:
            self.fig.savefig(save_path, dpi=100, bbox_inches='tight')
        
        if show:
            self.fig.show()

    def _get_owner_color(self, owner: int) -> str:
        """Get color for owner ID."""
        colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red']
        if owner == -1:
            return 'tab:gray'
        return colors[owner % len(colors)]

    def visualize_trajectory(
        self,
        observations: List[Dict[str, Any]],
        player_id: int = 0,
        save_path: Optional[str] = None,
        show: bool = True
    ):
        """
        Visualize trajectory of player's score over time.
        
        Args:
            observations: List of observations from game
            player_id: Player to track
            save_path: Path to save figure
            show: Show plot
        """
        scores = []
        for obs in observations:
            score = self._calculate_score(obs, player_id)
            scores.append(score)
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(scores, label=f'Player {player_id}')
        ax.set_xlabel('Turn')
        ax.set_ylabel('Score')
        ax.set_title('Score Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if save_path:
            fig.savefig(save_path, dpi=100, bbox_inches='tight')
        
        if show:
            fig.show()

    def _calculate_score(self, obs: Dict[str, Any], player_id: int) -> float:
        """Calculate score from observation."""
        planets = obs.get('planets', [])
        fleets = obs.get('fleets', [])
        
        planet_score = sum(p[5] for p in planets if p[1] == player_id)
        fleet_score = sum(f[6] for f in fleets if f[1] == player_id)
        
        return planet_score + fleet_score


def quick_visualize(observation: Dict[str, Any]):
    """Quickly visualize a single observation."""
    viz = GameVisualizer()
    viz.visualize_state(observation, save_path=None, show=True)


if __name__ == "__main__":
    print("GameVisualizer module loaded")
    print("Usage:")
    print("  from src.utils.visualization import GameVisualizer")
    print("  viz = GameVisualizer()")
    print("  viz.visualize_state(observation)")
