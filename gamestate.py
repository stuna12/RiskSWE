from country import Country, CountryEnum
from player import Player
from human_player import HumanPlayer
from enum import Enum
from card import Card
from random import randint, shuffle 
from arcade.types import Color
import arcade.color
import json

class Stage(Enum):
    TERRITORY_SELECTION = 0                 #initial territory selection
    TERRITORY_REINFORCEMENT = 1     # 
    ACQUIRE_ARMIES = 2
    TURN_IN_CARDS = 3
    ATTACK = 4
    CHOOSE_DICE = 7
    DEFENDER_CHOOSE_DICE = 8
    DAMAGE_STEP = 9
    OCCUPY = 10
    CHECK_DEFEAT = 11
    DRAW_CARD = 12
    FORTIFY = 13
    TWOP_SELECTION = 14
    NEUTRAL_SELECTION = 15
    PLAYERS_JOINING = 16

# important invariants:
# selected > attacked > attacker_rolls > defender_rolls, a larger one being None means all smaller must be None



class GameState:
    def __init__(self, territories: list[Country], two_player: bool = False):
        self.territories: list[Country] = territories
        self.two_player = two_player
        self.cards = Card.new_deck(keep_wilds= not two_player)
        self.selected: Country | None = None
        self.attacked: Country | None = None
        self.players: list[Player] = [] 
        self.current_player: Player | None = None
        self.current_stage: Stage = Stage.PLAYERS_JOINING
        self.attacker_rolls: list[int] | None = None
        self.defender_rolls: list[int] | None = None

    @classmethod
    def from_file(cls, edge_file: str, two_player: bool = False) -> "GameState":
        with open("edges.txt", "r", encoding="utf-8") as file:
            edges = json.load(file)
        
        territories: list[Country] = []
        for i in range(len(edges)):
            territories.append(Country(type=CountryEnum(i)))
        for (i,adj) in enumerate(edges):
            territories[i].adj = adj

        return cls(territories, two_player)
        
    def add_player(self, player: Player) -> bool:
        if self.current_stage != Stage.PLAYERS_JOINING or (self.two_player and len(self.players) >= 2) or len(self.players) >= 6:
            return False
        self.players.append(player)
        return True

    def start_play(self) -> bool:
        if self.current_stage != Stage.PLAYERS_JOINING or (self.two_player and len(self.players) < 2) or len(self.players) < 3:
            return False

        shuffle(self.players)
        self.current_player = self.players[0]
        self.current_stage = Stage.TERRITORY_REINFORCEMENT
        return True


    
    def reachable_tiles(self, player: Player) -> list[Country]:
        if player != self.current_player:
            return []

        if self.current_stage == Stage.ATTACK:
            if self.selected is None:
                # all owned territories with more than 1 army
                return list(filter(lambda x: x.owner == player and x.armies > 1, self.territories))
            elif self.attacked is None:
                # all non-owned territories adjacent to the selected territory, plus the selected territory itself (for deselection)
                return list(filter(lambda x : (x.owner != player and (self.selected is not None and x in self.selected.adj)) or x == self.selected, self.territories))
        
        if self.current_stage == Stage.TERRITORY_SELECTION:
            # all tiles with no owner
            return list(filter(lambda x: x.owner == None, self.territories))
        
        elif self.current_stage == Stage.TERRITORY_REINFORCEMENT:
            # all tiles owned by the current player
            return list(filter(lambda x: x.owner == self.current_player, self.territories))
        
            
        # elif self.current_stage: 
        return []

    def active_dice(self, player: Player) -> int:
        if self.current_stage != Stage.ATTACK or self.attacked is None:
            return 0
        if player == self.current_player and self.selected is not None:
            return min(3, self.selected.armies-1)
        if player == self.attacked.owner:
            return min(2, self.attacked.armies)
        return 0
        
    def rolls(self, player: Player) -> list[int]:
        if player == self.current_player and self.attacker_rolls is not None:
            return self.attacker_rolls
        if self.attacked is None:
            return []
        if player == self.attacked.owner and self.defender_rolls is not None:
            return self.defender_rolls
        return []

    """"""
    def select_dice(self, player:Player, count:int) -> bool:
        if count > self.active_dice(player) or self.current_stage != Stage.ATTACK:
            return False
        
        if player == self.current_player and self.attacked is not None and self.attacker_rolls is None:
            self.attacker_rolls = [0] * count
            for i in range(count):
                self.attacker_rolls[i] = randint(1, 6)
            return True
        
        if self.attacked is not None and player == self.attacked.owner and self.attacker_rolls is not None:
            self.defender_rolls = [0] * count
            for i in range(count):
                self.defender_rolls[i] = randint(1, 6)
            return True
        
        return False
    
    def select_territory(self, player:Player, id: int) -> bool:
        if player != self.current_player or self.territories[id] not in self.reachable_tiles(player):
            return False

        # wants to deselect selected territory
        if self.selected == self.territories[id] and self.attacked is None:
            self.selected = None
            return True
        
        # wants to deselect attacked territory
        if self.attacked == self.territories[id] and self.attacker_rolls is None:
            self.attacked = None
            return True

        self.selected = self.territories[id]
        return True

    def reset_attack(self):
        self.attacker_rolls = None
        self.defender_rolls = None
        self.attacked = None
        self.selected = None

    def skip_attacking(self, player : Player):
        if player == self.current_player and self.current_stage == Stage.ATTACK:
            self.current_stage = Stage.CHECK_DEFEAT
            self.reset_attack()

            
    def end_turn(self):
        self.selected = None
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.current_player = self.players[self.current_player_index]

    def do_damage(self, player : Player) -> bool:
        if self.attacker_rolls is None or self.defender_rolls is None or self.attacked is None or self.selected is None:
            return False

        attack = sorted(self.attacker_rolls)
        defend = sorted(self.defender_rolls)

        while len(attack) > 0 and len(defend) > 0:
            if attack.pop() > defend.pop(): #attacker won roll
                self.attacked.armies -= 1
            else:
                self.selected.armies -= 1

        # TODO: handle territory occupation correctly
        # Should be user-selected value between `len(self.attacker_rolls)` and self.selected.armies-1
        # Would change game-state to Stage.OCCUPY and wait for GUI to call `occupy`
        if self.attacked.armies == 0:
            self.current_stage = Stage.OCCUPY
            self.attacked.owner = self.current_player
            self.attacked.armies = 1
            self.selected.armies -= 1

        self.attacker_rolls = None
        self.defender_rolls = None
        self.selected = None
        self.attacked = None
        return True
    
#
# 1. Determine Play Order
# 2. Color Selection
# 3. Territory Selection (continues until no unclaimed territories)
# 4. Territory Reinforcement (continues until no remaining armies)
# 5. Move to Turns