import numpy as np
import copy
from cooked_pancakes.board import Board
from cooked_pancakes.team import Team
from cooked_pancakes.foundations import Rules, Hex, Action
from cooked_pancakes.gametheory import solve_game
from cooked_pancakes.astar_search import astar_search, find_attack_moves_for_token

CUTOFF = 2
UPPER = Rules.UPPER
LOWER = Rules.LOWER

# class Node:
#     children: list
#     score: float

#     def __init__(self, board: Board, parent: Node):       
#         self.board = board
#         self.parent = parent
#         self.children = []
#         self.score = -1

#     def add_child(self, child: Node):
#         self.children.append(child)


def improved_greedy(board: Board, team: Team):
    enemy_team = board.team_upper if team.team_name == LOWER else board.team_lower
    # Find best throw
    best_throw_action, throw_dist_to_kill = team.determine_best_throw(board.team_dict)

    # Find closest defeatable pair
    closest_pair, pair_dist_to_kill = team.determine_closest_kill(board.team_dict)
    closest_action = None

    # If can throw directly on top of opponent token, throw
    if best_throw_action and enemy_team.get_token_at(best_throw_action.to_hex):
        return best_throw_action.to_tuple()
    
    # Finding path between closest killable enemy token
    if closest_pair:
        path = astar_search(board.team_dict, team.team_name, closest_pair[0], closest_pair[1])
        if path:
            move_type = Rules.SLIDE if Hex.dist(path[0], path[1]) == 1 else Rules.SWING

            closest_action = Action(action_type = move_type, from_hex=path[0], to_hex=path[1])
        elif best_throw_action:
            return best_throw_action

    # attack_moves = team.generate_attack_actions(board.team_dict)
    # run_actions = team.generate_run_actions(board.team_dict)

    enemy_actions = enemy_team.generate_good_actions(board.team_dict)

    if closest_action and enemy_actions:
        U = []
        for enemy_action in enemy_actions:
            upper_action = closest_action if team.team_name == UPPER else enemy_action
            lower_action = closest_action if team.team_name == LOWER else enemy_action
            actions = {UPPER: upper_action, LOWER: lower_action}

            new_board = Board(team_upper = board.team_upper, team_lower = board.team_lower)
            new_board.successor(actions)
            u = new_board.evaluate(team)
            U.append(u)

        s = sum(U)/len(U)
        print(s)
        '''
        THINK ABOUT THIS VALUE
        '''
        if s > 0: 
            return closest_action

    # Solve game for them
    # if team.team_name == LOWER: 
    #     (s_opp,v) = solve_game(V, maximiser=False, rowplayer=True)
    # else:
    #     (s_opp,v) = solve_game(V, maximiser=False, rowplayer=False)
    
    # if team.team_name == UPPER: V = np.transpose(V)
    # V_total = np.dot(V, s)

    # print(len())
    # print(len(V_total))
    # Hence using we can work out our best move I think
    
    return lol_main(board, team)

    # (s, v, V) = recursive_thingo(board, team, depth = 0)
    # our_actions = team.generate_good_actions(board.team_dict)
    # # print(our_actions)
    # next_action = our_actions[np.argmax(s)]
    # if v > 0:
    #     return next_action
    
    # if closest_action:
    #     return closest_action

    # if best_throw_action:
    #     return best_throw_action

    # # if all else fails, random move
    # random_actions = team.generate_actions(board.team_dict)

    # i = np.random.randint(0, len(random_actions)-1)
    # next_action = random_actions[i]
    
    # return next_action



def simple_strategy(board: Board, team:Team):
    upper_actions = board.team_upper.generate_good_actions(board.team_dict)
    lower_actions = board.team_lower.generate_good_actions(board.team_dict)
    # print(f'upp: {upper_actions}')
    # print(f'low: {lower_actions}')
    
    # create matrix
    V = []
    for i in range(len(upper_actions)):
        V_i = []
        
        for j in range(len(lower_actions)):
            actions = {UPPER: upper_actions[i], LOWER: lower_actions[j]}
            # print(f'Upper: {upper_actions[i]}')
            # print(f'Lower: {lower_actions[j]}')
        
            new_board = Board(team_upper = board.team_upper, team_lower = board.team_lower)
            new_board.successor(actions)
            v = new_board.evaluate(team)
            # print(v)
            # print(new_board)
            V_i.append(v)
        
        V.append(V_i)
    return V, upper_actions, lower_actions

'''
ok honestly let's fix this first idk what's up anymore
'''
# def lol_main(curr_board: Board, team: Team):
    
#     V, upper_actions, lower_actions = simple_strategy(curr_board, team)
#     # print("Up")
#     # for action in upper_actions: print(action, end=', ')
#     # print('\n')
#     # print("Low")
#     # for action in lower_actions: print(action, end=', ')
#     # print('\n')
    
#     # print(V)
#     if team.team_name == LOWER: 
#         (s_opp,v) = solve_game(V, maximiser=False, rowplayer=True)
#     else:
#         (s_opp,v) = solve_game(V, maximiser=False, rowplayer=False)

#     # V_row_totals = []
#     # for V_i in V:
#     #     V_row_totals.append(np.sum(V_i))

#     if team.team_name == LOWER: 
#         V_total = np.dot(s_opp, V)
#     else:
#         V_total = np.dot(V, s_opp)
    
    
#     next_action = upper_actions[np.argmax(V_total)]

#     return next_action


def lol_main(curr_board: Board, team: Team):
    depth = 0
    (s, v, V) = recursive_thingo(curr_board, team, depth)

    # # Solve game for them
    # if team.team_name == LOWER: 
    #     (s_opp,v) = solve_game(V, maximiser=False, rowplayer=True)
    # else:
    #     (s_opp,v) = solve_game(V, maximiser=False, rowplayer=False)

    # Dot product
    # print(f's_opps: {s_opp}')
    # print(V)
    
    # lower_actions = curr_board.team_lower.generate_good_actions(curr_board.team_dict)
    # for action in lower_actions: print(action, end=', ')
    
    # if team.team_name == UPPER: V = np.transpose(V)
    # V_total = np.dot(V, s)

    # if team.team_name == LOWER:
    #     V_total = np.dot(s, V)
    # else:
    #     V_total = np.dot(V, s)

    # Hence using we can work out our best move I think
    our_actions = team.generate_good_actions(curr_board.team_dict)

    next_action = our_actions[np.argmax(s)]

    return next_action

'''
NEED TO PRUNE!!!
'''
def recursive_thingo(board: Board, team: Team, depth: int):
    enemy_team = board.team_upper if team.team_name == LOWER else board.team_lower
    
    if depth == CUTOFF:
        # return (None, board.evaluate(team) - board.evaluate(enemy_team), None)
        return (None, board.evaluate(team), None)
    
    else:
        depth += 1
        # generate potential actions
        upper_actions = board.team_upper.generate_good_actions(board.team_dict)
        lower_actions = board.team_lower.generate_good_actions(board.team_dict)
        # print(f'upp: {upper_actions}')
        # print(f'low: {lower_actions}')
        
        # create matrix
        V = []
        for i in range(len(upper_actions)):
            V_i = []
            
            for j in range(len(lower_actions)):
                actions = {UPPER: upper_actions[i], LOWER: lower_actions[j]}
                # fill matrix with successor board states
                
                new_board = Board(team_upper = board.team_upper, team_lower = board.team_lower)
                new_board.successor(actions)
                e = new_board.evaluate(team)
                # if e - board.evaluate(team) < -1:
                if e < board.evaluate(team):
                    v = e
                else:
                    (s, v, U) = recursive_thingo(new_board, team, depth)

                # print(new_board)
                # print(eval)
                # (s, v, U) = recursive_thingo(new_board, team, depth)

                
                V_i.append(v)
                # if upper_actions[i].is_throw():
                #     print("THROW")
                # else:
                #     print("MOVE")
                # print(v)
                # print(new_board)
                # print(f'lol: {v}')
            
            V.append(V_i)
        
        # solve matrix and return
        # Solve game for us 
        if team.team_name == UPPER: 
            (s,v) = solve_game(V)
            # (s_opp, v_opp) = solve_game(V, maximiser=False, rowplayer=False)
        else:
            (s,v) = solve_game(V, maximiser=True, rowplayer=False)
            # (s_opp, v_opp) = solve_game(V, maximiser=False, rowplayer=True)


        # print(V)
        # new_v = v-v_opp
        # if new_v < 0.0001:
        #     new_v = 0
        return (s, v, V)





