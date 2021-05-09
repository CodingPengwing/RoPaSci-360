from cooked_pancakes.foundations import *
from cooked_pancakes.token import Token
from cooked_pancakes.team import Team
from cooked_pancakes.board import Board
import random

UPPER = Rules.UPPER
LOWER = Rules.LOWER





num_tokens_upper = random.randint(0,5)

upper_tokens = []
for i in range(num_tokens_upper):
    rand_x = random.randint(-4,4)
    rand_y = random.randint(-4-rand_x, 4) if rand_x <= 0 else random.randint(-4, 4-rand_x)
    symbol = list(Rules.VALID_SYMBOLS)[random.randint(0,2)]
    upper_tokens.append(Token(Hex(rand_x,rand_y), symbol))

num_tokens_lower = random.randint(0,5)
lower_tokens = []
for i in range(num_tokens_lower):
    rand_x = random.randint(-4,4)
    rand_y = random.randint(-4-rand_x, 4) if rand_x <= 0 else random.randint(-4, 4-rand_x)
    symbol = list(Rules.VALID_SYMBOLS)[random.randint(0,2)]
    lower_tokens.append(Token(Hex(rand_x,rand_y), symbol))    
    
team_upper = Team(UPPER)
team_lower = Team(LOWER)
team_upper.active_tokens = upper_tokens
team_upper.throws_remaining = Rules.MAX_THROWS - len(upper_tokens)
team_lower.active_tokens = lower_tokens
team_lower.throws_remaining = Rules.MAX_THROWS - len(lower_tokens)

state = Board(team_upper=team_upper, team_lower=team_lower)
print(state)
print(state.evaluate(team=state.team_upper))