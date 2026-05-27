# -*- coding: utf-8 -*-
"""
Orbit Wars Heuristic Agent v1.1 - MORE AGGRESSIVE!
Target: 900+ Score
Changes from v1.0:
- Much more aggressive attack
- No defense reserve
- Higher production weighting
- Faster expansion
"""

import math

def agent(obs, cfg):
    my_id = obs['player']
    planets = obs['planets']
    fleets = obs.get('fleets', [])
    
    my_planets = [p for p in planets if p[1] == my_id]
    targets = [p for p in planets if p[1] != my_id]
    
    if not my_planets or not targets:
        return []
    
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
            
            score = t_prod * 30
            score -= dist * 0.15
            score -= t_ships * 0.2
            
            if t_owner == -1:
                score += 50
            
            if dist < 35:
                score += 30
            elif dist < 50:
                score += 15
            
            if score > best_score:
                best_score = score
                best_target = t
        
        if best_target:
            tx, ty = best_target[2], best_target[3]
            angle = math.atan2(ty - y, tx - x)
            
            needed_ships = best_target[5] + 2
            send_ships = int(min(ships * 0.85, needed_ships * 1.5))
            
            if send_ships < 5:
                send_ships = min(5, ships - 1)
            
            if send_ships < 1:
                continue
            
            moves.append([planet_id, angle, send_ships])
    
    return moves
