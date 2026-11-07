import json
from enum import Enum
from random import randint, shuffle

from arcade.types import Color
import arcade.color

from country import Country, CountryEnum
from player import Player
from human_player import HumanPlayer
from card import Card




class Stage(Enum):
    TERRITORY_SELECTION = 0                 #initial territory selection
    TERRITORY_REINFORCEMENT = 1
    PLACE_ARMIES = 2
    TURN_IN_CARDS = 3
    ATTACK = 4
    DAMAGE_STEP = 9
    OCCUPY = 10
    CHECK_DEFEAT = 11
    DRAW_CARD = 12
    FORTIFY = 13
    TWOP_SELECTION = 14
    NEUTRAL_SELECTION = 15
    PLAYERS_JOINING = 16
    GAME_OVER = 17

# important invariants:
# selected > attacked > attacker_rolls > defender_rolls, 
# a larger one being None means all smaller must be None

INFANTRY_COUNT = [0,0,40,35,30,25,20]

class GameState:
    def __init__(self, territories: list[Country], two_player: bool = False):
        self.territories: list[Country] = territories
        self.two_player = two_player
        self.cards = Card.new_deck(keep_wilds= not two_player)
        shuffle(self.cards)
        self.conquered_this_turn: bool = False
        self.winner: Player | None = None
        self.selected: Country | None = None
        self.attacked: Country | None = None
        self.players: list[Player] = []
        self.armies_remaining: dict[Player, int] = {}
        self.current_player: Player | None = None
        self.current_stage: Stage = Stage.PLAYERS_JOINING
        self.attacker_rolls: list[int] | None = None
        self.defender_rolls: list[int] | None = None
        # copies of the most recent roll so the UI can still show them after the attack
        self.last_attacker_rolls: list[int] = []
        self.last_defender_rolls: list[int] = []
        self.gained_armies: bool = False

    @classmethod
    def from_file(cls, edge_file: str, two_player: bool = False) -> "GameState":
        with open(edge_file, "r", encoding="utf-8") as file:
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
        if self.current_stage != Stage.PLAYERS_JOINING or len(self.players) < 2 or (not self.two_player and len(self.players) < 3):
            return False

        # disabled setup for now
        # for player in self.players:
        #     self.armies_remaining[player] = INFANTRY_COUNT[len(self.players)]
        # shuffle(self.players)
        # self.current_player = self.players[0]
        # self.current_stage = Stage.TERRITORY_SELECTION

        # old random setup
        shuffle(self.players)
        self.current_player = self.players[0]
        self.deal_territories()
        self.current_stage = Stage.ATTACK

        #ensure self.armies_remaining is set
        for player in self.players:
            self.armies_remaining[player] = 0
        return True

    def deal_territories(self):
        """Randomly split territories between players, 1-5 armies each."""
        indices = list(range(len(self.territories)))
        shuffle(indices)
        for (n, i) in enumerate(indices):
            self.territories[i].owner = self.players[n % len(self.players)]
            self.territories[i].armies = randint(1, 5)

    def reachable_tiles(self, player: Player) -> list[Country]:
        if player != self.current_player:
            return []

        if self.current_stage == Stage.ATTACK:
            if self.selected is None:
                # owned territories that have enough armies to attack
                return [x for x in self.territories if x.owner == player and x.armies > 1]
            if self.attacked is None:
                # adjacent enemies, plus the selected territory itself (to deselect)
                return [x for x in self.territories
                        if x == self.selected
                        or (x.owner != player and x.type.value in self.selected.adj)]
            # target chosen: click either one to back out
            return [self.selected, self.attacked]

        
        if self.current_stage == Stage.TERRITORY_SELECTION:
            # all tiles with no owner
            # print("Got here :)")
            return list(filter(lambda x: x.owner is None, self.territories))

        if self.current_stage == Stage.FORTIFY:
            if self.selected is not None:
                return [x for x in self.territories
                            if x == self.selected
                            or (x.owner == player and x.type.value in self.selected.adj)]
            return [x for x in self.territories
                            if x.owner == player and x.armies > 1]
        
        if self.current_stage in (Stage.TERRITORY_REINFORCEMENT, Stage.PLACE_ARMIES):
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
    
    def select_territory(self, player : Player, id: int):
        if player != self.current_player or self.territories[id] not in self.reachable_tiles(player):
            return False
        clicked = self.territories[id]

        if self.current_stage == Stage.ATTACK:
            if clicked == self.attacked:
                # pick a different target
                self.attacked = None
            elif clicked == self.selected:
                # deselect attacker, drops target too
                self.selected = None
                self.attacked = None
            elif self.selected is None:
                # first click: attacker
                self.selected = clicked
            else:
                # second click: target
                self.attacked = clicked
            return True
        
        if self.current_stage == Stage.FORTIFY:
            if clicked == self.selected:
                self.selected = None
            elif self.selected is None:
                self.selected = clicked
            else: # TODO: allow user to select number
                clicked.armies += self.selected.armies - 1
                self.selected.armies = 1
                self.end_turn()
            return True
        # if self.current_stage == Stage.TERRITORY_SELECTION:
        #     self.territories[id].armies += 1
        #     self.armies_remaining[player] -= 1 
        #     self.territories[id].owner = self.current_player
        #     if all(len(self.reachable_tiles(player)) == 0 for player in self.players):
        #         self.current_stage = Stage.TERRITORY_REINFORCEMENT
        #     self.end_turn()
        #     return True
        #
        # if self.current_stage == Stage.TERRITORY_REINFORCEMENT:
        #     self.territories[id].armies += 1
        #     self.armies_remaining[player] -= 1 
        #     if all(len(self.reachable_tiles(player)) == 0 for player in self.players):
        #         self.current_stage = Stage.PLACE_ARMIES
        #     self.end_turn()
        #     return True

        if self.current_stage == Stage.PLACE_ARMIES:
            self.territories[id].armies += 1
            self.armies_remaining[player] -= 1 
            if self.armies_remaining[player] == 0:
                self.current_stage = Stage.ATTACK
            return True       

        self.selected = self.territories[id]
        return True

    def attack_roll(self, player: Player) -> bool:
        """Roll max dice for both sides. Called by the Roll button."""
        if (self.current_stage != Stage.ATTACK or player != self.current_player
                or self.selected is None or self.attacked is None):
            return False
        defender = self.attacked.owner
        if defender is None:
            return False
        if not self.select_dice(player, self.active_dice(player)):
            return False
        if not self.select_dice(defender, self.active_dice(defender)):
            return False
        return self.do_damage()

    def reset_attack(self):
        self.attacker_rolls = None
        self.defender_rolls = None
        self.attacked = None
        self.selected = None

    def skip_attacking(self, player: Player):
        if player == self.current_player and self.current_stage == Stage.ATTACK:
            self.current_stage = Stage.CHECK_DEFEAT

    def can_skip(self, player: Player) -> bool:
        if player != self.current_player or self.current_stage in (
                Stage.TERRITORY_REINFORCEMENT, Stage.TERRITORY_SELECTION, Stage.PLACE_ARMIES):
            return False

        if self.current_stage == Stage.ATTACK:
            return True
        if self.current_stage == Stage.TURN_IN_CARDS and len(player.hand.cards) < 5:
            return True

        return False
    

    def can_skip_fortify(self, player):
        return player == self.current_player and self.current_stage == Stage.FORTIFY

    def skip_fortify(self):
        """Skip fortifying. end_turn clears selection."""
        if self.current_stage == Stage.FORTIFY:
            self.end_turn()

    def start_turn(self, player: Player):
        # Automatically get `max(controlled_territories // 3, 3)` armies
        self.armies_remaining[player] += max(len(player.controlled_territories(self.territories)) // 3, 3)
        
        # calculate continent bonuses
        bonuses: list[int] = [5, 2, 3, 5, 7, 2]
        for i in range(6):
            needed = CountryEnum.countries_in_continent(i)
            has_all: bool = True
            for country_id in needed:
                has_all &= self.territories[country_id].owner == player
            if has_all:
                self.armies_remaining[player] += bonuses[i]
        
        # if has cards to turn in, set to Stage.TURN_IN_CARDS
        if player.hand.can_use():
            self.current_stage = Stage.TURN_IN_CARDS
        # otherwise, move straight to Stage.place_armies
        else:
            self.current_stage = Stage.PLACE_ARMIES
        

    def end_turn(self):
        if self.current_stage == Stage.GAME_OVER:
            return
        self.reset_attack()
        assert self.current_player is not None
        # one card per turn if the player conquered at least one territory
        if self.conquered_this_turn and self.cards:
            self.current_player.hand.add_card(self.cards.pop())
        self.conquered_this_turn = False

        if self.current_stage == Stage.ATTACK:
            self.current_stage = Stage.FORTIFY
            return
            
        
        self.current_player = self.players[(self.players.index(self.current_player) + 1) % len(self.players)]
        self.start_turn(self.current_player)
        # TODO: enable once PLACE_ARMIES is playable and start_play fills armies_remaining
        # if self.current_stage not in (Stage.TERRITORY_SELECTION, Stage.TERRITORY_REINFORCEMENT):
        #     self.start_turn(self.current_player)


    def do_damage(self) -> bool:
        if self.attacker_rolls is None or self.defender_rolls is None or self.attacked is None or self.selected is None:
            return False

        # keep a sorted copy for the UI, highest first
        self.last_attacker_rolls = sorted(self.attacker_rolls, reverse=True)
        self.last_defender_rolls = sorted(self.defender_rolls, reverse=True)

        attack = list(self.last_attacker_rolls)
        defend = list(self.last_defender_rolls)
        while attack and defend:
            # ties go to the defender
            if attack.pop(0) > defend.pop(0):
                self.attacked.armies -= 1
            else:
                self.selected.armies -= 1

        if self.attacked.armies <= 0:
            # TODO: let the player choose how many to move
            moved = len(self.attacker_rolls)
            defender = self.attacked.owner
            self.attacked.owner = self.current_player
            self.attacked.armies = moved
            self.selected.armies -= moved
            self.conquered_this_turn = True
            self.reset_attack()
            self.check_defeat(defender)
        else:
            self.attacker_rolls = None
            self.defender_rolls = None
            if self.selected.armies < 2:
                self.reset_attack()
        return True

    def check_defeat(self, defender):
        """Remove `defender` if they lost their last territory, end the game if one player is left."""
        if defender is None or defender.controlled_territories(self.territories):
            return
        self.players.remove(defender)
        if len(self.players) == 1:
            self.winner = self.current_player
            self.current_stage = Stage.GAME_OVER

#
# 1. Determine Play Order
# 2. Color Selection
# 3. Territory Selection (continues until no unclaimed territories)
# 4. Territory Reinforcement (continues until no remaining armies)
# 5. Move to Turns
