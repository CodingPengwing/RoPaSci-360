from cooked_pancakes.board import Board

class Node:
    children: list
    score: float

    def __init__(self, board: Board, parent: Node):       
        self.board = board
        self.parent = parent
        self.children = []

    def add_child(self, child: Node):
        self.children.append(child)
    
     
    


