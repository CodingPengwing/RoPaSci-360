import itertools
import math
import copy
from cooked_pancakes.team import Team
from cooked_pancakes.foundations import *
from cooked_pancakes.gametheory import solve_game
from cooked_pancakes.util import exit_with_error, is_type
from cooked_pancakes.astar_search import find_path_length


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


    # def evaluate(self, team: Team):
    #     score = 0
    #     opp_team = self.team_upper if (team.team_name == LOWER) else self.team_lower
        
    #     closest_kill, kill_dist = team.determine_closest_kill(self.team_dict)
    #     closest_threat, threat_dist = team.determine_closest_threat(self.team_dict)

    #     if kill_dist > 0:
    #         score -= kill_dist
    #     if threat_dist > 0:
    #         score += (1/2) * threat_dist

    #     score += team.throws_remaining * 1
    #     score += (Rules.MAX_THROWS - opp_team.throws_remaining) - len(opp_team.active_tokens)
    #     score -= ((Rules.MAX_THROWS - team.throws_remaining) - len(team.active_tokens))
        
    #     return score


    def evaluate(self, team: Team):
        score = 0
        enemy_team = self.team_upper if (team.team_name == LOWER) else self.team_lower

        enemy_defeatable = team.generate_enemy_defeatable(self.team_dict)
        enemy_defeated_by = team.generate_enemy_defeated_by(self.team_dict)

        score += team.throws_remaining * 1
        score += len(team.active_tokens)
        if team.get_num_dups(Rules.ROCK):
            score = score - team.get_num_dups(Rules.ROCK) + 1
        if team.get_num_dups(Rules.PAPER):
            score = score - team.get_num_dups(Rules.PAPER) + 1
        if team.get_num_dups(Rules.SCISSOR):
            score = score - team.get_num_dups(Rules.SCISSOR) + 1

        weight_dist = {0: 1.22, 1: 1, 2: 0.80, 3: 0.62, 4: 0.46, 5: 0.32, 6: 0.20, 7: 0.10, 8: 0.02, 9: 0}
        for token in team.active_tokens:
            if enemy_defeatable[token.symbol]:
                for enemy_token in enemy_defeatable[token.symbol]:
                    path_length = find_path_length(self.team_dict, team.team_name, token, enemy_token)
                    if path_length:
                        dist_kill = path_length - 1
                        if dist_kill < 10: weight = weight_dist[dist_kill]
                        else: weight = 0
                        score += ((9 - dist_kill) * weight)
            if enemy_defeated_by[token.symbol]:
                for enemy_token in enemy_defeated_by[token.symbol]:
                    path_length = find_path_length(self.team_dict, team.team_name, token, enemy_token)
                    if path_length:
                        dist_threat = path_length - 1
                        if dist_threat < 10: weight = weight_dist[dist_threat]
                        else: weight = 0
                        score += (dist_threat * weight)

        enemy_active = len(enemy_team.active_tokens)
        enemy_num_defeatable = sum([len(enemy_defeatable[_s]) for _s in Rules.VALID_SYMBOLS])
        enemy_num_invincible = enemy_active - enemy_num_defeatable
        
        score += (9 - enemy_num_invincible) * 1.5

        """
        score += throws_remaining * 1.1
        score += tokens_active
        if find_num_dups(R)
            score -= find_num_dups(R) + 1
        if find_num_dups(P)
            score -= find_num_dups(P) + 1
        if find_num_dups(S)
            score -= find_num_dups(S) + 1

        weight_dist = {1: 1, 2: 0.80, 3: 0.62, 4: 0.46, 5: 0.32, 6: 0.20, 7: 0.10, 8: 0.02, 9: 0}
        if token_kills: (make find_token_kills)
            score += (9 - dist_kill) * weight_dist[dist_kill]
        if token_threats: (make find_token_threats)
            score += (dist_threat) * weight_dist[dist_threat]
            

        RUN:
        only run when opponent is within 3 steps
        if there is an overlap in run and attack, take that
        if there is no attack, find opponent token of the same type
        if standing on opponent token of same type: safe, do not move unless there is a target to kill


        CUT IN GREEDYS PATH: 
        if already in path, move towards kill, else cut the way.
        if next to target and haven't killed this target in 3 turns, try different method.
        score 
        """

        return score

        

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