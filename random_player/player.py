import random
import time
import numpy as np

from random_player.board import Board
from cooked_pancakes.foundations import Rules, Action

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
        team = self.board.get_team(self.team_name)
        actions = team.generate_actions(self.board.team_dict)
        # print([print(action) for action in actions])
        i = np.random.randint(0, len(actions)-1)
        next_action = actions[i]
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
