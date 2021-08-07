README.md

This program is meant to strategically play the game of Hearts using logic, card counting, and risk analysis. Other online Hearts bots operate with full knowledge
of the cards in every player's hand, a serious advantage. This one, however, infers decisions like a real human player, with no knowledge of what other 
players have left in their hands other than what it can logically deduce.

The bot is meant to replace the decisions of a human player in a real game. To run the program, simply run play_game.py. Input your hand in any order, representing
each card as a two-character rank-suit string. For example, the "2 of Clubs" should be represented as "2c", the "5 of Spades" should be represented as "5s", and 
the "Ace of Hearts" should be represented as "Ah" (note: "10 of Diamonds" should be represented as "Td", not "10d"). 

Simply follow the prompts from there. After inputting your hand, the program will ask whether the round is a passing round or not -- if so, it will instruct cards
to pass. In gameplay, you will input the cards played by other players -- on your turn, the program will instruct you which card to play. At the end of the 
round, it will tally the points and update the total. Once a player reaches 100 points, the game will end, and a winner will be crowned -- just as the standard
Hearts rules dictate.

In its current form, the program is not very "fun" to play with :) as the operator is just inputting cards and following instructions. However, card game websites
could easily implement the program, and use it as a fairer alternative to their current omniscient algorithms.

It is limited in the two following ways: it does not know how to "shoot the moon", and it does not protect the game from ending if it will likely lose. The goal of
Hearts is to minimize the number of points taken. But if a player is able to take all 26 of the points, i.e. "shoot the moon", then in fact they are awarded 0 
points and all other players are awarded 26. This program simply minimizes the number of points taken, as determining algorithmically when to try and shoot the moon
is very complicated. 

Secondly, if a player is on the verge of 100 points and the game is about to end, it will not prolong the game if it is currently losing. This, however, does not
matter much, as it is usually winning towards the end of the game.
