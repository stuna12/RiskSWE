# RiskSWE

Our team implemented the board game **Risk**, using the
[Arcade](https://api.arcade.academy/) game library. Players take turns placing
armies and attacking neighboring territories to control the map.

## Requirements

- Python 3.10 or newer (tested on 3.11.5)
- Arcade 3.0 or newer (tested on 3.3.3)

Arcade is the only third party package required.

## Installation

1. Clone or download the repository.
2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   - macOS/Linux: `source .venv/bin/activate`
   - Windows PowerShell: `.venv\Scripts\Activate.ps1`

3. Install Arcade:

   ```bash
   pip install arcade
   ```

## Running the Game

From the project folder (the folder containing `main.py`), run:

```bash
python main.py
```

Select **Start Game** from the main menu to begin. Press **Esc** at any time
to exit, or click **Quit Game** during a game.

## How to Play

The goal is to capture all 42 territories and eliminate the other player.
Players share the same screen and take turns. At the start of the game 
territories are distributed randomly.

### Taking a Turn

1. **Place armies:** Players receive troops at the start of each turn for every 
   turn after the first turn. Players always receive at least 3 troops. Receive 
   one troop for every three territories you own, plus bonuses for continents. 
   Click a territory you own to add troops to it. Once you collect enough cards, 
   you can also trade them in for bonus troops.

2. **Attack:** Select one of your territories with at least 2 armies, then
   select an adjacent enemy territory and click **Roll**. The attacker rolls
   up to 3 dice depending on the number of attacking troops. The defender rolls up 
   to 2 dice. The highest dice are compared and ties go to the defender. You can 
   attack multiple times.

3. **End Turn:** Click **End Turn** when you finish attacking. Gain a card 
   if you captured at least one territory during your turn.

4. **Fortify:** To fortify, select a territory you control with at least 2 
   armies and an adjacent territory you own. You can also choose to click 
   **Skip Fortify**.

The game ends when one player controls all territories. Press **Esc** or
click **Quit Game** to close the game.

## Citations

Map image: see `sources.md` (Wikimedia Commons, `Risk_game_map.png`).
