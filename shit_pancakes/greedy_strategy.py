import random
import numpy as np

from cooked_pancakes.team import Team
from cooked_pancakes.board import Board
from cooked_pancakes.foundations import Rules, Action, Hex
from cooked_pancakes.astar_search import astar_search

UPPER = Rules.UPPER
LOWER = Rules.LOWER
SLIDE = Rules.SLIDE
SWING = Rules.SWING

def greedy_strategy(board: Board, team:Team):
    next_action: Action
    team = board.team_dict[team.team_name]
    team_dict = board.team_dict
    enemy_team = board.team_upper if team.team_name == LOWER else board.team_lower
    
    # Initial throw
    if board.team_upper.throws_remaining == 9:
        next_action = team.first_move()
        return next_action.to_tuple()

    # Find best throw
    throw_action, throw_dist_to_kill = team.determine_best_throw(team_dict)

    # Find closest defeatable pair
    closest_pair, pair_dist_to_kill = team.determine_closest_kill(team_dict)

    # If can throw directly on top of opponent token, throw
    if throw_action and enemy_team.get_token_at(throw_action.to_hex):
        return throw_action.to_tuple()
    
    if closest_pair:
        path = astar_search(team_dict= board.team_dict, team_name=team.team_name, start=closest_pair[0], end=closest_pair[1])
        # print(closest_pair[0])
        # print(closest_pair[1])
        # print("path")
        # print(path)
        if path:
            next_action = Action.create_action_from_path(path[0], path[1])
            return next_action.to_tuple()
        # else:
            # ally and enemy token in same hex
            # move ally token away

            
    if throw_action:
        return throw_action.to_tuple()

    # if all else fails, random move
    random_actions = team.generate_actions(team_dict)

    i = np.random.randint(0, len(random_actions)-1)
    next_action = random_actions[i]
    
    return next_action.to_tuple()