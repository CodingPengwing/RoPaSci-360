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
        print(self.team_upper)
        print(self.team_lower, end='')
        return ''

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
        WEIGHT = 1

        opp_team = self.team_upper if (team_name == LOWER) else self.team_lower

        closest_defeatable = token.find_closest_token(opp_team.get_tokens_of_type(token.beats_what()))
        closest_defeated_by = token.find_closest_token(opp_team.get_tokens_of_type(token.what_beats()))
         
        if closest_defeatable:
            assert(Hex.dist(token.hex, closest_defeatable.hex) > 0)
            score -= math.log(Hex.dist(token.hex, closest_defeatable.hex))
        
        if closest_defeated_by:
            assert(Hex.dist(token.hex, closest_defeated_by.hex) > 0)
            score += WEIGHT * math.log(Hex.dist(token.hex, closest_defeated_by.hex))

        return score


    def evaluate(self, team:Team):
        score = 0
        opp_team = self.team_upper if (team.team_name == LOWER) else self.team_lower

        for token in team.active_tokens:
            score += self.evaluate_token(token, team.team_name)
        
        opp_total_active = len(opp_team.active_tokens)
        opp_num_invincible = opp_total_active
        for _s in Rules.VALID_SYMBOLS:
            our_same = team.get_tokens_of_type(_s)
            if len(our_same) == 0:
                continue
            
            opp_defeatable = opp_team.get_tokens_of_type(Token.BEATS_WHAT[_s])
            opp_defeated_by = opp_team.get_tokens_of_type(Token.WHAT_BEATS[_s])
            score += 2 - len(our_same) + len(opp_defeatable) - len(opp_defeated_by)
            opp_num_invincible -= len(opp_defeatable)
        
        # Throws
        score += team.throws_remaining - opp_team.throws_remaining

        # Total opponent defeatable v/s invincible
        score += (opp_total_active - opp_num_invincible)
        score -= opp_num_invincible

        '''
        IMPLEMENT THIS
        '''
        # Difference between number of active opponent tokens versus throws left
        score += (Rules.MAX_THROWS - opp_team.throws_remaining) - len(opp_team.active_tokens) 

        return score


    # def evaluate(self, team: Team, action: Action):

    #     score = 0
    #     # Penalty for throw action
    #     if action.is_throw():
    #         # dup_count = team.get_num_dups(action.token_symbol)
    #         # total_tokens = len(team.active_tokens)
            
    #         # If no defeatable pieces
            
    #         score -= (Rules.MAX_THROWS - team.throws_remaining)
    #         # if total_tokens == 1:
    #         #     '''WORK ON THIS'''
    #         #     score += 1
    #         # elif total_tokens != 0:
    #         #     score -= ((Rules.MAX_THROWS - team.throws_remaining)/Rules.MAX_THROWS + (dup_count/total_tokens))

    #     # Distances 

    #     for token in team.active_tokens:
    #         score += self.evaluate_token(token,team.team)

    #     return score*100

    # def evaluate(self, team: Team):
    #     """IMPLEMENT PREVIOUS STATE COMPARISON"""
    #     """
    #     score = throws_rem + active_tokens + negative_distance_ to killable tokens + positive distance from dangerous tokens
    #     throws_rem * 10
    #     active_tokens * 10
    #     """
    #     team_name = team.team_name
    #     enemy_team = [self.team_dict[i] for i in self.team_dict if i != team_name][0]
    #     scr_throws_rem = team.throws_remaining * 10
    #     scr_active_toks = len(team.active_tokens) * 10

    #     def calculate_killable_enemies_score(self, token: Token):
    #         if not is_type(token, Token): 
    #             exit_with_error("Error in Board.evaluate().calculate_killable...(): input is not a Token")
    #         score = 0
    #         killable_type = token.beats_what()
    #         killable_enemies = enemy_team.get_tokens_of_type(killable_type)
    #         for enemy in killable_enemies:
    #             score -= token.dist(other_token=enemy)
    #         return score

    #     def calculate_dangerous_enemies_score(self, token: Token):
    #         if not is_type(token, Token): 
    #             exit_with_error("Error in Board.evaluate().calculate_dangerous...(): input is not a Token")
    #         score = 0
    #         dangerous_type = token.what_beats()
    #         dangerous_enemies = enemy_team.get_tokens_of_type(dangerous_type)
    #         for enemy in dangerous_enemies:
    #             score += token.dist(other_token=enemy)
    #         return score


    #     """
    #     CALCULATE DISTANCE TO ONE KILLABLE ENEMY TOKEN ONLY, NOT EVERY KILLABLE
    #     CALCULATE NUMBER OF ROCKS V OPP PAPERS, SCISSORS, ETC...
    #     DISTANCE BETWEEN OUR PIECE AND DANGEROUS ENEMY PIECES SHOULDNT MATTER UNTIL THEY COME WITHIN A 3 DIAMETER
    #     OUTSIDE OF THE 3 DIAMETER, KEEP OUR TOKENS AS CLOSE TO EACH OTHER AS POSSIBLE WHILE APPROACH ENEMIES
    #     (MAYBE HAVE A DIAMETER THRESHOLD FOR ALLY TOKENS BEING FAR AWAY)
        
    #     """

    #     scr_killable_enemies = 0
    #     for token in team.active_tokens:
    #         scr_killable_enemies += calculate_killable_enemies_score(self, token) * 1.5
    #     scr_dangerous_enemies = 0
    #     for token in team.active_tokens:
    #         scr_dangerous_enemies += calculate_dangerous_enemies_score(self, token)

    #     score = scr_throws_rem + scr_active_toks + scr_killable_enemies + scr_dangerous_enemies
    #     return score




    def compute_utility_matrix(self, team: Team):
        # generate all pairings of actions for the 2 players 
        upper_actions = self.team_upper.generate_actions(self.team_dict)
        lower_actions = self.team_lower.generate_actions(self.team_dict)
        # actions = itertools.product(upper_actions, lower_actions)
        
        # for each pairing of actions, create a new "board" 
        V = []
        for i in range(len(upper_actions)):
            V_i = []
            for j in range(len(lower_actions)):
                actions_pair = {UPPER: upper_actions[i], LOWER: lower_actions[j]}
                new_board = Board(team_upper = self.team_upper, team_lower = self.team_lower)
                new_board.successor(actions_pair)
                V_i.append((new_board, actions_pair))
            V.append(V_i)
        
        # Evaluate the board
        Z_ups = []
        Z_lws = []
        actions_matrix = []
        for i in range(len(V)):
            Z_ups_i = []
            Z_lws_i = []
            # Z_i = []
            A_i = []
            for j in range(len(V[i])):
                # Z_ij = []
                state = V[i][j][0]
                actions_pair = V[i][j][1]
                team_upper_score = state.evaluate(state.team_upper)
                team_lower_score = state.evaluate(state.team_lower)

                # Z_ij = (team_upper_score, team_lower_score)
                # Z_ij = team_upper_score - team_lower_score if team.team == UPPER else team_lower_score - team_upper_score

                Z_ups_i.append(team_upper_score)
                Z_lws_i.append(team_lower_score)
                # Z_i.append(Z_ij)
                A_i.append(actions_pair)

            # Z.append(Z_i)
            Z_ups.append(Z_ups_i)
            Z_lws.append(Z_lws_i)
            actions_matrix.append(A_i)


        """PRUNE OUT ALL STRICTLY DOMINATED STRATEGIES IN THIS MATRIX FOR BOTH PLAYERS"""
        """CHECK FOR """

        Z = {UPPER: Z_ups, LOWER: Z_lws}
        # print_pretty(Z)
        return Z, actions_matrix



    # def find_nash_equilibrium(self):

    #     return nash_equilibrium
