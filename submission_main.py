# -*- coding: utf-8 -*-
"""
Orbit Wars - SIMPLE SUBMISSION VERSION
Just copy this entire file to Kaggle as main.py
"""

import math

def agent(obs, cfg):
    my_id = obs['player']
    planets = obs['planets']
    
    my_planets = [p for p in planets if p[1] == my_id]
    targets = [p for p in planets if p[1] != my_id]
    
    moves = []
    for p in my_planets:
        planet_id, owner, x, y, radius, ships, prod = p
        
        if ships < 15:
            continue
        
        best_target = None
        best_score = -1
        
        for t in targets:
            t_id, t_owner, t_x, t_y, t_r, t_ships, t_prod = t
            
            dist = math.sqrt((t_x - x) ** 2 + (t_y - y) ** 2)
            
            score = t_prod * 10 - dist * 0.3 - t_ships * 0.1
            
            if score > best_score:
                best_score = score
                best_target = t
        
        if best_target:
            tx, ty = best_target[2], best_target[3]
            angle = math.atan2(ty - y, tx - x)
            
            send_ships = int(min(ships * 0.6, best_target[5] + 10))
            if send_ships >= 10:
                moves.append([planet_id, angle, send_ships])
    
    return moves
