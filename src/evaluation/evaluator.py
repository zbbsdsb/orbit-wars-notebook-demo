"""
Agent evaluation framework for Orbit Wars.

Provides tournament functionality, benchmark tests, and performance statistics.

Contributors: CeaserZhao, PrismScope
"""

import time
import random
from typing import Dict, List, Any, Callable, Tuple
from collections import defaultdict


class AgentEvaluator:
    """
    Evaluate agent performance against baselines.
    
    Features:
    - Multi-game tournaments
    - Win rate and score statistics
    - Performance benchmarking
    """

    def __init__(self, env_name: str = "orbit-wars"):
        """
        Initialize evaluator.
        
        Args:
            env_name: Name of the Kaggle environment
        """
        self.env_name = env_name
        self.results = defaultdict(list)

    def evaluate(self, agent, opponents, num_games=100, verbose=False):
        """
        Run agent against opponents and return statistics.
        
        Args:
            agent: The agent function to evaluate
            opponents: List of opponent agent functions
            num_games: Number of games to run per opponent
            verbose: Print progress updates
        
        Returns:
            Dictionary with win rate, average score, and detailed statistics
        """
        all_results = {
            "win_rate": {},
            "avg_score": {},
            "detailed": {},
            "overall": {
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "avg_score": 0,
                "games_played": 0
            }
        }

        for idx, opponent in enumerate(opponents):
            if verbose:
                print(f"Evaluating vs opponent {idx + 1}/{len(opponents)}...")
            
            wins, losses, draws, scores = self._run_tournament(
                agent, opponent, num_games, verbose
            )
            
            win_rate = wins / num_games if num_games > 0 else 0
            avg_score = sum(scores) / len(scores) if scores else 0
            
            key = f"opponent_{idx}"
            all_results["win_rate"][key] = win_rate
            all_results["avg_score"][key] = avg_score
            all_results["detailed"][key] = {
                "wins": wins,
                "losses": losses,
                "draws": draws,
                "scores": scores,
                "avg_score": avg_score,
                "win_rate": win_rate
            }
            
            all_results["overall"]["wins"] += wins
            all_results["overall"]["losses"] += losses
            all_results["overall"]["draws"] += draws
            all_results["overall"]["avg_score"] += sum(scores)
            all_results["overall"]["games_played"] += num_games

        if all_results["overall"]["games_played"] > 0:
            all_results["overall"]["avg_score"] /= all_results["overall"]["games_played"]

        return all_results

    def _run_tournament(
        self,
        agent1: Callable,
        agent2: Callable,
        num_games: int,
        verbose: bool
    ) -> Tuple[int, int, int, List[float]]:
        """
        Run a tournament between two agents.
        
        Args:
            agent1: First agent
            agent2: Second agent
            num_games: Number of games
            verbose: Print progress
        
        Returns:
            (wins, losses, draws, scores) for agent1
        """
        wins = 0
        losses = 0
        draws = 0
        scores = []

        try:
            from kaggle_environments import make
            env = make(self.env_name)
        except ImportError:
            if verbose:
                print("kaggle_environments not installed, running mock evaluation")
            return self._run_mock_tournament(agent1, num_games)

        for i in range(num_games):
            if verbose and (i + 1) % 10 == 0:
                print(f"  Game {i + 1}/{num_games}")

            env.reset()
            result = env.run([agent1, agent2])
            
            final_state = result[-1]
            scores1 = final_state[0].get("observation", {}).get("score", 0)
            scores2 = final_state[1].get("observation", {}).get("score", 0)
            
            scores.append(scores1)
            
            if scores1 > scores2:
                wins += 1
            elif scores1 < scores2:
                losses += 1
            else:
                draws += 1

        return wins, losses, draws, scores

    def _run_mock_tournament(
        self,
        agent: Callable,
        num_games: int
    ) -> Tuple[int, int, int, List[float]]:
        """
        Run mock tournament for testing when kaggle_environments is unavailable.
        
        Args:
            agent: Agent to test
            num_games: Number of mock games
        
        Returns:
            (wins, losses, draws, scores)
        """
        wins = 0
        losses = 0
        draws = 0
        scores = []

        for _ in range(num_games):
            test_obs = self._generate_mock_observation()
            moves = agent(test_obs, {})
            
            valid_moves = self._validate_moves(moves)
            
            score = self._calculate_mock_score(moves, valid_moves)
            scores.append(score)
            
            if score > 600:
                wins += 1
            elif score > 500:
                draws += 1
            else:
                losses += 1

        return wins, losses, draws, scores

    def _generate_mock_observation(self) -> Dict[str, Any]:
        """Generate a mock observation for testing."""
        return {
            "player": 0,
            "planets": [
                [0, 0, 20.0, 20.0, 2.0, 50, 3],
                [1, 1, 80.0, 80.0, 2.0, 30, 2],
                [2, -1, 50.0, 20.0, 1.5, 20, 1],
                [3, 0, 30.0, 70.0, 2.2, 40, 4],
                [4, 1, 70.0, 30.0, 1.8, 25, 2],
            ],
            "fleets": [],
            "angular_velocity": 0.03,
            "comet_planet_ids": [],
            "comets": [],
            "initial_planets": [
                [0, 0, 20.0, 20.0, 2.0, 50, 3],
                [1, 1, 80.0, 80.0, 2.0, 30, 2],
                [2, -1, 50.0, 20.0, 1.5, 20, 1],
                [3, 0, 30.0, 70.0, 2.2, 40, 4],
                [4, 1, 70.0, 30.0, 1.8, 25, 2],
            ],
        }

    def _validate_moves(self, moves: List) -> bool:
        """Validate move format."""
        if not isinstance(moves, list):
            return False
        
        for move in moves:
            if not isinstance(move, list) or len(move) != 3:
                return False
            if not isinstance(move[0], (int, float)):
                return False
            if not isinstance(move[1], (int, float)):
                return False
            if not isinstance(move[2], (int, float)):
                return False
        
        return True

    def _calculate_mock_score(self, moves: List, valid: bool) -> float:
        """Calculate mock score based on move quality."""
        if not valid:
            return 400
        
        score = 500
        
        for move in moves:
            planet_id, angle, num_ships = move
            
            if num_ships >= 10:
                score += 20
            if 0 <= angle <= 6.28:
                score += 10
            if planet_id in [0, 1, 2, 3, 4]:
                score += 15
        
        return min(1000, score + random.randint(-50, 50))

    def benchmark(self, agent: Callable, verbose: bool = True) -> Dict[str, Any]:
        """
        Run standard benchmark suite.
        
        Args:
            agent: Agent to benchmark
            verbose: Print results
        
        Returns:
            Benchmark results
        """
        from src.agents.base_agent import RandomAgent, GreedyAgent
        
        random_agent = RandomAgent()
        greedy_agent = GreedyAgent()
        
        random_opponent = lambda obs, config: random_agent(obs, config)
        greedy_opponent = lambda obs, config: greedy_agent(obs, config)
        
        if verbose:
            print("Running benchmark against Random Agent...")
        
        random_results = self.evaluate(agent, [random_opponent], num_games=100, verbose=verbose)
        
        if verbose:
            print("\nRunning benchmark against Greedy Agent...")
        
        greedy_results = self.evaluate(agent, [greedy_opponent], num_games=100, verbose=verbose)

        summary = {
            "random_agent": {
                "win_rate": random_results["win_rate"]["opponent_0"],
                "avg_score": random_results["avg_score"]["opponent_0"],
                "details": random_results["detailed"]["opponent_0"]
            },
            "greedy_agent": {
                "win_rate": greedy_results["win_rate"]["opponent_0"],
                "avg_score": greedy_results["avg_score"]["opponent_0"],
                "details": greedy_results["detailed"]["opponent_0"]
            }
        }

        if verbose:
            self._print_summary(summary)

        return summary

    def _print_summary(self, summary: Dict[str, Any]):
        """Print benchmark summary."""
        print("\n" + "=" * 60)
        print("BENCHMARK SUMMARY")
        print("=" * 60)
        print(f"Random Agent:")
        print(f"  Win Rate: {summary['random_agent']['win_rate']:.2%}")
        print(f"  Avg Score: {summary['random_agent']['avg_score']:.1f}")
        print(f"\nGreedy Agent:")
        print(f"  Win Rate: {summary['greedy_agent']['win_rate']:.2%}")
        print(f"  Avg Score: {summary['greedy_agent']['avg_score']:.1f}")
        print("=" * 60)

    def measure_inference_time(
        self,
        agent: Callable,
        num_samples: int = 1000
    ) -> Dict[str, float]:
        """
        Measure agent inference time.
        
        Args:
            agent: Agent to test
            num_samples: Number of measurements
        
        Returns:
            Dictionary with min, max, avg, and std dev times
        """
        times = []
        
        for _ in range(num_samples):
            obs = self._generate_mock_observation()
            
            start = time.perf_counter()
            agent(obs, {})
            end = time.perf_counter()
            
            times.append(end - start)

        times.sort()
        
        return {
            "min": times[0] * 1000,
            "max": times[-1] * 1000,
            "avg": sum(times) / len(times) * 1000,
            "p50": times[len(times) // 2] * 1000,
            "p95": times[int(len(times) * 0.95)] * 1000,
            "p99": times[int(len(times) * 0.99)] * 1000,
            "samples": num_samples
        }


def run_benchmark(agent_func: Callable = None):
    """
    Run benchmark on the default agent.
    
    Args:
        agent_func: Agent function to benchmark (default: main agent)
    """
    if agent_func is None:
        from main import agent as main_agent
        agent_func = main_agent
    
    evaluator = AgentEvaluator()
    
    print("=" * 60)
    print("ORBIT WARS AGENT BENCHMARK")
    print("=" * 60)
    
    print("\n1. Measuring inference time...")
    time_results = evaluator.measure_inference_time(agent_func, num_samples=100)
    print(f"   Avg time: {time_results['avg']:.2f} ms")
    print(f"   P95 time: {time_results['p95']:.2f} ms")
    print(f"   Max time: {time_results['max']:.2f} ms")
    
    print("\n2. Running benchmark tournaments...")
    results = evaluator.benchmark(agent_func, verbose=True)
    
    return {
        "inference_time": time_results,
        "benchmark": results
    }


if __name__ == "__main__":
    run_benchmark()
