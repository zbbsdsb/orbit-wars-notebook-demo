# -*- coding: utf-8 -*-
"""
Orbit Wars AI - v1.3 结构化启发式智能体
基于 ChatGPT Deep Research 建议：
- 旋转星球截击几何
- 太阳安全检测
- ETA守军估计
- 任务化编排
- 后排增援
"""

import math
from typing import Dict, List, Any, Tuple, Optional
import os

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
        # 当直线飞行距离接近"速度 * eta"时，将其视为可命中候选。
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


if __name__ == "__main__":
    print("Orbit Wars v1.3 - 结构化启发式智能体")
    print("=" * 60)

    test_obs = {
        "player": 0,
        "planets": [
            [0, 0, 20.0, 20.0, 2.0, 50, 3],
            [1, 1, 80.0, 80.0, 2.0, 30, 2],
            [2, -1, 50.0, 20.0, 1.5, 20, 1],
        ],
        "fleets": [],
        "comet_planet_ids": [],
        "angular_velocity": 0.03,
        "step": 0,
    }

    result = agent(test_obs, {})
    print(f"测试结果: {result}")
    print("\n✅ Agent 本地测试通过")

    print("\n正在写入 main.py（用于 Kaggle 提交）...")
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write('''# -*- coding: utf-8 -*-
"""
Orbit Wars v1.3 - 结构化启发式智能体
Kaggle 提交版本
"""

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

    reserve = 6 + prod * 2

    if turn < 140:
        reserve += 2

    if nearest_enemy < 26:
        reserve += 8
    elif nearest_enemy < 38:
        reserve += 4

    return min(int(src[5]) - 1, max(0, reserve))


def _target_value(target, turn, comet_ids):
    owner = target[1]
    prod = target[6]

    val = 24.0 * prod

    if owner == -1:
        val += 18.0 if turn < 140 else 8.0
    else:
        val += 14.0 if turn > 120 else 4.0

    if not _is_rotating(target, comet_ids):
        val += 8.0

    center_gain = max(0.0, 46.0 - _orbital_radius(target))
    val += 0.22 * center_gain

    return val


def _ships_needed_to_take(target, eta, turn):
    owner = target[1]
    ships = target[5]
    prod = target[6]

    defend = ships + (prod * eta if owner != -1 else 0)

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

        miss = abs(d - speed * eta)
        threshold = target[4] + 0.9
        if miss > threshold:
            continue

        if _point_to_segment_distance((CENTER, CENTER), src_xy, future_xy) < SUN_RADIUS + 0.15:
            continue

        angle = math.atan2(future_xy[1] - src_xy[1], future_xy[0] - src_xy[0])

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

    trial_fracs = (0.38, 0.58, 0.82)
    candidates = []

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

''')
    print("✅ main.py 已写入")
