import itertools
import math
import copy
from cooked_pancakes.team import Team
from cooked_pancakes.foundations import *
from cooked_pancakes.gametheory import solve_game
from cooked_pancakes.util import exit_with_error, is_type


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
            self.team_upper = Team(team_name = UPPER, active_tokens=team_upper.active_tokens, throws_remaining=team_upper.throws_remaining)
            self.team_lower = Team(team_name = LOWER, active_tokens=team_lower.active_tokens, throws_remaining=team_lower.throws_remaining)
            # self.team_upper = copy.deepcopy(team_upper)
            # self.team_lower = copy.deepcopy(team_lower)
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
    

    def successor(self, actions: dict):
        for team_name in Rules.VALID_TEAMS:
            if team_name not in actions:
                exit_with_error("Error in Team.generate_dangerous_hexes(): incorrect team_dict format.")
            if not is_type(actions[team_name], Action):
                exit_with_error("Error in Team.generate_dangerous_hexes(): incorrect team_dict format.")        

        for team_name in actions:
            team = self.team_dict[team_name]
            action = actions[team_name]
            if action.is_throw():
                new_token = Token(action.to_hex, action.token_symbol)
                team.active_tokens.append(new_token)
                team.decrease_throw()
            else:
                to_move = team.get_token_at(action.from_hex)
                # print(action.from_hex)
                # print(to_move)
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

    def evaluate_token(self, token: Token, team_name: str):
        score = 0
        WEIGHT = 1/4

        opp_team = self.team_upper if (team_name == LOWER) else self.team_lower

        closest_defeatable = token.find_closest_token(opp_team.get_tokens_of_type(token.beats_what()))
        closest_defeated_by = token.find_closest_token(opp_team.get_tokens_of_type(token.what_beats()))
         
        if closest_defeatable:
            assert(Hex.dist(token.hex, closest_defeatable.hex)+1 > 0)
            score -= math.log(Hex.dist(token.hex, closest_defeatable.hex)+1)
        
        if closest_defeated_by:
            # print(token.symbol)
            # print(token.hex)
            # print(closest_defeated_by.hex)
            assert(Hex.dist(token.hex, closest_defeated_by.hex)+1 > 0)
            score += WEIGHT * math.log(Hex.dist(token.hex, closest_defeated_by.hex)+1)

        return score


    def evaluate(self, team: Team):
        score = 0
        opp_team = self.team_upper if (team.team_name == LOWER) else self.team_lower
        
        closest_kill, kill_dist = team.determine_closest_kill(self.team_dict)
        closest_threat, threat_dist = team.determine_closest_threat(self.team_dict)

        if kill_dist > 0:
            score -= kill_dist
        if threat_dist >0:
            score += (1/2) * threat_dist

        score += team.throws_remaining * 1
        score += (Rules.MAX_THROWS - opp_team.throws_remaining) - len(opp_team.active_tokens)
        score -= ((Rules.MAX_THROWS - team.throws_remaining) - len(team.active_tokens))
        

        return score

    # def evaluate(self, team: Team):
    #     score = 0
    #     opp_team = self.team_upper if (team.team_name == LOWER) else self.team_lower

    #     for token in team.active_tokens:
    #         score += self.evaluate_token(token, team.team_name)
        
    #     opp_total_active = len(opp_team.active_tokens)
    #     opp_num_invincible = opp_total_active
    #     for _s in Rules.VALID_SYMBOLS:
    #         our_same = team.get_tokens_of_type(_s)
    #         if len(our_same) == 0:
    #             continue
            
    #         opp_defeatable = opp_team.get_tokens_of_type(Token.BEATS_WHAT[_s])
    #         opp_defeated_by = opp_team.get_tokens_of_type(Token.WHAT_BEATS[_s])
    #         score += 2 - len(our_same) + len(opp_defeatable) - len(opp_defeated_by)
    #         opp_num_invincible -= len(opp_defeatable)
        

    #     # score += team.throws_remaining
    #     # score -= len(team.active_tokens)
    #     # Throws
    #     # score += (team.throws_remaining - opp_team.throws_remaining) * 5

    #     # Total opponent defeatable v/s invincible
    #     # score += (opp_total_active - opp_num_invincible) * 5
    #     score -= opp_num_invincible 
    #     score += team.throws_remaining 
    #     score += len(team.active_tokens) 

    #     # score -= ((Rules.MAX_THROWS - team.throws_remaining) - len(team.active_tokens)) * 5

        
    #     """
    #     CALCULATE DISTANCE TO ONE KILLABLE ENEMY TOKEN ONLY, NOT EVERY KILLABLE
    #     CALCULATE NUMBER OF ROCKS V OPP PAPERS, SCISSORS, ETC...
    #     EVERY PAIR OF FRIENDLY TOKENS NEXT TO EACH OTHER SHOULD GET BONUS SCORE
    #     """

    #     '''
    #     IMPLEMENT THIS
    #     '''
    #     # Difference between number of active opponent tokens versus throws left
    #     score += (Rules.MAX_THROWS - opp_team.throws_remaining) - len(opp_team.active_tokens) 
    #     # score -= (Rules.MAX_THROWS - team.throws_remaining) - len(team.active_tokens) 

    #     return score

    # def compute_utility_matrix(self, team: Team):
    #     # generate all pairings of actions for the 2 players 
    #     upper_actions = self.team_upper.generate_actions(self.team_dict)
    #     lower_actions = self.team_lower.generate_actions(self.team_dict)
    #     # actions = itertools.product(upper_actions, lower_actions)
        
    #     # for each pairing of actions, create a new "board" 
    #     V = []
    #     for i in range(len(upper_actions)):
    #         V_i = []
    #         for j in range(len(lower_actions)):
    #             actions_pair = {UPPER: upper_actions[i], LOWER: lower_actions[j]}
    #             new_board = Board(team_upper = self.team_upper, team_lower = self.team_lower)
    #             new_board.successor(actions_pair)
    #             V_i.append((new_board, actions_pair))
    #         V.append(V_i)
        
    #     # Evaluate the board
    #     Z_ups = []
    #     Z_lws = []
    #     actions_matrix = []
    #     for i in range(len(V)):
    #         Z_ups_i = []
    #         Z_lws_i = []
    #         # Z_i = []
    #         A_i = []
    #         for j in range(len(V[i])):
    #             # Z_ij = []
    #             state = V[i][j][0]
    #             actions_pair = V[i][j][1]
    #             team_upper_score = state.evaluate(state.team_upper)
    #             team_lower_score = state.evaluate(state.team_lower)

    #             # Z_ij = (team_upper_score, team_lower_score)
    #             # Z_ij = team_upper_score - team_lower_score if team.team == UPPER else team_lower_score - team_upper_score

    #             Z_ups_i.append(team_upper_score)
    #             Z_lws_i.append(team_lower_score)
    #             # Z_i.append(Z_ij)
    #             A_i.append(actions_pair)

    #         # Z.append(Z_i)
    #         Z_ups.append(Z_ups_i)
    #         Z_lws.append(Z_lws_i)
    #         actions_matrix.append(A_i)


    #     """PRUNE OUT ALL STRICTLY DOMINATED STRATEGIES IN THIS MATRIX FOR BOTH PLAYERS"""
    #     """CHECK FOR WEAKLY DOMINATED STRATEGIES"""

    #     Z = {UPPER: Z_ups, LOWER: Z_lws}
    #     # print_pretty(Z)
    #     return Z, actions_matrix



    # def find_nash_equilibrium(self):

    #     return nash_equilibrium

    def print_board(self, board_dict, message="", compact=True, ansi=False, **kwargs):
        """
        For help with visualisation and debugging: output a board diagram with
        any information you like (tokens, heuristic values, distances, etc.).
        Arguments:
        board_dict -- A dictionary with (r, q) tuples as keys (following axial
            coordinate system from specification) and printable objects (e.g.
            strings, numbers) as values.
            This function will arrange these printable values on a hex grid
            and output the result.
            Note: At most the first 5 characters will be printed from the string
            representation of each value.
        message -- A printable object (e.g. string, number) that will be placed
            above the board in the visualisation. Default is "" (no message).
        ansi -- True if you want to use ANSI control codes to enrich the output.
            Compatible with terminals supporting ANSI control codes. Default
            False.
        compact -- True if you want to use a compact board visualisation,
            False to use a bigger one including axial coordinates along with
            the printable information in each hex. Default True (small board).
        
        Any other keyword arguments are passed through to the print function.
        Example:
            >>> board_dict = {
            ...     ( 0, 0): "hello",
            ...     ( 0, 2): "world",
            ...     ( 3,-2): "(p)",
            ...     ( 2,-1): "(S)",
            ...     (-4, 0): "(R)",
            ... }
            >>> print_board(board_dict, "message goes here", ansi=False)
            # message goes here
            #              .-'-._.-'-._.-'-._.-'-._.-'-.
            #             |     |     |     |     |     |
            #           .-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
            #          |     |     | (p) |     |     |     |
            #        .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
            #       |     |     |     | (S) |     |     |     |
            #     .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
            #    |     |     |     |     |     |     |     |     |
            #  .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
            # |     |     |     |     |hello|     |world|     |     |
            # '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
            #    |     |     |     |     |     |     |     |     |
            #    '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
            #       |     |     |     |     |     |     |     |
            #       '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
            #          |     |     |     |     |     |     |
            #          '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
            #             | (R) |     |     |     |     |
            #             '-._.-'-._.-'-._.-'-._.-'-._.-'
        """
        if compact:
            template = """# {00:}
    #              .-'-._.-'-._.-'-._.-'-._.-'-.
    #             |{57:}|{58:}|{59:}|{60:}|{61:}|
    #           .-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
    #          |{51:}|{52:}|{53:}|{54:}|{55:}|{56:}|
    #        .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
    #       |{44:}|{45:}|{46:}|{47:}|{48:}|{49:}|{50:}|
    #     .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
    #    |{36:}|{37:}|{38:}|{39:}|{40:}|{41:}|{42:}|{43:}|
    #  .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
    # |{27:}|{28:}|{29:}|{30:}|{31:}|{32:}|{33:}|{34:}|{35:}|
    # '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
    #    |{19:}|{20:}|{21:}|{22:}|{23:}|{24:}|{25:}|{26:}|
    #    '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
    #       |{12:}|{13:}|{14:}|{15:}|{16:}|{17:}|{18:}|
    #       '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
    #          |{06:}|{07:}|{08:}|{09:}|{10:}|{11:}|
    #          '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
    #             |{01:}|{02:}|{03:}|{04:}|{05:}|
    #             '-._.-'-._.-'-._.-'-._.-'-._.-'"""
        else:
            template = """# {00:}
    #                  ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
    #                 | {57:} | {58:} | {59:} | {60:} | {61:} |
    #                 |  4,-4 |  4,-3 |  4,-2 |  4,-1 |  4, 0 |
    #              ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
    #             | {51:} | {52:} | {53:} | {54:} | {55:} | {56:} |
    #             |  3,-4 |  3,-3 |  3,-2 |  3,-1 |  3, 0 |  3, 1 |
    #          ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
    #         | {44:} | {45:} | {46:} | {47:} | {48:} | {49:} | {50:} |
    #         |  2,-4 |  2,-3 |  2,-2 |  2,-1 |  2, 0 |  2, 1 |  2, 2 |
    #      ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
    #     | {36:} | {37:} | {38:} | {39:} | {40:} | {41:} | {42:} | {43:} |
    #     |  1,-4 |  1,-3 |  1,-2 |  1,-1 |  1, 0 |  1, 1 |  1, 2 |  1, 3 |
    #  ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
    # | {27:} | {28:} | {29:} | {30:} | {31:} | {32:} | {33:} | {34:} | {35:} |
    # |  0,-4 |  0,-3 |  0,-2 |  0,-1 |  0, 0 |  0, 1 |  0, 2 |  0, 3 |  0, 4 |
    #  `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
    #     | {19:} | {20:} | {21:} | {22:} | {23:} | {24:} | {25:} | {26:} |
    #     | -1,-3 | -1,-2 | -1,-1 | -1, 0 | -1, 1 | -1, 2 | -1, 3 | -1, 4 |
    #      `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
    #         | {12:} | {13:} | {14:} | {15:} | {16:} | {17:} | {18:} |
    #         | -2,-2 | -2,-1 | -2, 0 | -2, 1 | -2, 2 | -2, 3 | -2, 4 |
    #          `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
    #             | {06:} | {07:} | {08:} | {09:} | {10:} | {11:} |
    #             | -3,-1 | -3, 0 | -3, 1 | -3, 2 | -3, 3 | -3, 4 |   key:
    #              `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'     ,-' `-.
    #                 | {01:} | {02:} | {03:} | {04:} | {05:} |       | input |
    #                 | -4, 0 | -4, 1 | -4, 2 | -4, 3 | -4, 4 |       |  r, q |
    #                  `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'         `-._,-'"""
        # prepare the provided board contents as strings, formatted to size.
        reach = Rules.HEX_RANGE
        cells = []
        for rq in [(r,q) for r in reach for q in reach if -r-q in reach]:
            if rq in board_dict and board_dict[rq]:
                cell = ""
                for token in board_dict[rq]:
                    cell = cell + str(token) + ','
                cell = cell[:-1].center(5)
                if ansi:
                    # put contents in bold
                    cell = f"\033[1m{cell}\033[0m"
            else:
                cell = "     " # 5 spaces will fill a cell
            cells.append(cell)
        # prepare the message, formatted across multiple lines
        multiline_message = "\n# ".join(message.splitlines())
        # fill in the template to create the board drawing, then print!
        board = template.format(multiline_message, *cells)
        print(board, **kwargs)



    def __str__(self):
        print(self.team_upper)
        print(self.team_lower)

        board_dict = {}
        for team_name in self.team_dict:
            team = self.team_dict[team_name]
            if not team.active_tokens: continue
            for token in team.active_tokens:
                _s = token.symbol
                if team_name == UPPER: _s = _s.upper()
                position = token.hex.to_tuple()
                if position in board_dict:
                    board_dict[position].append(_s)
                else:
                    board_dict[position] = [_s]

        self.print_board(board_dict, compact=True)
        return ''