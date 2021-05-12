import random
import time
import numpy as np

from cooked_pancakes.gametheory import solve_game
from cooked_pancakes.board import Board
from cooked_pancakes.foundations import Rules, Action, Hex
from cooked_pancakes.strategy import *
from cooked_pancakes.util import is_type
from cooked_pancakes.greedy_strategy import greedy_strategy

UPPER = Rules.UPPER
LOWER = Rules.LOWER

class Player:
    team_name: str
    board: Board
    total_time: float
    start_time: float

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
        self.total_time = float(0)

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        start_time = time.time()
        next_action: Action
        team = self.board.team_dict[self.team_name]

        # Initial throw
        if team.throws_remaining == 9:
            next_action = self.board.get_team(self.team_name).first_move()
            return next_action.to_tuple()
        # Second move
        if team.throws_remaining == 8:
            active_symbol = team.active_tokens[0].symbol

            best_throw, min_dist = team.determine_best_throw(self.board.team_dict)
            if best_throw and best_throw.token_symbol != active_symbol:
                return best_throw.to_tuple()
            else:
                next_action = self.board.get_team(self.team_name).second_move()
                return next_action.to_tuple()

        next_action = defense_mechanism(self.board, team)
        if next_action: return next_action.to_tuple()
        
        if (self.total_time > 45):
            print("===== Switched to greedy strategy =====")
            return greedy_strategy(self.board, team)
        
        next_action = game_theory(self.board, team).to_tuple()
        end_time = time.time()
        
        self.total_time += (end_time - start_time)
        return next_action

    

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
        # print(f'EVAL: {self.board.evaluate(self.board.team_dict[self.team_name])}')
