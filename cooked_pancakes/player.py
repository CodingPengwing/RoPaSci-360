import random
import numpy as np

from cooked_pancakes.gametheory import solve_game
from cooked_pancakes.board import Board
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
        # Initial throw
        if self.board.team_upper.throws_remaining == 9:
            next_action = self.board.get_team(self.team_name).first_move()
            return next_action.to_tuple()

        # Z, A = self.board.compute_utility_matrix(self.board.get_team(self.team_name))
        # max_score = None
        # best_action = None
        # if self.team_name == UPPER:
        #     for i in range(len(Z)):
        #         row_sum = sum(Z[i])
        #         if max_score is None: max_score = row_sum
        #         elif max_score < row_sum: 
        #             max_score = row_sum
        #             best_action = i
        # else:
        #     for j in range(len(Z[0])):
        #         col_sum = 0
        #         for i in range(len(Z)):
        #             col_sum += Z[i][j]
        #         if max_score is None: max_score = col_sum
        #         elif max_score < col_sum: 
        #             max_score = col_sum
        #             best_action = j

        # next_action = A[0][best_action][LOWER] if self.team_name == LOWER else A[best_action][i][UPPER]




        # Not Initial throw idk do shit

        # find nash equilibrium using the current board state
        # the return value of find_nash_equilibrium() should be a dictionary that maps each team to its corresponding "optimal" action
        Z_ups, Z_lws, A = self.board.find_nash_equilibrium()
        
        if Z_ups or Z_lws:
            if self.team_name == UPPER: 
                (s,v) = solve_game(Z_ups)
                # next_action = A[v.index(max(v))][0]
            else:
                (s,v) = solve_game(Z_lws, True, False)
                # next_action = A[v.index(max(v))][1]
            
            if self.team_name == UPPER:
                next_action = A[np.argmax(s)][0][self.team_name]
            else:
                next_action = A[0][np.argmax(s)][self.team_name]
            # print(f'{self.team}: {next_action}')
            # print(s)
            # print("MAX")
            # print(np.argmax(s))
        else:
            next_action = self.board.get_team(self.team_name).first_move()
        # nash_equilibrium = s # huh?
        # nash_equilibrium = v
        
        # next_action = nash_equilibrium[self.team]



        


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
