"""
Simple test script for Orbit Wars agent.
Tests the agent with kaggle-environments if available.

Contributors: CeaserZhao, PrismScope
"""

import sys
import time

print("=" * 60)
print("ORBIT WARS AGENT TEST")
print("=" * 60)

print("\n1. Testing agent import...")
try:
    from main import agent, get_agent
    print("   ✅ Agent imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import agent: {e}")
    sys.exit(1)

print("\n2. Testing basic agent call...")
try:
    test_obs = {
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
        "initial_planets": [],
    }
    
    result = agent(test_obs, {})
    print(f"   ✅ Agent returned: {result}")
except Exception as e:
    print(f"   ❌ Agent call failed: {e}")
    sys.exit(1)

print("\n3. Testing inference time...")
times = []
for _ in range(100):
    start = time.perf_counter()
    agent(test_obs, {})
    end = time.perf_counter()
    times.append((end - start) * 1000)

avg_time = sum(times) / len(times)
max_time = max(times)
print(f"   Avg: {avg_time:.2f} ms")
print(f"   Max: {max_time:.2f} ms")
if max_time < 1000:
    print("   ✅ Inference time OK (< 1 second)")
else:
    print("   ❌ Inference time too slow")

print("\n4. Testing kaggle-environments...")
try:
    from kaggle_environments import make
    print("   ✅ kaggle-environments available")
    
    print("\n5. Running test game...")
    try:
        env = make("orbit-wars")
        env.run([agent, agent])
        print("   ✅ Game completed successfully")
        
        if hasattr(env, 'render'):
            print("   Note: Use env.render() to visualize")
    except Exception as e:
        print(f"   ⚠️ Game run failed: {e}")
        print("   This might be due to missing dependencies")
        
except ImportError as e:
    print(f"   ⚠️ kaggle-environments not installed: {e}")
    print("   To install: pip install kaggle-environments")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
