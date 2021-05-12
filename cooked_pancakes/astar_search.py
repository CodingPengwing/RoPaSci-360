
from cooked_pancakes.util import exit_with_error
from cooked_pancakes.foundations import Token, Hex, Rules

UPPER = Rules.UPPER
LOWER = Rules.LOWER

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

def astar_search(team_dict: dict, team_name: str, start: Token, end: Token, blacklist: list = []):
    """
    Performs A* search
    """
    if team_name not in Rules.VALID_TEAMS:
        exit_with_error("Error in astar_search(): invalid team_name format.")
    for team in Rules.VALID_TEAMS:
        if team not in team_dict:
            exit_with_error("Error in astar_search(): incorrect team_dict dictionary format.")
    
    team = team_dict[team_name]
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
        neighbours = [a.to_hex for a in team._move_actions(x, team_dict)]

        # for neighbour in neighbours: print(neighbour)

        for neighbour in neighbours:
            neighbour = Node(neighbour, current_node)

            if neighbour in closed: continue
            if neighbour.position in blacklist: continue

            # Using euclidean distance to calculate heuristics
            neighbour.g = Hex.dist(neighbour.position, start_node.position)
            neighbour.h = Hex.dist(neighbour.position, goal_node.position)
            # neighbour.g = distance.euclidean(neighbour.position, start_node.position)
            # neighbour.h = distance.euclidean(neighbour.position, goal_node.position)
            neighbour.f = neighbour.g + neighbour.h

            if (add_to_open(open,neighbour) == True):
                open.append(neighbour)

    # No paths found
    # print("why")
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

def find_path_length(team_dict: dict, team_name: str, start: Token, end: Token):
    path = astar_search(team_dict, team_name, start, end)
    return len(path) if path else None


"""---------> Might have to change 'end' to a Hex so it works with cutting in path"""
def find_attack_moves_for_token(team_dict: dict, team_name: str, start: Token, end: Token):
    moves = []
    blacklist = []
    # team = team_dict[team_name]
    path = astar_search(team_dict, team_name, start, end)
    if path:
        optimal_path_len = len(path)
    else:
        return None

    if len(path) == 2:
        moves.append(path[1])
        blacklist.append(path[1])
        path = astar_search(team_dict, team_name, start, end, blacklist=blacklist)
        if path:
            moves.append(path[1])
    elif len(path) > 2:
        while path:
            if len(path) == optimal_path_len:
                moves.append(path[1])
                blacklist.append(path[1])
                path = astar_search(team_dict, team_name, start, end, blacklist=blacklist)
            else: break

    enemy_team = team_dict[UPPER] if team_name == LOWER else team_dict[LOWER]
    enemy_occupied = [t.hex for t in enemy_team.get_tokens_of_type(start.what_beats())]
    safe_moves = []
    if enemy_occupied and moves:
        risky_hexes = []
        for hex in enemy_occupied:
            risky_hexes += [a.to_hex for a in enemy_team._move_actions(hex, team_dict)]
        risky_hexes = set(risky_hexes)
        for move in moves:
            if move not in risky_hexes:
                safe_moves.append(move)

    return safe_moves if safe_moves else moves


