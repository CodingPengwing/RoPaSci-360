from cooked_pancakes.pq import PriorityQueue
from cooked_pancakes.foundations import *
import math

# # #
# Search algorithm: AStar
# 

def astar_search(start, goal_test, heuristic, verbose=False):
    """
    Run the A star search algorithm from a given start state with a given
    goal test and heuristic.
    `start` should be a state object with `actions_successors` method
    which yields actions and successor states.
    """
    # keep track of distances and predecessor states/actions in these maps
    dist = {start: 0}
    back = {start: None}
    # start with the start state and loop through states in priority order
    queue = PriorityQueue([(start, heuristic(start))])
    for state in queue:
        if verbose: state.print(f"{dist[state]} {heuristic(state)}")
        # if this is the goal, we are done: backtrack and return path
        if goal_test(state):
            actions = []
            while back[state] is not None:
                state, action = back[state]
                actions.append(action)
            return actions[::-1]
        # otherwise, expand this node to continue the search
        dist_new = dist[state] + 1
        for (action, successor) in state.actions_successors():
            if successor not in dist or dist[successor] > dist_new:
                dist[successor] = dist_new
                back[successor] = (state, action)
                queue[successor] = dist_new + heuristic(successor)
    # priority queue empty, there must be no solution
    return None

# # #
# Informing the search algorithm: Heuristic
# A simple calculation determines the straight-line hexagonal distance 
# of each lower token from the nearest upper token which will defeat it.
# The sum of these distances is a simple (but not necessarily admissible)
# heuristic drawing upper tokens towards lower tokens.
# The heuristic is not admissible in at least two ways:
# 1. Swing actions can reduce the effective distance between tokens, and
# 2. Moving upper tokens can reduce two minimum distances at once if the
#    lower tokens are in the same region of the board.
# The heuristic could be improved in any or all of the following ways:
# 1. Pre-computing real distances using an all-pairs-shortest-paths algorithm
#    could make the distance calculations aware of the block tokens.
# 2. Using a more sophisticated method of aggrgating the distances when there
#    are multiple tokens of the one symbol (upper or lower) such as solving
#    a small linear sum assignment problem and/or travelling salesman problem
#    could make the heuristic more accurate in more complex cases.
def heuristic(state):
    distance = 0
    for x, s in state.lower_tokens:
        r = Token.WHAT_BEATS[s]
        ys = [y for y, r_ in state.upper_tokens if r_ == r]
        if ys:
            distance += min(Hex.dist(x, y) for y in ys)
        else:
            distance += math.inf
    return distance

