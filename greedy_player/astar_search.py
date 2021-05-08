from scipy.spatial import distance
from cooked_pancakes.foundations import Token, Hex
from cooked_pancakes.team import Team
from cooked_pancakes.board import Board


"""
This file was created while referencing the following website:
https://www.annytab.com/a-star-search-algorithm-in-python/
"""

class Node:

    def __init__(self, position: Hex, parent: Hex):
        self.position = position
        self.parent = parent
        self.g = 0  # Estimated distance from start node
        self.h = 0  # Estimated distance to goal node 
        self.f = 0  # g + h
    
    def __eq__(self, other):
        return other.position == self.position

    def __lt__(self, other):
        return other.f > self.f
    
    def __repr__(self):
        return ('({0},{1})'.format(self.position, self.f))

def astar_search(board: Board, start: Token, end: Token, team: Team):
    """
    Performs A* search
    """
    open = []
    closed = []

    start_node = Node(start.hex, None)
    goal_node = Node(end.hex, None)

    open.append(start_node)

    while open:
        # Sorting the open list so that the node with the lowest f value is first
        open.sort()
        
        current_node = open.pop(0)
        closed.append(current_node)
        
        # If goal has been reached, backtrack to find the path and return
        if current_node == goal_node:
            path = []
            while current_node != start_node:
                path.append(current_node.position)
                current_node = current_node.parent
            path.append(start.hex)
            return path[::-1]

        x = current_node.position
        
        # Finding actions of current node
        neighbours = [a.to_hex for a in team._move_actions(x, board.team_dict)]

        for neighbour in neighbours:
            neighbour = Node(neighbour, current_node)

            if neighbour in closed: continue

            # Using euclidean distance to calculate heuristics
            neighbour.g = Hex.dist(neighbour.position, start_node.position)
            neighbour.h = Hex.dist(neighbour.position, goal_node.position)
            # neighbour.g = distance.euclidean(neighbour.position, start_node.position)
            # neighbour.h = distance.euclidean(neighbour.position, goal_node.position)
            neighbour.f = neighbour.g + neighbour.h

            if (add_to_open(open,neighbour) == True):
                open.append(neighbour)

    # No paths found
    return None

def add_to_open(open, neighbour):
    """
    Checks if a neighbour should be added to open list
    """
    for node in open:
        if neighbour == node and neighbour.f >= node.f:
            # Will not add if there already exists the same node in open that has lower f value
            return False

    return True


