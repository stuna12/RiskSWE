# Flow of Play (3-6 Players)

### Setup:
1. Determine Play Order
2. Color Selection
3. Territory Selection (continues until no unclaimed territories)
4. Territory Reinforcement (continues until no remaining armies)
5. Move to Turns

### Turns:
1. Acquire New Armies
    - Automatically get `max(controlled_territories // 3, 3)` armies
    - Take armies for continent bonuses
    - If you have 5 or 6 cards, you *must* turn them in
    - Turn in cards, get new armies depending on how many cards have been turned in
    - If you control any of the territories on a card you've turned in, you get two more troops this turn, to be placed in that specific territory. If you had multiple such cards, you still only get two armies, but you may choose which territory they are placed in.
2. Attack (You may attack as many times in a turn as you would like)
    - Decide if you want to attack or pass this section of your turn
    - Designate an attacking territory you own and an attacked territory adjacent to the attacking territory.
    - Call the troop count on your territory `t` and that of the attacked territory `p`
    - You must have at least 2 troops on your attacking territory
    - You will roll your choice of `range(1, min(3, t-1))` 6-sided dice
    - The defender will roll their choice of `range(1, min(2, p))` 6-sided dice
    - Compare the highest die from each pool. If the attacker's is higher, the defender loses one defender, otherwise the attacker loses one attacking piece. 
    - Do the same for each next pair of dice (if they exist)
    - As soon as a defending territory is empty, you capture that territory and must occupy it. Move your choice of `range(d, max(t-1))` armies onto the occupied territory, where `d` is the number of dice you rolled to occupy it. 

3. Defeating Opponents
    - If you have defeated the last army of an opponent, you win any cards that player has collected.
    - If winning them gives you 6 or more cards, you must immediately trade in enough sets to reduce your hand to 4 or fewer cards, at which point you must stop trading.
    - Otherwise, you must wait until the start of your next turn to make any trades.

4. Draw Cards
    - If you have captured at least one territory this turn, draw one card from the deck.

5. Fortify
    - Move as many armies as you'd like from any one of your territories to an adjacent territory you control one single time. You must leave at least one army behind.

### Winning
Once each opponent has been defeated, you have won the game.

# Flow of Play (2 Players)
### Setup:
1. Determine Play Order
2. Color Selection
3. Territory Selection
    - Remove wild cards from the deck and shuffle, dealing equally into three piles. For each pile, choose a color and place individual armies of that color on each territory
4. Territory Reinforcement
    - Each player (in order of play) places two armies on any one or two of their territories, then places one neutral piece in a neutral territory of their choice. This repeats until all troops are deployed.
5. Return all cards to the deck and shuffle.
6. Move to Turns

### Turns: 
Behaves the same as the 3-6 player variant except that your opponent will perform the dice rolls for the neutral territories when they are attacked, the neutral "player" does not take turns, and does not have to be defeated to win. Defeating only the territories your opponent controls will win the game.