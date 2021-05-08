import random
import numpy as np

from cooked_pancakes.board import Board
from cooked_pancakes.team import Team
from cooked_pancakes.foundations import Rules, Action, Hex
from greedy_player.astar_search import astar_search

UPPER = Rules.UPPER
LOWER = Rules.LOWER
SLIDE = Rules.SLIDE
SWING = Rules.SWING

class Player:
    team_name: str
    board: Board

    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """

        self.team_name = player
        self.board = Board()

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        next_action: Action
        team = self.board.team_dict[self.team_name]
        team_dict = self.board.team_dict
        
        # Initial throw
        if self.board.team_upper.throws_remaining == 9:
            next_action = team.first_move()
            return next_action.to_tuple()

        # Find best throw
        throw_action, throw_dist_to_kill = team.determine_best_throw(team_dict)

        # Find closest defeatable pair
        closest_pair, pair_dist_to_kill = team.determine_closest_kill(team_dict)

        # If can throw directly on top of opponent token, throw
        if throw_action and team.get_token_at(throw_action.to_hex):
            return throw_action.to_tuple()
        
        if closest_pair:
            path = astar_search(self.board, closest_pair[0], closest_pair[1], team)
            print(closest_pair[0])
            print(closest_pair[1])
            print("path")
            print(path)
            if path:
                symbol = team.get_token_at(path[0]).symbol
                move_type = SLIDE if Hex.dist(path[0], path[1]) == 1 else SWING

                next_action = Action(action_type = move_type, token_symbol = symbol, from_hex=path[0], to_hex=path[1])
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
    



    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """

        player_action = Action(action_tuple = player_action)
        opponent_action = Action(action_tuple = opponent_action)
        update_actions = {UPPER: player_action, LOWER: opponent_action} if (self.team_name == UPPER) else {LOWER: player_action, UPPER: opponent_action}        
        self.board.successor(update_actions)
