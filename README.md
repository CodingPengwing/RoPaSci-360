# RoPaSci 360 #

This is a custom game of Rock Paper Scissors with a twist! The game is played on a hexagonal board with dimensions of 6 x 6.
The rules are:
- Each player has 9 "throws"
- Each time you throw, you can put down a Rock/Paper/Scissor.
- Each turn, you can either throw, or move a piece
- The goal is to kill all the pieces belonging to the opponent.
More specific rules can be found in the specifications file in the repo.

To run, navigate to the correct directory, then use command in terminal:  
python -m referee <player_1> <player_2>  
(where players can be one of: random_player, greedy_player, cooked_pancakes)

Here are some examples:  
python -m referee greedy_player cooked_pancakes  
python -m referee random_player cooked_pancakes  
python -m referee cooked_pancakes cooked_pancakes  
