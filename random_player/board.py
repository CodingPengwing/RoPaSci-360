import itertools
import copy
from random_player.team import Team
from cooked_pancakes.foundations import *
from cooked_pancakes.gametheory import solve_game
from cooked_pancakes.util import exit_with_error

UPPER = Rules.UPPER
LOWER = Rules.LOWER

class Board:
    team_upper: Team
    team_lower: Team
    team_dict: dict
    upper_tokens: list
    lower_tokens: list

    def __init__(self, team_upper: Team = None, team_lower: Team = None):

        if team_upper is not None and team_lower is not None:
            self.team_upper = copy.deepcopy(team_upper)
            self.team_lower = copy.deepcopy(team_lower)
        else:
            if team_upper is not None or team_lower is not None:
                exit_with_error("Error in Board.__init__(): one of the arguments (team_upper/team_lower) is None.")
            self.team_upper = Team(UPPER)
            self.team_lower = Team(LOWER)

        self.team_dict = {UPPER: self.team_upper, LOWER: self.team_lower}
        self.upper_tokens = self.team_upper.active_tokens
        self.lower_tokens = self.team_lower.active_tokens

     
    def get_team(self, team_name: str):
        if team_name not in self.team_dict:
            exit_with_error("Error in Board.get_team(): team name undefined.")
        return self.team_dict[team_name]
    
    def __str__(self):
        return str(self.team_upper) + "\n" + str(self.team_lower)


    def successor(self, actions: dict):
        if (UPPER not in actions or LOWER not in actions):
            exit_with_error("Error in Board.successor(): incorrect actions dictionary format.")

        for team_name in actions:
            team = self.team_dict[team_name]
            action = actions[team_name]
            if action.is_throw():
                new_token = Token(action.to_hex, action.token_symbol)
                team.active_tokens.append(new_token)
                team.decrease_throw()
            else:
                to_move = team.get_token_at(action.from_hex)
                to_move.move(action.to_hex)  

        # where tokens clash, do battle
        # TODO: only necessary to check this at destinations of actions
        # (but then will have to find another way to fill the lists)
        safe_upper_tokens = []
        safe_lower_tokens = []
        for x in Map.ALL_HEXES:
            ups_at_x = [t for t in self.upper_tokens if t.hex == x]
            lws_at_x = [t for t in self.lower_tokens if t.hex == x]
            symbols = {t.symbol for t in ups_at_x + lws_at_x}
            if len(symbols) > 1:
                for _s in symbols:
                    k = Token.BEATS_WHAT[_s]
                    ups_at_x = [t for t in ups_at_x if t.symbol != k]
                    lws_at_x = [t for t in lws_at_x if t.symbol != k]
            safe_upper_tokens.extend(ups_at_x)
            safe_lower_tokens.extend(lws_at_x)

        self.team_upper.active_tokens = safe_upper_tokens
        self.team_lower.active_tokens = safe_lower_tokens
        self.upper_tokens = self.team_upper.active_tokens
        self.lower_tokens = self.team_lower.active_tokens

    def get_tokens(self, team_name: str, token_type: str):
        if team_name not in self.team_dict or token_type not in Rules.VALID_SYMBOLS:
            exit_with_error("Error in Board.get_tokens(): invalid inputs.")
        return [token for token in self.team_dict[team_name].active_tokens if token.symbol == token_type]
