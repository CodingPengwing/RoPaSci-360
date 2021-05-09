from cooked_pancakes.foundations import *
import random

UPPER = Rules.UPPER
LOWER = Rules.LOWER

class Team:
    team_name: str
    throws_remaining: int
    active_tokens: list

    # Hold the last 5 moves that we made
    previous_moves: list

    def __init__(self, team_name: str):
        self.team_name = team_name
        self.throws_remaining = Rules.MAX_THROWS
        self.active_tokens = []
        self.previous_moves = []

    def __str__(self):
        return "Team " + self.team_name + ", " + "throws_remaining: " + str(self.throws_remaining) + "\nActive tokens: " + str(self.active_tokens)

     
    def get_token_at(self, hex: Hex):
        """ Returns the first token found at specified hex for this team. """
        for token in self.active_tokens:
            if token.hex == hex:
                return token
        return None

    def get_tokens_at(self, hex: Hex):
        """ Returns all the tokens found at specified hex for this team. """
        return [token for token in self.active_tokens if token.hex == hex]

    def exists_token_at(self, hex: Hex):
        """Check if there exists a token at specified hex for this team."""
        if self.get_token_at(hex):
            return True
        return False

    def has_active_token(self, token_symbol: str):
        for token in self.active_tokens:
            if token.symbol == token_symbol:
                return True
        return False

    def get_rock_tokens(self):
        return [token for token in self.active_tokens if token.symbol == Token.ROCK]

    def get_paper_tokens(self):
        return [token for token in self.active_tokens if token.symbol == Token.PAPER]

    def get_scissor_tokens(self):
        return [token for token in self.active_tokens if token.symbol == Token.SCISSOR]

    def get_num_rock(self):
        return len(self.get_rock_tokens())

    def get_num_paper(self):
        return len(self.get_paper_tokens())

    def get_num_scissor(self):
        return len(self.get_scissor_tokens())

    def get_tokens_of_type(self, token_type: str):
        if token_type not in Rules.VALID_SYMBOLS:
            exit_with_error("Error in Team.get_tokens_of_type(): token_type invalid.")
        if token_type == Token.ROCK:
            return self.get_rock_tokens()
        if token_type == Token.PAPER:
            return self.get_paper_tokens()
        if token_type == Token.SCISSOR:
            return self.get_scissor_tokens()

    def get_num_dups(self, token_type: str):
        return len(self.get_tokens_of_type(token_type))

    def decrease_throw(self):
        self.throws_remaining -= 1

    def first_move(self):
        s = [Token.ROCK, Token.PAPER, Token.SCISSOR]
        i = random.randint(0,2)
        reach = max(Rules.HEX_RANGE)
        throw_hex = Hex(reach,-(reach)/2)
        if self.team_name == UPPER:
            return Action(action_type = Action.THROW, token_symbol = s[i], to_hex = throw_hex)
        if self.team_name == LOWER:
            throw_hex.invert()
            return Action(action_type = Action.THROW, token_symbol = s[i], to_hex = throw_hex)

    def generate_actions(self, team_dict: dict):
        """
        Generate all available actions.
        """
        for team_name in Rules.VALID_TEAMS:
            if team_name not in team_dict:
                exit_with_error("Error in Team.generate_actions(): incorrect team_dict dictionary format.")
        xs = [x.hex for x in self.active_tokens]
        occupied_hexes = set(xs)

        def _move_actions(self, x: Hex):
            actions = []
            adjacents_x = set(x.adjacents())
            for y in adjacents_x:
                actions.append(Action(action_type = "SLIDE", from_hex = x, to_hex = y))
                if y in occupied_hexes:
                    opposites_y = y.adjacents() - adjacents_x - {x}
                    for z in opposites_y:
                        actions.append(Action(action_type="SWING", from_hex = x, to_hex =z))
            # print(f'slides/swings: {len(actions)}')
            return actions

        def _throw_actions(self):
            throws = Rules.MAX_THROWS - self.throws_remaining
            throw_actions = []
            if throws < 9:
                sign = -1 if self.team_name == LOWER else 1
                radius_range = Rules.HEX_RADIUS - 1
                throw_zone = {Hex(r, q) for r, q in Map._SET_HEXES if (sign * r >= radius_range - throws)}
                for x in throw_zone:
                    _s = list(Rules.VALID_SYMBOLS)[random.randint(0,2)]
                    throw_actions.append(Action(action_type = Action.THROW, token_symbol=_s, to_hex = x))
            # print(f'throws: {len(throw_actions)}')
            return throw_actions
                
        actions = []
        
        for x in xs:
            actions += _move_actions(self,x)
        actions += _throw_actions(self)
        # print(actions)
        # print(len(actions))
        return actions

