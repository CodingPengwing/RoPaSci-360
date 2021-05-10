from cooked_pancakes.foundations import *
import random
import copy
import numpy as np
from cooked_pancakes.astar_search import astar_search, find_attack_moves_for_token

UPPER = Rules.UPPER
LOWER = Rules.LOWER
ATTACK = "attack"
RUN = "run"
OVERLAP = "overlap"

class Team:
    team_name: str
    throws_remaining: int
    active_tokens: list

    def __init__(self, team_name: str, active_tokens: list = None, throws_remaining: int = None):
        if team_name not in Rules.VALID_TEAMS:
            exit_with_error("Error in Team.__init__(): invalid team_name input.")
        
        self.team_name = team_name
        if throws_remaining:
            self.throws_remaining = copy.deepcopy(throws_remaining)
        else:
            self.throws_remaining = Rules.MAX_THROWS
        if active_tokens:
            self.active_tokens = copy.deepcopy(active_tokens)
        else:
            self.active_tokens = []

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

    def has_active_token(self, token_type: str):
        if token_type not in Rules.VALID_SYMBOLS:
            exit_with_error("Error in Team.has_active_token(): token_type invalid.")
        if self.get_tokens_of_type(token_type):
            return True
        return False

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

    def generate_enemy_defeatable(self, team_dict: dict):
        for team_name in Rules.VALID_TEAMS:
            if team_name not in team_dict:
                exit_with_error("Error in Team.generate_enemy_defeatable(): incorrect team_dict dictionary format.")
            if not is_type(team_dict[team_name], Team):
                exit_with_error("Error in Team.generate_enemy_defeatable(): incorrect team_dict dictionary format.")

        enemy_team = team_dict[UPPER] if self.team_name == LOWER else team_dict[LOWER]
        enemy_rocks = enemy_team.get_tokens_of_type(Rules.ROCK)
        enemy_papers = enemy_team.get_tokens_of_type(Rules.PAPER)
        enemy_scissors = enemy_team.get_tokens_of_type(Rules.SCISSOR)
        defeatable_tokens = {Rules.PAPER: enemy_rocks, Rules.ROCK: enemy_scissors, Rules.SCISSOR: enemy_papers}
        return defeatable_tokens

    def generate_enemy_defeated_by(self, team_dict: dict):
        for team_name in Rules.VALID_TEAMS:
            if team_name not in team_dict:
                exit_with_error("Error in Team.generate_enemy_defeated_by(): incorrect team_dict dictionary format.")
            if not is_type(team_dict[team_name], Team):
                exit_with_error("Error in Team.generate_enemy_defeated_by(): incorrect team_dict dictionary format.")

        enemy_team = team_dict[UPPER] if self.team_name == LOWER else team_dict[LOWER]
        enemy_rocks = enemy_team.get_tokens_of_type(Rules.ROCK)
        enemy_papers = enemy_team.get_tokens_of_type(Rules.PAPER)
        enemy_scissors = enemy_team.get_tokens_of_type(Rules.SCISSOR)
        defeated_by_tokens = {Rules.PAPER: enemy_scissors, Rules.ROCK: enemy_papers, Rules.SCISSOR: enemy_rocks}
        return defeated_by_tokens







    '''
    vibe check
    '''





    def _move_actions(self, x: Hex, team_dict: dict):
        for team_name in Rules.VALID_TEAMS:
            if team_name not in team_dict:
                exit_with_error("Error in Team._move_actions(): incorrect team_dict dictionary format.")
            if not is_type(team_dict[team_name], Team):
                exit_with_error("Error in Team._move_actions(): incorrect team_dict dictionary format.")
        if not is_type(x, Hex):
            exit_with_error("Error in Team._move_actions(): x input is not a Hex.")

        token = self.get_token_at(x)

        occupied_hexes = self.generate_occupied_hexes()
        dangerous_hexes = self.generate_dangerous_hexes(team_dict)
        # find all adjacent hexes that are not occupied by ally tokens
        
        adjacents_x = set(x.adjacents()) - occupied_hexes 
        if token:
            adjacents_x -= dangerous_hexes[token.symbol]
            
        # find all hexes that are occupied 
        actions = []
        for y in adjacents_x:
            actions.append(Action(action_type = "SLIDE", from_hex = x, to_hex = y))
            if y in occupied_hexes:
                opposites_y = y.adjacents() - adjacents_x - occupied_hexes - {x}
                if token:
                    opposites_y -= dangerous_hexes[token.symbol]
                for z in opposites_y:
                    actions.append(Action(action_type="SWING", from_hex = x, to_hex =z))
        # print(f'slides/swings: {len(actions)}')
        random.shuffle(actions)
        '''<<<--------------------------------------------------------------------------- CHECK THIS WORKS FINE'''
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

    
    """Generate all throw actions"""
    # def _throw_actions(self, team_dict: dict):
    #     for team_name in Rules.VALID_TEAMS:
    #         if team_name not in team_dict:
    #             exit_with_error("Error in Team._throw_actions(): incorrect team_dict dictionary format.")
    #         if not is_type(team_dict[team_name], Team):
    #             exit_with_error("Error in Team._throw_actions(): incorrect team_dict dictionary format.")

    #     throw_actions = []
    #     if self.throws_remaining > 0:
    #         # Only throw this type if we do NOT already have it on the board
    #         throw_types = {symbol for symbol in Rules.VALID_SYMBOLS if not self.has_active_token(symbol)}
    #         for _s in throw_types:
    #             throw_zone = self.generate_throw_zone(team_dict, _s)
    #             for x in throw_zone:
    #                 throw_actions.append(Action(action_type = Action.THROW, token_symbol=_s, to_hex = x))
    #     # print(f'throws: {len(throw_actions)}')
    #     # random.shuffle(throw_actions)
    #     return throw_actions

    '''
    Only generate like 3 throw actions one for each type
    '''
    def _throw_actions(self, team_dict: dict, token_symbol: str):
        enemy_team = team_dict[UPPER] if self.team_name == LOWER else team_dict[LOWER]
        best_throw = None
        throw_action = None
        min_dist = -1

        if self.throws_remaining == 0:
            return None
        
        if self.throws_remaining > 0:
            throw_zone = self.generate_throw_zone(team_dict, token_symbol)
            for throw in throw_zone:
                killable_enemies = enemy_team.get_tokens_of_type(Token.BEATS_WHAT[token_symbol])
                for enemy in killable_enemies:  
                    dist = Hex.dist(throw, enemy.hex)
                    if min_dist == -1 or dist < min_dist:
                        min_dist = dist
                        best_throw = throw
            if best_throw:
                throw_action = Action(action_type = Rules.THROW, token_symbol = token_symbol, to_hex=best_throw)
        return throw_action

    

    # def _block_throw_action():
    #     # Find closest killable pair for enemy team
    #     # Find path with astar
    #     # Throw on the path to block

    #     #overlap between one of our token's next action and path[1]
    #     # then move that token

    #     (team_dict: dict, team_name: str, start: Token, end: Token, blacklist: list = [])
    #     return 

    def token_run_away_from(self, ally_token, opp_token, team_dict: dict):
        occupied_hexes = self.generate_occupied_hexes()
        dangerous_hexes = self.generate_dangerous_hexes(team_dict)
        x = ally_token.hex
        # find all adjacent hexes that are not occupied by ally tokens
        adjacents_x = set(x.adjacents()) - occupied_hexes - dangerous_hexes[ally_token.symbol]
        # find all hexes that are occupied 
        moves = set({})
        for y in adjacents_x:
            moves.add(y)
            if y in occupied_hexes:
                opposites_y = y.adjacents() - adjacents_x - occupied_hexes - {x} - dangerous_hexes[ally_token.symbol]
                for z in opposites_y:
                    moves.add(z)
        
        hex_avoid = opp_token.hex
        good_moves = []
        max_dist = -1
        for hex in moves:
            if max_dist == -1 or Hex.dist(hex, hex_avoid) > max_dist:
                good_moves = [hex]
                max_dist = Hex.dist(hex, hex_avoid)
            elif Hex.dist(hex, hex_avoid) == max_dist:
                good_moves.append(hex)
        return good_moves

    def generate_run_actions(self, team_dict: dict):
        defeated_by_tokens = self.generate_enemy_defeated_by(team_dict)
        actions = []
        for ally in self.active_tokens:
            scary_dudes = defeated_by_tokens[ally.symbol]
            closest_enemy = ally.find_closest_token(scary_dudes)
            if closest_enemy: 
                run_moves = self.token_run_away_from(ally, closest_enemy, team_dict)
                if not run_moves: continue
                new_dist = Hex.dist(run_moves[0], ally.hex)
                if new_dist == 1 or new_dist > Hex.dist(ally.hex, closest_enemy.hex):
                    for move in run_moves:
                        new_action = Action.create_action_from_path(ally.hex, move)
                        actions.append(new_action) 

        # print("Runnnnn")
        # for action in actions: print(action, end=', ')
        # print('\n')
        return actions                

    def generate_attack_actions(self, team_dict: dict):
        defeatable_tokens = self.generate_enemy_defeatable(team_dict)
        actions = []
        for ally in self.active_tokens:
            # Attack actions
            if defeatable_tokens[ally.symbol]:
                for enemy in defeatable_tokens[ally.symbol]:
                    moves = find_attack_moves_for_token(team_dict, self.team_name, ally, enemy)
                    if moves:
                        for move in moves:
                            new_action = Action.create_action_from_path(ally.hex, move)
                            actions.append(new_action) 
        # print("Actacckkk:")
        # for action in actions: print(action, end=', ')
        # print('\n')
        '''MAYBE: implement a counter for attack options and if there are overlaps, that attack gets a higher weighting'''
        return actions

    def generate_throw_actions(self, team_dict: dict):
        actions = []
        # Best throw action for each token symbol
        for _s in Rules.VALID_SYMBOLS:
            throw_action = self._throw_actions(team_dict, _s)
            if throw_action:
                # print(f'thr: {throw_action}')
                actions.append(throw_action)
        # print("Throwwww")
        # for action in actions: print(action, end=', ')
        # print('\n')
        return actions

    # def find_next_move_for_token(self, ally: Token, team_dict: dict):
    #     defeatable_tokens = self.generate_enemy_defeatable(team_dict)
    #     defeated_by_tokens = self.generate_enemy_defeated_by(team_dict)
    #     run_actions = []
    #     attack_actions = []
    #     scary_dudes = defeated_by_tokens[ally.symbol]
    #     closest_enemy = ally.find_closest_token(scary_dudes)
    #     # Find run actions
    #     if closest_enemy: 
    #         run_moves = self.token_run_away_from(ally, closest_enemy, team_dict)
    #         if run_moves:
    #             new_dist = Hex.dist(run_moves[0], ally.hex)
    #             if new_dist == 1 or new_dist > Hex.dist(ally.hex, closest_enemy.hex):
    #                 for move in run_moves:
    #                     new_action = Action.create_action_from_path(ally.hex, move)
    #                     run_actions.append(new_action)
    #     # Find attack actions
    #     if defeatable_tokens[ally.symbol]:
    #         for enemy in defeatable_tokens[ally.symbol]:
    #             attack_moves = find_attack_moves_for_token(team_dict, self.team_name, ally, enemy)
    #             if attack_moves:
    #                 for move in attack_moves:
    #                     new_action = Action.create_action_from_path(ally.hex, move)
    #                     attack_actions.append(new_action)
    #     # overlap = Action.find_overlap_actions(run_actions, attack_actions)
    #     return {ATTACK: attack_actions, RUN: run_actions} #, OVERLAP: overlap}
        

    # def generate_move_actions(self, team_dict: dict):
    #     attack_actions = []
    #     run_actions = []
    #     for ally in self.active_tokens:
    #         token_actions = self.find_next_move_for_token(ally, team_dict)
    #         # if token_actions[OVERLAP]:
    #         #     optimal_move_found = False
    #         #     for action in token_actions[OVERLAP]:
    #         #         if Hex.dist(action.from_hex, action.to_hex) == 1:
    #         #             optimal_move_found = True
    #         #             attack_actions.append(action)
    #         #     if optimal_move_found: continue
    #         attack_actions += token_actions[ATTACK]
    #         run_actions += token_actions[RUN]
    #     return {ATTACK: attack_actions, RUN: run_actions}









            
    
    
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
        
        # Best throw action for each token symbol
        for _s in Rules.VALID_SYMBOLS:
            throw_action = self._throw_actions(team_dict, _s)
            if throw_action:
                actions.append(throw_action)
        
        # actions += self._throw_actions(team_dict)
        # random.shuffle(actions)
        return actions
    

    def generate_good_actions(self, team_dict: dict):
        """
        Good actions include:
        - Chasing a killable opponent
        - Throwing on/close to a killable opponent
        - Running from a dangerous opponent
        """
        
        for team_name in Rules.VALID_TEAMS:
            if team_name not in team_dict:
                exit_with_error("Error in Team.generate_actions(): incorrect team_dict dictionary format.")
            if not is_type(team_dict[team_name], Team):
                exit_with_error("Error in Team.generate_actions(): incorrect team_dict dictionary format.")

        enemy_team = team_dict[UPPER] if self.team_name == LOWER else team_dict[LOWER]
        actions = []

        # Move actions
        attack_actions = self.generate_attack_actions(team_dict)
        run_actions = self.generate_run_actions(team_dict)
        
        # If there is overlap, only consider overlap if dist < 1
        overlap = Action.find_overlap_actions(attack_actions, run_actions)
        overlap_important = []
        for action in overlap:
            if enemy_team.exists_token_at(action.to_hex):
                overlap_important.append(action)

        if overlap_important:
            actions += overlap_important
        else:
            actions += attack_actions
            actions += run_actions
            # Throw actions
            actions += self.generate_throw_actions(team_dict)
        
        # If no good actions, random move
        if len(actions) == 0:
            random_actions = self.generate_actions(team_dict)
            i = np.random.randint(0, len(random_actions)-1)
            actions.append(random_actions[int(i)])

        return actions


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
                # dist = Hex.dist(token.hex, enemy_token.hex)
                dist = token.dist(other_token = enemy_token)
                if min_dist == -1 or dist < min_dist:
                    min_dist = dist
                    closest_pair = (token, enemy_token)
    
        return closest_pair, min_dist

    def determine_closest_threat(self, team_dict: dict):

        enemy_team = team_dict[UPPER] if self.team_name == LOWER else team_dict[LOWER]
        closest_pair = None
        min_dist = -1
        
        for token in enemy_team.active_tokens:
            ally_tokens = self.get_tokens_of_type(token.beats_what())
            
            ally_token = token.find_closest_token(ally_tokens)
            if ally_token:
                dist = token.dist(other_token = ally_token)
                if min_dist == -1 or dist < min_dist:
                    min_dist = dist
                    closest_pair = (token, ally_token)
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
            return None, None

        throw_types = {symbol for symbol in Rules.VALID_SYMBOLS if not self.has_active_token(symbol)}
        
        for _s in throw_types:
            throw_zone = list(self.generate_throw_zone(team_dict, _s))
            random.shuffle(throw_zone)
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

