from cooked_pancakes.foundations import *
import random

UPPER = Rules.UPPER
LOWER = Rules.LOWER

class Team:
    team_name: str
    throws_remaining: int
    active_tokens: list

    """----> Hold the last 5 moves that we made"""
    previous_moves: list

    """----> Keep track of how many states have passed since we last moved each token."""

    def __init__(self, team_name: str):
        if team_name not in Rules.VALID_TEAMS:
            exit_with_error("Error in Team.__init__(): invalid team_name input.")
        self.team_name = team_name
        self.throws_remaining = Rules.MAX_THROWS
        self.active_tokens = []
        self.previous_moves = []

    def __str__(self):
        print("Team " + self.team_name + ", " + "throws_remaining: " + str(self.throws_remaining) + "\nActive tokens: ", end = '')
        [print(str(token) + ", ", end='') for token in self.active_tokens]
        return ''
     
    def get_token_at(self, hex: Hex):
        """ Returns the first token found at specified hex for this team. """
        if not is_type(hex, Hex):
            exit_with_error("Error in Team.get_token_at(): hex input is not a Hex.")
        for token in self.active_tokens:
            if token.hex == hex:
                return token
        return None

    def get_tokens_at(self, hex: Hex):
        """ Returns all the tokens found at specified hex for this team. """
        if not is_type(hex, Hex):
            exit_with_error("Error in Team.get_tokens_at(): hex input is not a Hex.")
        return [token for token in self.active_tokens if token.hex == hex]

    def exists_token_at(self, hex: Hex):
        """Check if there exists a token at specified hex for this team."""
        if not is_type(hex, Hex):
            exit_with_error("Error in Team.exists_token_at(): hex input is not a Hex.")
        if self.get_token_at(hex):
            return True
        return False

    def has_active_token(self, token_type: str):
        if token_type not in Rules.VALID_SYMBOLS:
            exit_with_error("Error in Team.has_active_token(): token_type invalid.")
        for token in self.active_tokens:
            if token.symbol == token_type:
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
        if token_type not in Rules.VALID_SYMBOLS:
            exit_with_error("Error in Team.get_num_dups(): token_type invalid.")
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

    def generate_occupied_hexes(self):
        xs = [x.hex for x in self.active_tokens]
        occupied_hexes = set(xs)
        return occupied_hexes
    
    def generate_dangerous_hexes(self, team_dict: dict):
        for team_name in Rules.VALID_TEAMS:
            if team_name not in team_dict:
                exit_with_error("Error in Team.generate_dangerous_hexes(): incorrect team_dict dictionary format.")
            if not is_type(team_dict[team_name], Team):
                exit_with_error("Error in Team.generate_dangerous_hexes(): incorrect team_dict dictionary format.")

        enemy = LOWER if self.team_name == UPPER else UPPER
        enemy_rocks = set([x.hex for x in team_dict[enemy].get_rock_tokens()])
        enemy_papers = set([x.hex for x in team_dict[enemy].get_paper_tokens()])
        enemy_scissors = set([x.hex for x in team_dict[enemy].get_scissor_tokens()])
        dangerous_hexes = {Token.ROCK: enemy_papers, Token.PAPER: enemy_scissors, Token.SCISSOR: enemy_rocks}
        return dangerous_hexes

    def _move_actions(self, x: Hex, team_dict: dict):
        for team_name in Rules.VALID_TEAMS:
            if team_name not in team_dict:
                exit_with_error("Error in Team._move_actions(): incorrect team_dict dictionary format.")
            if not is_type(team_dict[team_name], Team):
                exit_with_error("Error in Team._move_actions(): incorrect team_dict dictionary format.")
        if not is_type(x, Hex):
            exit_with_error("Error in Team._move_actions(): x input is not a Hex.")


        occupied_hexes = self.generate_occupied_hexes()
        dangerous_hexes = self.generate_dangerous_hexes(team_dict)
        token = self.get_token_at(x)
        # find all adjacent hexes that are not occupied by ally tokens
        adjacents_x = set(x.adjacents()) - occupied_hexes 
        if token:
            adjacents_x -= dangerous_hexes[token.symbol]
        # find all hexes that are occupied 
        # x_token = self.get_token_at(x)
        actions = []
        for y in adjacents_x:
            actions.append(Action(action_type = "SLIDE", from_hex = x, to_hex = y))
            if y in occupied_hexes:
                opposites_y = y.adjacents() - adjacents_x - occupied_hexes - {x}
                for z in opposites_y:
                    actions.append(Action(action_type="SWING", from_hex = x, to_hex =z))
        # print(f'slides/swings: {len(actions)}')
        # random.shuffle(actions)
        return actions
    
    def generate_throw_zone(self, team_dict: dict, token_type: str):
        for team_name in Rules.VALID_TEAMS:
            if team_name not in team_dict:
                exit_with_error("Error in Team.generate_throw_zone(): incorrect team_dict dictionary format.")
            if not is_type(team_dict[team_name], Team):
                exit_with_error("Error in Team.generate_throw_zone(): incorrect team_dict dictionary format.")
        if token_type not in Rules.VALID_SYMBOLS:
            exit_with_error("Error in Team.generate_throw_zone(): invalid token_type.")

        throws = Rules.MAX_THROWS - self.throws_remaining
        sign = -1 if self.team_name == LOWER else 1
        dangerous_hexes = self.generate_dangerous_hexes(team_dict)
        radius_range = Rules.HEX_RADIUS - 1
        throw_zone = {Hex(r, q) for r, q in Map._SET_HEXES if (sign * r >= radius_range - throws and not self.exists_token_at(Hex(r, q)))}
        throw_zone -= dangerous_hexes[token_type]
        
        return throw_zone
    
    '''
    Only generate like 3 throw actions one for each type
    '''
    def _throw_actions(self, team_dict: dict):
        for team_name in Rules.VALID_TEAMS:
            if team_name not in team_dict:
                exit_with_error("Error in Team._throw_actions(): incorrect team_dict dictionary format.")
            if not is_type(team_dict[team_name], Team):
                exit_with_error("Error in Team._throw_actions(): incorrect team_dict dictionary format.")

        throw_actions = []
        if self.throws_remaining > 0:
            # Only throw this type if we do NOT already have it on the board
            throw_types = {symbol for symbol in Rules.VALID_SYMBOLS if not self.has_active_token(symbol)}
            for _s in throw_types:
                throw_zone = self.generate_throw_zone(team_dict, _s)
                for x in throw_zone:
                    throw_actions.append(Action(action_type = Action.THROW, token_symbol=_s, to_hex = x))
        # print(f'throws: {len(throw_actions)}')
        # random.shuffle(throw_actions)
        return throw_actions

    
    
    def generate_actions(self, team_dict: dict):
        """
        Generate all available actions.
        """
        for team_name in Rules.VALID_TEAMS:
            if team_name not in team_dict:
                exit_with_error("Error in Team.generate_actions(): incorrect team_dict dictionary format.")
            if not is_type(team_dict[team_name], Team):
                exit_with_error("Error in Team.generate_actions(): incorrect team_dict dictionary format.")

        occupied_hexes = self.generate_occupied_hexes()
        actions = []
        for x in occupied_hexes:
            actions += self._move_actions(x, team_dict)
        actions += self._throw_actions(team_dict)
        random.shuffle(actions)
        return actions





    # def generate_good_actions():
    #     """
    #     Good actions include:
    #     - Chasing a killable opponent
    #     - Throwing on a killable opponent
    #     - Running from a dangerous opponent
    #     """
    #     return good_actions


    def determine_closest_kill(self, team_dict: dict):
        for team_name in Rules.VALID_TEAMS:
            if team_name not in team_dict:
                exit_with_error("Error in Team.determine_closest_kill(): incorrect team_dict dictionary format.")
            if not is_type(team_dict[team_name], Team):
                exit_with_error("Error in Team.determine_closest_kill(): incorrect team_dict dictionary format.")

        enemy_team = team_dict[UPPER] if self.team_name == LOWER else team_dict[LOWER]
        closest_pair = None
        min_dist = -1
        
        for token in self.active_tokens:
            enemy_tokens = enemy_team.get_tokens_of_type(token.beats_what())
            
            enemy_token = token.find_closest_token(enemy_tokens)
            if enemy_token:
                dist = token.dist(other_token = enemy_token)
                if min_dist == -1 or dist < min_dist:
                    min_dist = dist
                    closest_pair = (token, enemy_token)
    
        return closest_pair, min_dist

    def determine_best_throw(self, team_dict: dict):
        for team_name in Rules.VALID_TEAMS:
            if team_name not in team_dict:
                exit_with_error("Error in Team.determine_best_throw(): incorrect team_dict dictionary format.")
            if not is_type(team_dict[team_name], Team):
                exit_with_error("Error in Team.determine_best_throw(): incorrect team_dict dictionary format.")

        # Distance of throw zone hexes to enemy tokens
        # Choose minimal distance
        enemy_team = team_dict[UPPER] if self.team_name == LOWER else team_dict[LOWER]
        best_throw = None
        best_throw_symbol = None
        throw_action = None
        min_dist = -1

        if self.throws_remaining == 0:
            return None

        throw_types = {symbol for symbol in Rules.VALID_SYMBOLS if not self.has_active_token(symbol)}
        
        for _s in throw_types:
            throw_zone = self.generate_throw_zone(team_dict, _s)
            for throw in throw_zone:
                killable_enemies = enemy_team.get_tokens_of_type(Token.BEATS_WHAT[_s])
                for enemy in killable_enemies:  
                    dist = Hex.dist(throw, enemy.hex)
                    if min_dist == -1 or dist < min_dist:
                        min_dist = dist
                        best_throw = throw
                        best_throw_symbol = _s
        if best_throw:
            throw_action = Action(action_type = Rules.THROW, token_symbol = best_throw_symbol, to_hex=best_throw)
        
        return throw_action, min_dist




    # def determine_closest_guardian_ally():
    #     # Once you find this, 
    #     return closest_guardian_ally

