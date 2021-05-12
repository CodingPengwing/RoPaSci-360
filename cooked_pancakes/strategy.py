import numpy as np
import copy
import random
from cooked_pancakes.board import Board
from cooked_pancakes.team import Team
from cooked_pancakes.foundations import Rules, Hex, Action, Token
from cooked_pancakes.gametheory import solve_game
from cooked_pancakes.astar_search import astar_search, find_attack_moves_for_token

CUTOFF = 1
UPPER = Rules.UPPER
LOWER = Rules.LOWER


def run_to_ally_strategy(team:Team, team_dict:dict, vulnerable_token: Token, enemy_token: Token, enemy_what_beats: str):
    next_action: Action = None
    saviour = vulnerable_token.find_closest_token(team.get_tokens_of_type(enemy_what_beats))

    if not saviour: return None
    
    if Hex.dist(saviour.hex, vulnerable_token.hex) == 1: 
        moves = team.token_run_away_from(vulnerable_token, enemy_token, team_dict)
        if moves:
            if Hex.dist(vulnerable_token.hex, moves[0]) == 2:
                return Action.create_action_from_path(vulnerable_token.hex, moves[0])

    all_actions = team._move_actions(vulnerable_token.hex, team_dict)
    all_moves = [action.to_hex for action in all_actions]
    min_dist = -1
    next_hex = None
    if all_moves: random.shuffle(all_moves)
    for move in all_moves:
        dist = Hex.dist(move, saviour.hex)
        if min_dist == -1 or dist < min_dist:
            min_dist = dist
            next_hex = move
    
    if next_hex:
        return Action.create_action_from_path(vulnerable_token.hex, next_hex)
    return None

def run_to_enemy_strategy(team:Team, team_dict:dict, vulnerable_token: Token, enemy_token:Token, enemy_team: Team):
    next_action: Action = None
    safe_enemies = enemy_team.get_tokens_of_type(vulnerable_token.symbol)
    if safe_enemies:
        closest_safe_enemy = vulnerable_token.find_closest_token(safe_enemies)
        
        all_actions = team._move_actions(vulnerable_token.hex, team_dict)
        all_moves = [action.to_hex for action in all_actions]

        # run_moves = team.token_run_away_from(vulnerable_token, enemy_token, team_dict)
        min_dist = -1
        best_run_move = None
        for move in all_moves:
            # print(move)
            dist = Hex.dist(move, closest_safe_enemy.hex)
            if min_dist == -1 or dist < min_dist:
                min_dist = dist
                best_run_move = move
        
        if best_run_move:
            return Action.create_action_from_path(vulnerable_token.hex, best_run_move)

    return next_action

def throw_strategy(team: Team, enemy_token:Token, enemy_what_beats: str, throwzone: list):
    next_action: Action = None
    min_dist = -1
    closest_throw_hex = None
    for throw_hex in throwzone:
        dist = Hex.dist(throw_hex, enemy_token.hex)
        if min_dist == -1 or dist < min_dist:
            closest_throw_hex = throw_hex
            min_dist = dist

    if closest_throw_hex and team.throws_remaining:
        next_action = Action(action_type=Rules.THROW, token_symbol=enemy_what_beats, to_hex=throw_hex)
    
    return next_action

def protect_strategy():
    next_action: Action
    return next_action

def attack_strategy():
    next_action: Action
    return next_action


def defense_mechanism(board:Board, team:Team):
    enemy_team = board.team_upper if team.team_name == LOWER else board.team_lower
    team_dict = board.team_dict

    attack_actions = team.generate_attack_actions(team_dict)
    if attack_actions:
        for action in attack_actions:
            attack_position = action.to_hex
            enemy_tokens = enemy_team.get_tokens_at(attack_position)
            if enemy_tokens: 
                num_enemy_tokens = len(enemy_tokens)
                if num_enemy_tokens > 1:
                    ally_tokens = team.get_tokens_at(attack_position)
                    if not ally_tokens:
                        return action
                    if num_enemy_tokens - len(ally_tokens) >= 2:
                        return action

    (threat, threat_dist) = team.determine_closest_threat(team_dict)
    if threat:
        enemy_defeatables = team.generate_enemy_defeatable(team_dict)
        enemy_token = threat[0]
        ally_token = threat[1]
        enemy_what_beats = enemy_token.what_beats()
        
        if threat_dist == 1: 
            if enemy_defeatables[ally_token.symbol]:
                defeatable_list = enemy_defeatables[ally_token.symbol]
                while defeatable_list:
                    closest_enemy = ally_token.find_closest_token(defeatable_list)
                    path = astar_search(team_dict, team.team_name, ally_token, closest_enemy)
                    if not path:
                        defeatable_list.remove(closest_enemy)
                    else:
                        return Action.create_action_from_path(path[0], path[1])
            
            # Get as close to saviour as possible
            run_to_ally = run_to_ally_strategy(team, team_dict, ally_token, enemy_token, enemy_what_beats)
            if run_to_ally: return run_to_ally

            run_to_enemy = run_to_enemy_strategy(team, team_dict, ally_token, enemy_token, enemy_team)
            if run_to_enemy: return run_to_enemy
            
            # if team.throws_remaining > enemy_team.throws_remaining:
            # If in our territory, throw on top 
            if len(team.get_tokens_of_type(enemy_what_beats)) < 2 and team.throws_remaining>0:
                throwzone = team.generate_throw_zone(team_dict, enemy_what_beats)   
                if enemy_token.hex in throwzone:
                    return Action(action_tuple=(Rules.THROW, enemy_what_beats, enemy_token.hex.to_tuple()))
                

        elif threat_dist <= 3:
            path = astar_search(team_dict, enemy_team.team_name, enemy_token, ally_token)
             
            if path:
                # check if ally token can cut in 
                saviours = team.get_tokens_of_type(enemy_what_beats)
                if saviours:
                    for ally in saviours:
                        ally_moves = team._move_actions(ally.hex, team_dict)
                        for action in ally_moves:
                            if action.to_hex == path[1]:
                                cut_path_action = action
                                return cut_path_action

                # Check if throw is possible given that that token symbol is not already on board
                if len(team.get_tokens_of_type(enemy_what_beats)) < 2 and team.throws_remaining>0:
                    throwzone = team.generate_throw_zone(team_dict, enemy_what_beats)   
                    if path[1] in throwzone and team.throws_remaining:
                        return Action(action_tuple=(Rules.THROW, enemy_what_beats, path[1].to_tuple()))

        if not team.generate_attack_actions(team_dict):
            throw_action, min_dist = team.determine_best_throw(team_dict)
            return throw_action

    return None
            
    

def game_theory(board:Board, team:Team):
    team_dict = board.team_dict
    depth = 0
    (s, v, V) = mixed_strategy_nash_equilibrium(board, team, depth)
    our_actions = team.generate_good_actions(team_dict)
    chance = random.uniform(0,1)
    index = 0
    cumulative_probability = 0
    for i in range(len(s)):
        prob = s[i]
        if chance > cumulative_probability:
            index = i
            break
        cumulative_probability += prob

    next_action = our_actions[index]

    return next_action

    

'''
NEED TO PRUNE!!!
'''
def mixed_strategy_nash_equilibrium(board: Board, team: Team, depth: int):
    enemy_team = board.team_upper if team.team_name == LOWER else board.team_lower
    
    if depth == CUTOFF:
        return (None, board.evaluate(team) - board.evaluate(enemy_team), None)
        # return (None, board.evaluate(team), None)
    
    else:
        depth += 1
        # generate potential actions
        upper_actions = board.team_upper.generate_good_actions(board.team_dict)
        lower_actions = board.team_lower.generate_good_actions(board.team_dict)
        
        # create matrix
        V = []
        for i in range(len(upper_actions)):
            V_i = []
            
            for j in range(len(lower_actions)):
                actions = {UPPER: upper_actions[i], LOWER: lower_actions[j]}
                # fill matrix with successor board states
                
                new_board = Board(team_upper = board.team_upper, team_lower = board.team_lower)
                new_board.successor(actions)

                # else:
                (s, v, U) = mixed_strategy_nash_equilibrium(new_board, team, depth)
                
                V_i.append(v)
            
            V.append(V_i)
        
        # solve matrix and return
        # Solve game for us 
        if team.team_name == UPPER: 
            (s,v) = solve_game(V)
        else:
            (s,v) = solve_game(V, maximiser=True, rowplayer=False)

        return (s, v, V)





