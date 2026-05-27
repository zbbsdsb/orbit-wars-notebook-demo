# Orbit Wars AI 智能体开发全局策略规划

## 比赛规则与当前竞赛面貌

我先把能从官方页面、官方开源引擎和公开竞赛资料里确认的事实压缩成一个可直接用于研发决策的版本。Orbit Wars 的官方目标是让参赛者“创建和/或训练 AI bots”，去参加一个新型的多智能体对战环境；比赛既支持 1v1，也支持 4 人 free-for-all。官方玩法描述明确写到：棋盘是连续二维空间，行星绕太阳旋转，彗星沿椭圆轨道穿越棋盘，舰队沿直线飞行；整局持续 500 回合，结束时总舰船数最多的玩家获胜。citeturn6search0turn23search0turn13view0

官方开源环境把这些机制写得很具体。`orbit_wars.json` 定义了环境只支持 2 或 4 个 agents，`episodeSteps=500`，`actTimeout=1`，`remainingOverageTime=60`，默认 `shipSpeed=6.0`，`cometSpeed=4.0`；动作格式是一个 move 列表，每个 move 为 `[from_planet_id, direction_angle, num_ships]`；观测里直接暴露 `planets`、`fleets`、`player`、`angular_velocity`、`initial_planets`、`next_fleet_id`、`comets`、`comet_planet_ids` 等字段。citeturn22view0

官方引擎源码还给出了很多对策略很关键、但仅靠比赛简介不容易意识到的细节。地图是四重旋转对称生成的；Q1 象限会随机生成 5–10 组星球，再旋转得到全图；外圈至少有 3 组静态星球；中央太阳半径是 10；彗星会在第 50、150、250、350、450 回合生成；2 人对局时，系统会从一个对称组里挑两个家园星球，双方初始各有 10 艘船。citeturn11view0turn12view3

结算顺序同样非常重要。官方源码显示：每回合先处理发舰，再做已占领星球生产，然后按“舰队与移动中的星球的连续碰撞检测”推进舰队；舰队速度不是常数，而是随舰船数量按对数规律增长，最多接近 `shipSpeed` 的上限；路径穿过太阳会直接损失舰队；到达行星后的战斗不是简单“到达就占领”，而是先汇总每个玩家本回合冲到该星球的舰船数，再用第一名减第二名得到幸存兵力，幸存者要么加到己方星球上，要么去打穿守军后完成占领。终盘 reward 在环境层面只是 `+1/-1`，但胜负依据是“行星里的船 + 飞行中的船”的总和。citeturn12view8turn12view12turn12view14turn13view0turn13view1

示例代码方面，官方开源环境里已经内置了 `random` 和 `starter` 两个基线 agent。`random` 的行为很简单，对己方星球随机找角度发出半数兵力；`starter` 会优先寻找“静态且非己方”的最近星球，然后在本星球船数至少 20 时发出一半兵力。Kaggle 官方页面也说明了，写 bot 和提交所需的入门说明都放在 starter kit 里。citeturn13view0turn32search0

排行榜信息上，Kaggle 的 leaderboard 页面在当前抓取环境里没能直接展开到可读的行级别数据，所以我不能假装自己拿到了“官方实时前十列表”。但公开 notebook 与讨论快照已经足够说明当前分数带：有公开 notebook 报到 919.0 的 structured baseline、1003.7 的 public score、1018.4 的 best score、1039.2 的 launch-safety heuristic，另一个公开 notebook 标题直接写“1049.2+ Highest Public”，还有公开 notebook 的历史 best 到了 1060.2。与此同时，竞赛讨论里有人把约 590 分对应到约 rank 1049，也有人把约 1161 分对应到接近 rank 68。对你来说，这意味着“900+”不是幻想区，而是已经被公开作品反复证明可达的竞争区间。citeturn34search5turn34search0turn34search4turn24search8turn14search0turn34search1turn31search2turn21search1

评分标准也要分两层理解。环境层面的单局 reward 是终局 `+1/-1`；但竞赛层面的 Kaggle 榜单分是一个持续验证后的 rating 风格分数，而不是单局平均 reward。公开讨论明确提到：每个参赛者可以有 2 个 active agents，榜单显示的是这两个 agent 中更高的那个 rating；新提交会让上一份失活。另一个讨论则说明，分数在少量 validation games 后可能先冲高，再随着更多验证局数回落。你后面所有“版本是否真的进步”的判断，都必须在这个 rating 噪声背景下进行。citeturn13view1turn33search0turn33search1

## 对你当前启发式的诊断

你现在的 v1.1 代码，本质上是“当前时刻的目标打分 + 单步贪心发舰”。它能拿到 301 的原因很简单：它已经抓住了三个最基础的收益源——扩张、中立优先、生产优先——因此在非常弱的起点上，肯定能迅速超过 random / 极简 bot。问题在于，它没有显式建模 Orbit Wars 里真正决定上限的那几个高杠杆机制：旋转目标的拦截几何、路径穿太阳的安全性、发舰量影响 ETA，进而影响目标到达时守军和生产。官方环境恰恰把这些机制放在了结算核心位置。citeturn22view0turn12view8turn12view12turn12view14

换句话说，我认为你的 v1.1 不是“启发式太简单”，而是“启发式的状态表征太浅”。你现在对目标的估值只用了 `t_prod、dist、neutral bonus`，但真实世界里至少还应该有：到达时守军、是否需要拦截而不是直瞄、路径是否穿太阳、出兵后源星是否会裸露、目标拿下后能否守住、以及这次发舰是否只是帮第三方做嫁衣。官方引擎又是连续空间、同时行动、多玩家博弈，所以一旦这些因素没入模，靠调几个权重通常只会让模型“更自信地犯错”。citeturn23search0turn12view12turn12view14turn31search0

公开社区信号其实已经很好地说明了启发式的真正边界。讨论里有人明确说，“只靠 trajectory calculations 再加一些处理，就可以上到 1000 rating”；最近还有把“launch safety”直接写进标题的 1039.2 notebook，以及 919.0 的 structured baseline。它们传达的核心不是“启发式无用”，而是“静态打分启发式很弱，但带几何前瞻和任务结构的启发式很强”。所以你当前的瓶颈，并不是你已经碰到了启发式天花板；你碰到的是“没有前向几何和任务编排的启发式天花板”。citeturn31search1turn24search8turn34search5

你 v1.2 “复杂化后退步”的另一个原因，很可能是评测噪声与过拟合。公开讨论显示，Orbit Wars 的 live score 会在很少的 validation games 后出现明显跳涨，然后随着更多比赛回落；另一条讨论则直说评测很贵，大约 20–30 秒一局，可用预算通常只是几百到几千局，而不是百万级暴力调参。这种条件下，如果你没有稳定的本地 harness，就很容易把“live 分上下波动”误判成“策略真的进步/退步”，或者把一版碰巧吃到好对局分布的 bot 错当成新最佳。citeturn33search1turn33search2

你当前的发舰规则也偏激进。`send_ships = min(ships * 0.85, target_ships + 10)` 这种模式，对 4P 尤其危险，因为它隐含地假设“只要拿下一个星球就是赚”。但公开复盘已经指出，在 4 人局里，高度争夺的星球会把交战双方都打残，最后占领者常常只剩下一个脆弱驻军；这时你如果没有留守约束和后续增援，扩张会迅速变成暴露。即使在 2P，过高发舰比例也会让你失去连续进攻和防反弹性。citeturn31search0

## 我建议的全局路线

我的结论很明确：**短期主线应该继续做启发式，但必须升级为“结构化启发式 + 轻量前向模拟”**；**中期再接宏动作搜索**；**机器学习与自博弈环境要并行铺设，但不应立刻成为主线**。原因不是保守，而是现有公开证据已经表明，915–1040+ 的区间并不要求先做重型 RL；相反，先把几何、任务、风控和局部 rollout 做出来，才是从 301 冲到 900+ 的最短路径。citeturn34search5turn24search8turn14search0turn34search0

我不建议你现在就把主要精力投到 vanilla minimax / alpha-beta。Orbit Wars 官方环境本身就支持 2P 和 4P，动作又是连续角度的 move 列表，不是经典的离散、交替行动、二人零和棋类。学术上，UCT 直接套进 simultaneous-move games 并不保证一般性收敛到 Nash equilibrium；RTS 里的 UCT 成功案例，历史上也更多集中在“局部战术突击规划”这类裁剪后的子问题，而不是整张大图、全动作空间的裸搜索。把大量时间押在“把 minimax 做出来”上，ROI 往往不高。citeturn22view0turn29search2turn29search7turn26search18

如果把资源分配说得更具体一些，我会建议你接下来一段时间这样投放。短期大约六到七成时间用来做 heuristic-hybrid 主线：截击几何、太阳安全、ETA 守军估计、留守规则、任务级排序、后排增援、浅层 rollout。两到三成时间用来做数据与实验基础设施：版本固定、本地模拟器、回放采集、指标看板。最后留一小部分时间做 RL/IL 预研，比如把 replay 数据读通、做一个行为克隆原型，但先不要把最终目标设为“训练出端到端 PPO agent”。这部分是我的工程建议，不是硬性比赛规则，但它最符合目前已知证据。citeturn33search2turn27search3turn35search0

因此，我给你的技术演进路径会做一个重要修正：**不是“启发式 → 搜索 → RL”这样线性切换，而是“启发式 → 结构化启发式 + rollout → 宏动作搜索 → 模仿学习/策略先验 → 自博弈 RL”**。也就是说，搜索和学习都应该建立在你已经有一个“会提出好任务候选”的策略骨架上，而不是从零开始替代它。这个路径比“先把启发式调到死，再完全推倒重来”更高效，也更符合近年复杂博弈 AI 的常见做法。citeturn25search1turn25search2turn25search3turn25search6

## 启发式升级方案

如果你选择继续走启发式主线，我建议你不要再围绕“分数公式再加几个项”打转，而是直接把 v1.x 升级成一个**任务驱动的结构化 agent**。最先要补上的，是**几何层**。你需要显式判断目标是静态星球还是旋转星球；对旋转目标求一个离散 intercept，而不是对当前坐标发射；对每次候选发舰做太阳穿越检测；对 ETA 期间目标守军增长做估计。官方机制里，舰队速度会随发舰规模改变，而已占领星球会持续生产，所以“发多少”和“多久到”必须一起求，而不能先盲目发，再希望打分函数替你兜底。citeturn22view0turn12view8turn12view12turn12view14

第二个要补的是**任务层**。当前代码是“每个己方星球各自挑一个看起来最值的目标”，这会天然导致整体上的重复占领、过度进攻以及源星裸露。我建议把任务至少拆成四类：安全扩张、低防 exposed-planet snipe、后排向前线增援、以及不行动保留兵力。然后把这些任务放进一个全局候选池，按统一的 mission score 排序，再做“一个源星最多接一个任务、一个脆弱目标不要被己方多路重复投资”的分配。公开社区已经出现了 “structured baseline”“forward sim”“timeline simulation”“launch-safety heuristic” 这些命名，说明高分做法普遍已经不是简单 per-planet greedy，而是任务化编排。citeturn34search5turn24search0turn14search22turn24search8

第三个要补的是**经济层与风控层**。真正有用的启发式不该再问“这个目标分高不高”，而该问“这次任务的净现值高不高”。一个更合理的 mission score，应该至少同时包含：目标生产、预计 ETA、到达时需要的兵力、出兵后的源星剩余、目标拿下后是否容易守住、以及失败时的损失。你的 v1.1 里对中立星球一律加 50 分，这样太粗。早期中立通常很香，但到中后期，很多“便宜中立扩张”会输给“低守军敌星球狙击”或者“兵力集中到关键前线”。终盘又必须切回“最大化总船数”逻辑，因为官方胜负依据是行星与舰队的总船数，而不是单纯版图面积。citeturn23search0turn13view1turn31search0

第四个要补的是**阶段感知，但要用结构变化，不是纯权重变化**。与你 v1.2 失败的经验相反，阶段感知本身不是错，问题是如果你只是给同一个静态分数公式换一组 early/mid/late weights，信息量仍然不够。我更建议用“允许的任务集合变化”来表达阶段：前期主打安全中立与外圈静态星球；中期开始加 exposed enemy snipes 与前线 reinforcement；后期减少低 ROI 扩张，转向保总船数、收割低守军和防守稳态。这种分层比“前期 neutral_bonus=70，后期 neutral_bonus=20”更不容易漂。citeturn31search1turn24search8turn31search0

第五个要补的是**指标化调试**。你下一版不该只输出 Kaggle score，还必须同时记录：发舰总数、太阳/越界损失率、截击成功率、任务类型分布、每次任务投入兵力与拿下星球产能的比值、每个源星的留守下界是否被破坏、2P 与 4P 的表现是否分叉。Orbit Wars 的 live rating 会飘，如果你没有过程指标，后面每次退步都很难定位到底是几何错、经济错，还是对局分布噪声。citeturn33search1turn33search2

## 搜索与机器学习路线

如果你之后要转向搜索，我建议你做的是**宏动作搜索**，而不是原子动作搜索。具体来说，先让启发式生成每个源星的少量高质量任务候选，例如“以某个兵力档位拦截某个旋转目标”“对某个敌方 exposed 星球发起一次 snipe”“向某个前线星球增援”；然后把这些候选当作搜索节点的动作空间，再做 4–8 回合 horizon 的 beam search、rolling-horizon 或者 progressive-widening MCTS。连续动作空间里，MCTS 通常需要 progressive widening 才实用；而 RTS 里 UCT 的经典成功案例本身也是在动作空间被大幅裁剪后的战术子问题上取得的。citeturn29search0turn29search6turn26search18

这也解释了为什么我不把 minimax 放在路线图前面。Orbit Wars 不是国际象棋；它更像一个同时行动、连续空间、多方博弈、有限时预算下的在线规划问题。相较于全局 minimax，更高 ROI 的做法是“用启发式产生好候选，再对候选做短视界 lookahead”。你真正要搜索的不是所有可能角度，而是“哪些任务组合在接下来若干回合里，能让我的总船数和版图结构变得更好”。这是一种更符合比赛形态的 planner 设计。citeturn22view0turn29search2turn29search12

机器学习方面，最现实的切入点不是直接 PPO，而是**先做 replay 驱动的模仿学习 / 策略先验**。Orbit Wars 社区已经有每天的 replay datasets、一个“3,000+ games ready to analyze in seconds”的 parquet 数据集，以及 episode scraper downloader，明确点名可用于 imitation learning workflows。这意味着你完全可以先把公开回放转成“状态 → 任务类型/目标选择/发舰规模”的监督学习样本，用一个轻量模型学出 target prior 或 action prior，再把它接回你的任务生成器和搜索器里。citeturn27search2turn27search3turn27search1

如果再往前走，PPO 确实是实现复杂度、样本效率和工程可控性之间比较平衡的强化学习基线；而 AlphaStar、OpenAI Five 这些结果也证明了自博弈 RL 在复杂 RTS / MOBA 上的最终上限非常高。但这些成功案例的共同点，是模仿预热、大规模并行环境、自博弈分布设计和长时间算力投入，而不是“简单把环境包一层 PPO 就自然起飞”。因此，对 Orbit Wars 更合理的长期路线是：先把 replay 数据、行为克隆、任务先验和轻量搜索做起来，再考虑自博弈 PPO；如果未来你真要试 AlphaZero-like 路线，也应该是“任务级策略网络 + 宏动作 MCTS”，而不是直接在连续角度原子动作上裸跑。citeturn25search1turn25search2turn25search3turn25search6turn25search12

还有一个很现实的工程提醒。2026 年 4 月 22 日的竞赛讨论里，有参赛者明确报告 Orbit Wars 评测环境没有预装 PyTorch。这个信息可能后来发生过变化，所以我不会把它当成永恒真理；但它足以说明，你在真正把 torch 依赖写进提交物之前，必须先验证当前 runtime，而不能假设“本地能跑，Kaggle 评测就一定能跑”。citeturn28search0

## 可运行代码与测试计划

下面这份代码，我把它定位成你可以立刻替换 v1.1 的 **v1.3 结构化启发式基线**。它没有上重搜索，但有意把目前最确定的高杠杆因素补齐了：旋转星球的离散 intercept、太阳安全过滤、ETA 守军估计、源星留守、以及后排对前线的增援。这个方向与官方结算机制，也与最近公开的 919–1039+ 结构化/安全型启发式实践是一致的。citeturn22view0turn12view12turn12view14turn24search8turn34search5

```python
import math

BOARD_SIZE = 100.0
CENTER = BOARD_SIZE / 2.0
SUN_RADIUS = 10.0
ROTATION_RADIUS_LIMIT = 50.0
DEFAULT_MAX_SPEED = 6.0


def _cfg_get(cfg, key, default=None):
    if isinstance(cfg, dict):
        return cfg.get(key, default)
    return getattr(cfg, key, default)


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _point_to_segment_distance(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    abx = bx - ax
    aby = by - ay
    apx = px - ax
    apy = py - ay
    ab2 = abx * abx + aby * aby
    if ab2 <= 1e-12:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, (apx * abx + apy * aby) / ab2))
    qx = ax + t * abx
    qy = ay + t * aby
    return math.hypot(px - qx, py - qy)


def _fleet_speed(ships, max_speed):
    ships = max(1, int(ships))
    if ships <= 1:
        return 1.0
    x = math.log(ships) / math.log(1000)
    x = max(0.0, min(1.0, x))
    return min(max_speed, 1.0 + (max_speed - 1.0) * (x ** 1.5))


def _orbital_radius(planet):
    return math.hypot(planet[2] - CENTER, planet[3] - CENTER)


def _is_rotating(planet, comet_ids):
    if planet[0] in comet_ids:
        return False
    return _orbital_radius(planet) + planet[4] < ROTATION_RADIUS_LIMIT


def _future_pos(planet, dt, angular_velocity, comet_ids):
    if not _is_rotating(planet, comet_ids):
        return (planet[2], planet[3])
    r = _orbital_radius(planet)
    ang = math.atan2(planet[3] - CENTER, planet[2] - CENTER) + angular_velocity * dt
    return (CENTER + r * math.cos(ang), CENTER + r * math.sin(ang))


def _nearest_enemy_distance(src, enemy_planets):
    if not enemy_planets:
        return 999.0
    s = (src[2], src[3])
    return min(_dist(s, (e[2], e[3])) for e in enemy_planets)


def _reserve_ships(src, enemy_planets, turn):
    prod = int(src[6])
    nearest_enemy = _nearest_enemy_distance(src, enemy_planets)

    # 基础留守：至少保留一部分驻军，不再像 v1.1 那样 85% 一把梭。
    reserve = 6 + prod * 2

    # 前期更重视连续扩张能力与防止被反扑。
    if turn < 140:
        reserve += 2

    # 靠近敌方时提高留守。
    if nearest_enemy < 26:
        reserve += 8
    elif nearest_enemy < 38:
        reserve += 4

    return min(int(src[5]) - 1, max(0, reserve))


def _target_value(target, turn, comet_ids):
    owner = target[1]
    prod = target[6]

    # 生产值始终重要
    val = 24.0 * prod

    # 前期偏好中立扩张，中后期提高打敌方薄弱星球的权重
    if owner == -1:
        val += 18.0 if turn < 140 else 8.0
    else:
        val += 14.0 if turn > 120 else 4.0

    # 静态星球更容易稳定命中与守住
    if not _is_rotating(target, comet_ids):
        val += 8.0

    # 中心区域通常更有联通性，但也不能过度迷信
    center_gain = max(0.0, 46.0 - _orbital_radius(target))
    val += 0.22 * center_gain

    return val


def _ships_needed_to_take(target, eta, turn):
    owner = target[1]
    ships = target[5]
    prod = target[6]

    # 中立不生产；已占领星球会继续生产
    defend = ships + (prod * eta if owner != -1 else 0)

    # 冗余安全边际
    buffer = 2 if owner == -1 else 4 + prod // 2
    if turn > 260 and owner != -1:
        buffer += 2

    return int(math.ceil(defend + buffer))


def _best_intercept(src, target, send, angular_velocity, comet_ids, max_speed, max_eta=50):
    speed = _fleet_speed(send, max_speed)
    src_xy = (src[2], src[3])

    best = None
    best_key = None

    for eta in range(1, max_eta + 1):
        future_xy = _future_pos(target, eta, angular_velocity, comet_ids)
        d = _dist(src_xy, future_xy)

        # 用离散 eta 近似求截击点：
        # 当直线飞行距离接近“速度 * eta”时，将其视为可命中候选。
        miss = abs(d - speed * eta)
        threshold = target[4] + 0.9
        if miss > threshold:
            continue

        # 太阳安全检查
        if _point_to_segment_distance((CENTER, CENTER), src_xy, future_xy) < SUN_RADIUS + 0.15:
            continue

        angle = math.atan2(future_xy[1] - src_xy[1], future_xy[0] - src_xy[0])

        # 优先 miss 更小、ETA 更短的方案
        key = (miss + 0.03 * eta, eta)
        if best is None or key < best_key:
            best = (eta, angle, d, future_xy)
            best_key = key

    return best


def _frontline_value(planet, enemy_planets):
    nearest_enemy = _nearest_enemy_distance(planet, enemy_planets)
    return 6.0 * planet[6] - 0.45 * nearest_enemy + (8.0 if nearest_enemy < 32 else 0.0)


def agent(obs, cfg):
    my_id = obs["player"]
    planets = obs["planets"]
    turn = obs.get("step", 0)
    angular_velocity = obs.get("angular_velocity", 0.0)
    comet_ids = set(obs.get("comet_planet_ids", []))
    max_speed = float(_cfg_get(cfg, "shipSpeed", DEFAULT_MAX_SPEED) or DEFAULT_MAX_SPEED)

    my_planets = [p for p in planets if p[1] == my_id]
    enemy_planets = [p for p in planets if p[1] not in (-1, my_id)]
    target_planets = [p for p in planets if p[1] != my_id and p[0] not in comet_ids]

    if not my_planets or not target_planets:
        return []

    by_id = {p[0]: p for p in planets}
    remaining = {p[0]: int(p[5]) for p in my_planets}

    chosen_sources = set()
    chosen_targets = set()
    moves = []

    # 少量兵力档位，避免连续动作空间爆炸
    trial_fracs = (0.38, 0.58, 0.82)
    candidates = []

    # 先生成全局候选任务
    for src in my_planets:
        reserve = _reserve_ships(src, enemy_planets, turn)
        available = int(src[5]) - reserve
        if available < 6:
            continue

        for target in target_planets:
            if src[0] == target[0]:
                continue

            best_for_pair = None

            for frac in trial_fracs:
                send = max(6, int(available * frac))
                if send > available:
                    continue

                hit = _best_intercept(
                    src=src,
                    target=target,
                    send=send,
                    angular_velocity=angular_velocity,
                    comet_ids=comet_ids,
                    max_speed=max_speed,
                )
                if hit is None:
                    continue

                eta, angle, travel_dist, _ = hit
                need = _ships_needed_to_take(target, eta, turn)
                if send < need:
                    continue

                send = min(available, max(need, send))

                score = (
                    _target_value(target, turn, comet_ids)
                    - 0.17 * send
                    - 1.1 * eta
                    - 0.03 * travel_dist
                    + 9.0 * min(1.5, target[6] / max(1.0, need))
                )

                if target[1] == -1 and turn < 140:
                    score += 6.0
                if target[1] != -1 and turn > 180:
                    score += 6.0

                cand = (score, src[0], target[0], angle, int(send))
                if best_for_pair is None or cand[0] > best_for_pair[0]:
                    best_for_pair = cand

            if best_for_pair is not None:
                candidates.append(best_for_pair)

    # 按全局收益排序，而不是每个星球独立贪心
    candidates.sort(reverse=True)

    for score, src_id, target_id, angle, send in candidates:
        if src_id in chosen_sources or target_id in chosen_targets:
            continue

        src = by_id[src_id]
        reserve = _reserve_ships(src, enemy_planets, turn)
        available = remaining[src_id] - reserve
        if available < 6:
            continue

        send = min(send, available)
        if send < 5:
            continue

        moves.append([src_id, float(angle), int(send)])
        remaining[src_id] -= send
        chosen_sources.add(src_id)
        chosen_targets.add(target_id)

    # 回退策略：后排向前线增援，提高连续作战能力
    if len(moves) < max(1, len(my_planets) // 3) and len(my_planets) >= 2:
        frontline_targets = sorted(
            my_planets,
            key=lambda p: _frontline_value(p, enemy_planets),
            reverse=True,
        )
        frontline_ids = {p[0] for p in frontline_targets[: max(1, len(frontline_targets) // 2)]}

        for src in my_planets:
            if src[0] in chosen_sources:
                continue

            reserve = _reserve_ships(src, enemy_planets, turn)
            available = remaining[src[0]] - reserve
            if available < 10:
                continue

            best_reinf = None
            for dst in frontline_targets:
                if dst[0] == src[0]:
                    continue
                if dst[0] not in frontline_ids:
                    continue

                src_xy = (src[2], src[3])
                dst_xy = (dst[2], dst[3])

                if _point_to_segment_distance((CENTER, CENTER), src_xy, dst_xy) < SUN_RADIUS + 0.15:
                    continue

                angle = math.atan2(dst[3] - src[3], dst[2] - src[2])
                score = 4.0 * dst[6] - 0.04 * _dist(src_xy, dst_xy)

                if best_reinf is None or score > best_reinf[0]:
                    best_reinf = (score, dst[0], angle)

            if best_reinf is None:
                continue

            send = int(max(0, available * 0.45))
            if send >= 8:
                moves.append([src[0], float(best_reinf[2]), int(send)])
                remaining[src[0]] -= send
                chosen_sources.add(src[0])

    return moves
```

如果你要本地做一个最小可运行的 smoke test，可以用这样的 harness。它不是完整评测系统，但足够先检查是否报错、是否超时、以及在固定 seed 下的稳定性。

```python
from statistics import mean
from kaggle_environments import make
from my_agent import agent as my_agent  # 把上面的代码保存为 my_agent.py

def play_once(agents, seed):
    env = make("orbit_wars", configuration={"seed": seed}, debug=False)
    env.run(agents)
    return [s.reward for s in env.state]

def batch_eval(agents, seeds):
    results = [play_once(agents, seed) for seed in seeds]
    my_rewards = [r[0] for r in results]
    win_rate = sum(1 for x in my_rewards if x > 0) / len(my_rewards)
    return {
        "games": len(seeds),
        "mean_reward": mean(my_rewards),
        "win_rate": win_rate,
    }

if __name__ == "__main__":
    seeds = list(range(50))
    print("2P vs starter:", batch_eval([my_agent, "starter"], seeds))
    print("4P vs 3 starters:", batch_eval([my_agent, "starter", "starter", "starter"], seeds))
```

测试计划上，我强烈建议你以后**不要再只看 Kaggle live 分数做开发闭环**。公开讨论已经表明，rating 会随着 validation games 数增加而明显波动，而单局评测成本又大约在 20–30 秒量级；再考虑到官方开源环境仍在演化、2026 年 5 月时公开仓库上还有 Orbit Wars 相关 open issues，所以本地实验首先要做的是“版本固定 + 固定 seed + 可重复 head-to-head”，而不是“改点权重就直接提一个 live submission”。本地环境至少要固定到一个明确的 `kaggle-environments` 版本；当前 PyPI 发布到了 1.29.3，而开源 spec 中 `orbit_wars` 的环境版本写的是 1.0.9。citeturn33search1turn33search2turn22view0turn4search9turn2search2turn2search7

我建议把实验分成三层。第一层是 **smoke test**：100 个固定 seed，检查语法错误、超时、空动作、太阳自杀、越界自杀。第二层是 **promotion test**：2P 分别对 `starter`、对你自己的 v1.1、对当前分支的上一版候选 bot 各跑 300–500 局；4P 则至少评 `[your_bot, starter, starter, starter]` 和一个混合池。第三层才是 **live submission**。Orbit Wars 的公开讨论本身就反复提到 2P/4P 本地评测、并行 harness 的资源约束，以及 live score 的波动问题，所以这套三层流程会比“直接线上验证”可靠得多。citeturn20search3turn30search0turn30search1turn33search1

最后给你一个很实用的转向阈值。只要你还没有把“拦截几何、太阳安全、留守约束、任务化排序、后排增援、浅层 rollout”这六件事做完，就不要宣布“启发式到头了”。相反，如果你把这些都做完了，本地对 v1.1 的优势仍然不稳定，或者 public score 还是长期卡在 700 以下，那时再把主要精力转去宏动作搜索；等你有了稳定的 replay 管线和行为先验之后，再上 imitation / PPO。这条路线既尊重官方机制，也尊重当前社区已经公开展示出来的事实：启发式主导的方法已经能从几百分区间一路打进 900+ 甚至 1000+。citeturn14search22turn34search5turn24search8turn35search0