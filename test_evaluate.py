from cooked_pancakes.foundations import *
from cooked_pancakes.team import Team
from cooked_pancakes.board import Board
import random

UPPER = Rules.UPPER
LOWER = Rules.LOWER

<<<<<<< HEAD:cooked_pancakes/test_evaluate.py
=======
REACH = max(Rules.HEX_RANGE)


>>>>>>> ef711518da80465256215c17a89e2d75a5c49828:test_evaluate.py
num_tokens_upper = random.randint(0,5)
upper_positions = []
for i in range(num_tokens_upper):
    rand_x = random.randint(-REACH, REACH)
    rand_y = random.randint(-REACH-rand_x, REACH) if rand_x <= 0 else random.randint(-REACH, REACH-rand_x)
    symbol = list(Rules.VALID_SYMBOLS)[random.randint(0,2)]
    upper_positions.append(((rand_x,rand_y), symbol))

num_tokens_lower = random.randint(0,5)
lower_positions = []
for i in range(num_tokens_lower):
    rand_x = random.randint(-REACH, REACH)
    rand_y = random.randint(-REACH-rand_x, REACH) if rand_x <= 0 else random.randint(-REACH, REACH-rand_x)
    symbol = list(Rules.VALID_SYMBOLS)[random.randint(0,2)]
    lower_positions.append(((rand_x,rand_y), symbol))
    
upper_tokens = [Token(Hex(coordinate=position[0]), position[1]) for position in upper_positions]
lower_tokens = [Token(Hex(coordinate=position[0]), position[1]) for position in lower_positions]

team_upper = Team(UPPER)
team_lower = Team(LOWER)
team_upper.active_tokens = upper_tokens
team_upper.throws_remaining = Rules.MAX_THROWS - len(upper_tokens)
team_lower.active_tokens = lower_tokens
team_lower.throws_remaining = Rules.MAX_THROWS - len(lower_tokens)

state = Board(team_upper=team_upper, team_lower=team_lower)

print(state)
print(state.evaluate(team=state.team_upper))