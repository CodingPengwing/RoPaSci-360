import numpy as np
from cooked_pancakes.board import Board
from cooked_pancakes.team import Team
from cooked_pancakes.foundations import Rules
from cooked_pancakes.gametheory import solve_game

CUTOFF = 3
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
    

def lol_main(curr_board: Board, team: Team):
    depth = 0
    (s,v) = recurisve_thingo(curr_board, team, depth)

    # Hence using s we can work out our best move I think
    our_actions = team.generate_actions(curr_board.team_dict)
    next_action = our_actions[np.argmax(s)]

    return next_action

'''
NEED TO PRUNE!!!
'''
def recurisve_thingo(board: Board, team: Team, depth: int):
    
    if depth == CUTOFF:
        return (None, board.evaluate(team))
    
    else:
        depth += 1
        # generate potential actions
        upper_actions = board.team_upper.generate_actions(board.team_dict)
        lower_actions = board.team_lower.generate_actions(board.team_dict)
        
        # create matrix
        V = []
        for i in range(len(upper_actions)):
            V_i = []
            
            for j in range(len(lower_actions)):
                actions = {UPPER: upper_actions[i], LOWER: lower_actions[j]}
                # fill matrix with successor board states
                
                new_board = Board(board.team_upper, board.team_lower)
                new_board.successor(actions)
                (s, v) = recurisve_thingo(new_board, team, depth)
                V_i.append(v)
            
            V.append(V_i)

        # solve matrix and return
        '''check maximiser and minimiser stuff idk'''
        (s, v) = solve_game(V)
        return (s, v)





