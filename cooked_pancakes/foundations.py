from cooked_pancakes.util import exit_with_error, is_tuple

class Rules:
    MAX_STEPS = 9
    MAX_THROWS = 9

    ROCK = "r"
    PAPER = "p"
    SCISSOR = "s"
    VALID_SYMBOLS = {ROCK, PAPER, SCISSOR}

    UPPER = "upper"
    LOWER = "lower"
    VALID_TEAMS = {UPPER, LOWER}

    THROW = "THROW"
    SLIDE = "SLIDE"
    SWING = "SWING"
    VALID_ACTIONS = {THROW, SLIDE, SWING}

    HEX_RADIUS = 5
    # range -4 to 4 because map includes (0,0)
    HEX_RANGE = range(-HEX_RADIUS+1, HEX_RADIUS)
 
    
    
class Hex:
    """
    Hexagonal axial coordinates with basic operations and hexagonal
    manhatten distance.
    Thanks to https://www.redblobgames.com/grids/hexagons/ for some
    of the ideas implemented here.
    """

    HEX_RADIUS = Rules.HEX_RADIUS

    r: int
    q: int
        
    @classmethod
    def is_in_boundary(cls, r: int, q: int):
        """
        Determines whether the given coordinate (r,q) or given Hex is within the bounds of our 
        playing board. Inputting a Hex will override any other arguments given.
        """
        if abs(r) >= cls.HEX_RADIUS or abs(q) >= cls.HEX_RADIUS or abs(r+q) >= cls.HEX_RADIUS:
            return False
        return True
    
    
    @classmethod
    def is_valid_coordinate(cls, coordinate: tuple):
        if not coordinate: return False
        if len(coordinate) != 2: return False
        return Hex.is_in_boundary(coordinate[0], coordinate[1])
    

    def __init__(self, r: int = None, q: int = None, coordinate: tuple = None):
        if coordinate:
            if not Hex.is_valid_coordinate(coordinate):
                exit_with_error("Error in Hex.__init__(): invalid coordinate.")
            self.r = coordinate[0]
            self.q = coordinate[1]
        else:
            if not Hex.is_in_boundary(r, q):
                exit_with_error("Error in Hex.__init__(): r or q out of boundaries.")
            self.r = r
            self.q = q
        
    def to_tuple(self):
        return (self.r, self.q)

    def __str__(self):
        return str(self.to_tuple())

    @staticmethod
    def dist(hex_1, hex_2):
        """
        Hexagonal manhattan distance between two hex coordinates.
        """
        delta_r = hex_1.r - hex_2.r
        delta_q = hex_1.q - hex_2.q
        return (abs(delta_r) + abs(delta_q) + abs(delta_r + delta_q)) // 2

    def __add__(self, other):
        # this special method is called when two Hex objects are added with +
        return Hex(self.r + other.r, self.q + other.q)
    
    def __eq__(self, other):
        return self.r == other.r and self.q == other.q
    
    def __ne__(self, other):
        return self.r != other.r or self.q != other.q

    def __hash__(self):
        return hash((self.r, self.q))
    
    def adjacents(self):
        """
        Creates a set of neighbouring coordinates to self's coordinate (r,q)
        """
        output = set({})
        r = self.r
        q = self.q
        for item in set({(r+1, q-1),(r+1,q),(r,q+1),(r-1,q+1),(r-1,q),(r,q-1)}):
            if Hex.is_valid_coordinate(item):
                output.add(Hex(coordinate=item))
        return output


class Map:
    HEX_STEPS = [Hex(r, q) for r, q in [(1,-1),(1,0),(0,1),(-1,1),(-1,0),(0,-1)]]
    ALL_HEXES = frozenset(Hex(r, q) for r in Rules.HEX_RANGE for q in Rules.HEX_RANGE if -r-q in Rules.HEX_RANGE)

    _ORD_HEXES = [(r, q) for r in Rules.HEX_RANGE for q in Rules.HEX_RANGE if -r - q in Rules.HEX_RANGE]
    _SET_HEXES = frozenset(_ORD_HEXES)



class Token:
    PAPER = Rules.PAPER
    ROCK = Rules.ROCK
    SCISSOR = Rules.SCISSOR

    hex:    Hex
    symbol: str
    # id: int
    
    BEATS_WHAT = {'r': 's', 'p': 'r', 's': 'p'}
    WHAT_BEATS = {'r': 'p', 'p': 's', 's': 'r'}

    def __init__(self, hex: Hex, symbol: str):
        if symbol not in Rules.VALID_SYMBOLS:
            exit_with_error("Error in Token.__init__(): invalid token symbol.")
        self.hex = hex
        self.symbol = symbol
    
    def to_tuple(self):
        return (self.hex.to_tuple(), self.symbol)
    
    def __str__(self):
        return str(self.to_tuple())

    def move(self, new_hex: Hex):
        self.hex = new_hex

    def is_paper(self):
        return self.symbol == Token.PAPER

    def is_rock(self):
        return self.symbol == Token.ROCK

    def is_scissor(self):
        return self.symbol == Token.SCISSOR

    def beats_what(self):
        return Token.BEATS_WHAT[self.symbol]

    def what_beats(self):
        return Token.WHAT_BEATS[self.symbol]

    def dist(self, other_hex: Hex = None, other_token = None):
        if other_hex != None:
            return Hex.dist(self.hex, other_hex)
        if other_token != None:
            return Hex.dist(self.hex, other_token.hex)
        exit_with_error("Error in Token.dist(): no arguments were given.")

    def find_closest_token(self, tokens: list):
        if tokens is None: return None
        if len(tokens) == 0: return None
        closest = None
        min = -1
        for token in tokens:
            dist = self.dist(other_token = token)
            if min == -1 or dist < min:
                min = dist  
                closest = token     
        return closest



class Action:
    THROW = Rules.THROW
    SLIDE = Rules.SLIDE
    SWING = Rules.SWING

    action_type: str
    token_symbol: str
    from_hex: Hex
    to_hex: Hex
        
    @staticmethod
    def check_valid_action_tuple(action_tuple: tuple):
        # check format of action_tuple
        if not action_tuple: return False
        if len(action_tuple) != 3: return False
        # check 1st argument
        if action_tuple[0] not in Rules.VALID_ACTIONS: return False
        #check 2nd argument
        if action_tuple[0] == Action.THROW:
            if action_tuple[1] not in Rules.VALID_SYMBOLS: return False
        else:
            if not (is_tuple(action_tuple[1])): return False
            if not Hex.is_valid_coordinate(action_tuple[1]): return False
        #check 3rd argument
        if not (is_tuple(action_tuple[2])): return False
        if not Hex.is_valid_coordinate(action_tuple[2]): return False
        return True

    def __init__(self, action_type: str = None, token_symbol: str = None, from_hex: Hex = None, to_hex: Hex = None, action_tuple: tuple = None):

        # If we were not given an action_tuple, we will create one from the other arguments that are supposed to be given
        # Otherwise continue
        if not action_tuple:
            if not action_type in Rules.VALID_ACTIONS:
                exit_with_error("Error in Action.__init__(): invalid action_type.")
            # convert from_hex and to_hex into tuples inside of Hexes so that we could use check_valid_action_tuple() function
            if from_hex: from_hex = from_hex.to_tuple()
            if to_hex: to_hex = to_hex.to_tuple()
            # create the action_tuple so we can test its validity
            action_tuple = (action_type, token_symbol, to_hex) if (action_type == Action.THROW) else (action_type, from_hex, to_hex)
        
        # Here we have an action_tuple, we need to check that it's valid
        if not Action.check_valid_action_tuple(action_tuple):
            print(action_tuple)
            print("Error in Action.__init__(): invalid input arguments.")
            exit(1)
        # Here our action_tuple is valid and is ready to be turned into an Action object
        self.action_type = action_tuple[0]
        self.to_hex = Hex(coordinate = action_tuple[2])
        if action_tuple[0] == Action.THROW:
            self.token_symbol = action_tuple[1]
        else:
            self.from_hex = Hex(coordinate = action_tuple[1])

    def is_throw(self):
        return self.action_type == Action.THROW

    def is_slide(self):
        return self.action_type == Action.SLIDE

    def is_swing(self):
        return self.action_type == Action.SWING

    def to_tuple(self):
        if self.is_throw():
            return (self.action_type, self.token_symbol, self.to_hex.to_tuple())
        else:
            return (self.action_type, self.from_hex.to_tuple(), self.to_hex.to_tuple())

    def __str__(self):
        return str(self.to_tuple())
