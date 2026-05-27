# 给 ChatGPT Deep Research 的提示词

---

## 🎮 Orbit Wars AI 智能体开发 - 全局策略规划

### 📎 Kaggle 竞赛链接
**https://www.kaggle.com/competitions/orbit-wars**

请先访问这个链接，了解：
- 完整的游戏规则
- 评分标准
- 示例代码
- 排行榜信息

---

## 🎯 我们的整体策略演进路径

### 第一阶段：启发式方法 ✅
**目标：** 快速实现基础功能，理解游戏机制
**方法：** 
- 人工设计的评估函数
- 固定规则和阈值
- 简单但有效的启发式
**成果：** v1.1 得分 600

**核心代码（当前最佳）：**
```python
def agent(obs, cfg):
    my_id = obs['player']
    planets = obs['planets']
    fleets = obs.get('fleets', [])
    
    my_planets = [p for p in planets if p[1] == my_id]
    targets = [p for p in planets if p[1] != my_id]
    
    moves = []
    for p in my_planets:
        planet_id, owner, x, y, radius, ships, prod = p
        
        if ships < 5:
            continue
        
        best_target = None
        best_score = -1
        
        for t in targets:
            t_id, t_owner, t_x, t_y, t_r, t_ships, t_prod = t
            
            dist = math.sqrt((t_x - x) ** 2 + (t_y - y) ** 2)
            
            # 评分公式
            score = t_prod * 30 - dist * 0.15
            
            if t_owner == -1:
                score += 50  # 中立星球加分
            
            if score > best_score:
                best_score = score
                best_target = t
        
        if best_target:
            tx, ty = best_target[2], best_target[3]
            angle = math.atan2(ty - y, tx - x)
            
            send_ships = int(min(ships * 0.85, best_target[5] + 10))
            
            if send_ships >= 5:
                moves.append([planet_id, angle, send_ships])
    
    return moves
```

**问题：** 遇到瓶颈，复杂化后反而退步

---

### 第二阶段：优化启发式 ⚠️
**目标：** 在启发式框架内优化
**方法：**
- 参数调优
- 评估函数改进
- 游戏阶段感知
- 敌人行为建模

**当前困境：**
- v1.2 尝试了动态权重、敌人追踪 → 退步
- 不知道边界在哪里

---

### 第三阶段：搜索算法（待开发）
**目标：** 超越简单启发式
**方法：**
- Minimax / Alpha-Beta 搜索
- Monte Carlo Tree Search (MCTS)
- 考虑多步决策

**挑战：**
- 状态空间大
- 实时性要求高

---

### 第四阶段：机器学习（待开发）
**目标：** 从数据中学习最优策略
**方法：**
- **强化学习 (RL)**：PPO, SAC, AlphaZero
- **模仿学习**：从高手对局学习
- **神经进化**：NEAT, ES

**挑战：**
- 需要大量训练
- 训练环境搭建复杂

---

## 📊 当前进度总结

**得分历史：**
- v1.0：287.1 分
- v1.1：600 分（最佳）
- v1.2：越来越低（失败）

**目标：** 900+ 分

---

## 🤔 请你帮助思考的问题

### 1. 启发式优化
- 为什么复杂化后反而退步？
- 启发式的边界在哪里？
- 如何在启发式框架内继续优化？

### 2. 全局策略
- 我们应该继续优化启发式，还是应该转向搜索/ML？
- 如果优化启发式，下一步应该怎么做？
- 如果转向其他方法，应该做什么准备？

### 3. 技术路线
- 启发式 → 搜索 → RL，这样的演进合理吗？
- 有没有更高效的路径？
- 每个阶段的关键技术是什么？

### 4. 资源分配
- 应该投入多少时间在启发式优化上？
- 什么时候应该转向更复杂的方法？
- 如何平衡短期收益和长期提升？

---

## 📋 请提供

1. **全局策略建议**：我们应该走哪条路？
2. **启发式优化方案**：如果继续用启发式，如何改进？
3. **技术路线图**：如果转向其他方法，应该怎么做？
4. **代码实现**：提供可运行的 Python 代码
5. **测试计划**：如何验证效果？

---

## 🎯 最终目标

在 Kaggle Orbit Wars 竞赛中达到 **900+ 分**，并且建立一个可持续迭代的技术体系。

---

感谢你的深度研究！
