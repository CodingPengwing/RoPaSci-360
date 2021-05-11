import random
import numpy as np

from cooked_pancakes.gametheory import solve_game
from cooked_pancakes.board import Board
from cooked_pancakes.foundations import Rules, Action, Hex
from cooked_pancakes.strategy import *
from cooked_pancakes.util import is_type

UPPER = Rules.UPPER
LOWER = Rules.LOWER

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

        # Initial throw
        if team.throws_remaining == 9:
            to_hex = Hex(r=4,q=-2)
            if self.team_name == LOWER: to_hex.invert()
            next_action = Action(action_type = "THROW", token_symbol= "r", to_hex=to_hex)
            # next_action = self.board.get_team(self.team_name).first_move()
            return next_action.to_tuple()

        # # If second throw
        # if team.throws_remaining == 8:
        #     to_hex = Hex(r=3,q=-2)
        #     if self.team_name == LOWER: to_hex.invert()
        #     next_action = Action(action_type = "THROW", token_symbol= "s", to_hex=to_hex)
        #     return next_action.to_tuple()

        # # If third throw
        # if team.throws_remaining == 7:
        #     to_hex = Hex(r=2,q=-1)
        #     if self.team_name == LOWER: to_hex.invert()
        #     next_action = Action(action_type = "THROW", token_symbol= "p", to_hex=to_hex)
        #     return next_action.to_tuple()

        # next_action = improved_greedy(self.board, team)
        # if is_type(next_action, tuple): return next_action
        # return next_action.to_tuple()
        return lol_main(self.board, team).to_tuple()

    

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
