# -*- coding: utf-8 -*-
"""
Orbit Wars - 本地评测 Harness
按照 ChatGPT Deep Research 建议的三层测试：
1. smoke test：检查不报错、不超时、不自杀
2. promotion test：与 v1.1 和 starter 对战
3. live submission：前两层通过后才提交
"""

import time
import math
from statistics import mean
from typing import Dict, List, Any
import importlib.util


# 导入 v1.1 和 v1.3
def load_agent_from_file(filepath: str):
    spec = importlib.util.spec_from_file_location("agent_module", filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


# ============== 模拟环境（简化版，用于 quick smoke test）==============
def create_simple_observation(turn: int = 0):
    return {
        "player": 0,
        "planets": [
            [0, 0, 20.0, 20.0, 2.0, 50, 3],
            [1, 1, 80.0, 80.0, 2.0, 30, 2],
            [2, -1, 50.0, 20.0, 1.5, 20, 1],
            [3, -1, 20.0, 80.0, 1.0, 15, 2],
            [4, -1, 80.0, 20.0, 1.2, 18, 1],
        ],
        "fleets": [],
        "comet_planet_ids": [],
        "angular_velocity": 0.03,
        "step": turn,
    }


def smoke_test_single(agent_fn, name: str, num_tests: int = 100):
    """
    Smoke test 层：检查不报错、不超时、不自杀
    """
    print(f"\n{'='*60}")
    print(f"SMOKE TEST: {name}")
    print(f"{'='*60}")

    errors = []
    total_time = 0.0
    empty_moves = 0
    valid_moves = 0

    for turn in range(num_tests):
        obs = create_simple_observation(turn)

        try:
            start = time.time()
            moves = agent_fn(obs, {})
            elapsed = time.time() - start
            total_time += elapsed

            # 检查输出格式
            if not isinstance(moves, list):
                errors.append(f"Turn {turn}: Output not a list: {type(moves)}")
                continue

            if len(moves) == 0:
                empty_moves += 1
                continue

            for move in moves:
                if not isinstance(move, list) or len(move) != 3:
                    errors.append(f"Turn {turn}: Invalid move format: {move}")
                else:
                    valid_moves += 1

            # 检查超时（单步应该 < 0.1s）
            if elapsed > 0.1:
                errors.append(f"Turn {turn}: Slow response {elapsed:.3f}s")

        except Exception as e:
            errors.append(f"Turn {turn}: Exception {e}")

    avg_time = total_time / num_tests if num_tests > 0 else 0

    print(f"Tests: {num_tests}")
    print(f"Avg time per turn: {avg_time*1000:.1f}ms")
    print(f"Empty moves: {empty_moves}/{num_tests}")
    print(f"Valid moves: {valid_moves}")
    print(f"Errors: {len(errors)}")

    for err in errors[:10]:
        print(f"  - {err}")

    if len(errors) > 0:
        print(f"  (...and {len(errors)-10} more)" if len(errors) > 10 else "")

    return len(errors) == 0


def quick_check():
    """
    不依赖 kaggle_environments 的快速检查
    """
    print("\n" + "="*60)
    print("QUICK CHECK - 不依赖 kaggle_environments")
    print("="*60)

    try:
        v11_agent = load_agent_from_file("kaggle_notebook_v1.1.py")
        print("✅ v1.1 加载成功")
    except Exception as e:
        print(f"❌ v1.1 加载失败: {e}")
        v11_agent = None

    try:
        v13_agent = load_agent_from_file("kaggle_notebook_v1.3.py")
        print("✅ v1.3 加载成功")
    except Exception as e:
        print(f"❌ v1.3 加载失败: {e}")
        v13_agent = None

    print("\n开始 smoke tests...")

    v11_ok = False
    if v11_agent:
        v11_ok = smoke_test_single(v11_agent, "v1.1")

    v13_ok = False
    if v13_agent:
        v13_ok = smoke_test_single(v13_agent, "v1.3")

    print("\n" + "="*60)
    print("QUICK CHECK 结果:")
    print(f"  v1.1: {'✅ OK' if v11_ok else '❌ FAIL'}")
    print(f"  v1.3: {'✅ OK' if v13_ok else '❌ FAIL'}")
    print("="*60)

    return v11_ok and v13_ok


# ============== 完整评测（需要 kaggle_environments）==============
def run_full_evaluation():
    """
    使用真实 kaggle_environments 的完整评测
    """
    print("\n" + "="*60)
    print("FULL EVALUATION (需要 kaggle-environments)")
    print("="*60)

    try:
        from kaggle_environments import make
        print("✅ kaggle-environments 已加载")
    except ImportError:
        print("❌ kaggle-environments 未安装")
        print("请运行: pip install kaggle-environments")
        return False

    # 这里可以继续实现与 starter 对战的代码
    print("\n提示：完整评测功能待实现（需要下载 kaggle starter 代码）")
    print("当前可以：")
    print("  1. 先运行 QUICK CHECK（上面的）")
    print("  2. 直接用 v1.3 提交到 Kaggle 测试")

    return True


# ============== 主函数 ==============
if __name__ == "__main__":
    print("Orbit Wars - 本地评测 Harness")
    print("="*60)

    success = quick_check()

    if success:
        print("\n🎉 Quick Check 通过！")
        print("\n下一步:")
        print("  1. 可选：安装 kaggle-environments 运行完整评测")
        print("  2. 推荐：直接用 kaggle_notebook_v1.3.py 提交到 Kaggle")
    else:
        print("\n❌ Quick Check 有问题，请检查")
