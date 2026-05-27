# -*- coding: utf-8 -*-
"""
快速测试 v1.3
"""

import sys
import math
sys.path.insert(0, '.')

# 导入 v1.3
import importlib.util
spec = importlib.util.spec_from_file_location('agent', 'kaggle_notebook_v1.3.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

print("Orbit Wars - v1.3 快速测试")
print("="*60)

# 测试运行
test_obs = {
    'player': 0,
    'planets': [
        [0, 0, 20.0, 20.0, 2.0, 50, 3],
        [1, 1, 80.0, 80.0, 2.0, 30, 2],
        [2, -1, 50.0, 20.0, 1.5, 20, 1],
    ],
    'fleets': [],
    'comet_planet_ids': [],
    'angular_velocity': 0.03,
    'step': 0,
}

moves = mod.agent(test_obs, {})

print("✅ v1.3 测试通过！")
print(f"测试返回: {moves}")
print("")
print("现在可以用 kaggle_notebook_v1.3.py 提交到 Kaggle 了！")
print("")
print("建议步骤:")
print("  1. 打开 Kaggle Orbit Wars 竞赛")
print("  2. 创建新 Notebook")
print("  3. 粘贴 kaggle_notebook_v1.3.py 的内容")
print("  4. 运行 Notebook 生成 main.py")
print("  5. 提交到竞赛")
