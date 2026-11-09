# pylint: disable=C0114, C0116
import json
from dataclasses import dataclass, field
from enum import Enum
from random import randint, shuffle

from country import Country, CountryEnum
from player import Player
from card import Card




class Stage(Enum):
    """Phases the game moves through."""
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
# turn.selected > battle.attacked > battle.attacker_rolls > battle.defender_rolls,
# a larger one being None means all smaller must be None

INFANTRY_COUNT = [0,0,40,35,30,25,20]


@dataclass
class TurnState:
    """Whose turn it is, which stage they are in, and what they have selected."""
    player: Player | None = None
    stage: Stage = Stage.PLAYERS_JOINING
    selected: Country | None = None
    conquered: bool = False         # conquered at least one territory this turn
    gained_armies: bool = False
    selected_cards: list[int] = field(default_factory=list)
    cards_submitted: int = 0


@dataclass
class Battle:
    """The territory being attacked and the dice rolled in the current attack."""
    attacked: Country | None = None
    attacker_rolls: list[int] | None = None
    defender_rolls: list[int] | None = None
    # copies of the most recent roll so the UI can still show them after the attack
    last_attacker_rolls: list[int] = field(default_factory=list)
    last_defender_rolls: list[int] = field(default_factory=list)


class GameState:
    """Holds all game data and rules for changing it."""

    def __init__(self, territories: list[Country], two_player: bool = False):
        self.territories: list[Country] = territories
        self.two_player = two_player
        self.cards = Card.new_deck(keep_wilds= not two_player)
        shuffle(self.cards)
        self.players: list[Player] = []
        self.armies_remaining: dict[Player, int] = {}
        self.turn = TurnState()
        self.battle = Battle()

    @classmethod
    def from_file(cls, edge_file: str, two_player: bool = False) -> "GameState":
        with open(edge_file, "r", encoding="utf-8") as file:
            edges = json.load(file)

        territories: list[Country] = []
        for i in range(len(edges)):
            territories.append(Country(country_type=CountryEnum(i)))
        for (i,adj) in enumerate(edges):
            territories[i].adj = adj

        return cls(territories, two_player)

    @property
    def winner(self) -> Player | None:
        """The last player standing, once the game is over."""
        if self.turn.stage == Stage.GAME_OVER and len(self.players) == 1:
            return self.players[0]
        return None

    def add_player(self, player: Player) -> bool:
        if (self.turn.stage != Stage.PLAYERS_JOINING
                or (self.two_player and len(self.players) >= 2)
                or len(self.players) >= 6):
            return False
        self.players.append(player)
        return True

    def start_play(self) -> bool:
        if (self.turn.stage != Stage.PLAYERS_JOINING
                or len(self.players) < 2
                or (not self.two_player and len(self.players) < 3)):
            return False

        # disabled setup for now
        # for player in self.players:
        #     self.armies_remaining[player] = INFANTRY_COUNT[len(self.players)]
        # shuffle(self.players)
        # self.turn.player = self.players[0]
        # self.turn.stage = Stage.TERRITORY_SELECTION

        # old random setup
        shuffle(self.players)
        self.turn.player = self.players[0]
        self._deal_territories()
        self.turn.stage = Stage.ATTACK

        self.turn.player.hand.add_card(self.cards.pop())
        self.turn.player.hand.add_card(self.cards.pop())
        self.turn.player.hand.add_card(self.cards.pop())
        self.turn.player.hand.add_card(self.cards.pop())
        self.turn.player.hand.add_card(self.cards.pop())
        self.turn.player.hand.add_card(self.cards.pop())
        
        #ensure self.armies_remaining is set
        for player in self.players:
            self.armies_remaining[player] = 0
        return True

    def _deal_territories(self):
        """Randomly split territories between players, 1-5 armies each."""
        indices = list(range(len(self.territories)))
        shuffle(indices)
        for (n, i) in enumerate(indices):
            self.territories[i].owner = self.players[n % len(self.players)]
            self.territories[i].armies = randint(1, 5)

    def reachable_tiles(self, player: Player) -> list[Country]:
        if player != self.turn.player:
            return []

        stage = self.turn.stage
        if stage == Stage.ATTACK:
            return self._attack_tiles(player)

        if stage == Stage.TERRITORY_SELECTION:
            # all tiles with no owner
            return [x for x in self.territories if x.owner is None]

        if stage == Stage.FORTIFY:
            return self._fortify_tiles(player)

        if stage in (Stage.TERRITORY_REINFORCEMENT, Stage.PLACE_ARMIES):
            # all tiles owned by the current player
            return [x for x in self.territories if x.owner == player]

        return []

    def _attack_tiles(self, player: Player) -> list[Country]:
        selected = self.turn.selected
        if selected is None:
            # owned territories that have enough armies to attack
            return [x for x in self.territories if x.owner == player and x.armies > 1]
        if self.battle.attacked is None:
            # adjacent enemies, plus the selected territory itself (to deselect)
            return [x for x in self.territories
                    if x == selected
                    or (x.owner != player and x.type.value in selected.adj)]
        # target chosen: click either one to back out
        return [selected, self.battle.attacked]

    def _fortify_tiles(self, player: Player) -> list[Country]:
        selected = self.turn.selected
        if selected is not None:
            return [x for x in self.territories
                        if x == selected
                        or (x.owner == player and x.type.value in selected.adj)]
        return [x for x in self.territories
                        if x.owner == player and x.armies > 1]

    def active_dice(self, player: Player) -> int:
        attacked = self.battle.attacked
        if self.turn.stage != Stage.ATTACK or attacked is None:
            return 0
        if player == self.turn.player and self.turn.selected is not None:
            return min(3, self.turn.selected.armies-1)
        if player == attacked.owner:
            return min(2, attacked.armies)
        return 0

    def rolls(self, player: Player) -> list[int]:
        if player == self.turn.player and self.battle.attacker_rolls is not None:
            return self.battle.attacker_rolls
        if self.battle.attacked is None:
            return []
        if player == self.battle.attacked.owner and self.battle.defender_rolls is not None:
            return self.battle.defender_rolls
        return []

    def select_dice(self, player:Player, count:int) -> bool:
        if count > self.active_dice(player) or self.turn.stage != Stage.ATTACK:
            return False

        battle = self.battle
        if (player == self.turn.player and battle.attacked is not None
                and battle.attacker_rolls is None):
            battle.attacker_rolls = [randint(1, 6) for _ in range(count)]
            return True

        if (battle.attacked is not None and player == battle.attacked.owner
                and battle.attacker_rolls is not None):
            battle.defender_rolls = [randint(1, 6) for _ in range(count)]
            return True

        return False

    def select_territory(self, player, territory_id):
        if (player != self.turn.player
                or self.territories[territory_id] not in self.reachable_tiles(player)):
            return False
        clicked = self.territories[territory_id]

        if self.turn.stage == Stage.ATTACK:
            if clicked == self.battle.attacked:
                # pick a different target
                self.battle.attacked = None
            elif clicked == self.turn.selected:
                # deselect attacker (and target)
                self.turn.selected = None
                self.battle.attacked = None
            elif self.turn.selected is None:
                # first click: attacker
                self.turn.selected = clicked
            else:
                # second click: target
                self.battle.attacked = clicked
            return True

        if self.turn.stage == Stage.FORTIFY:
            if clicked == self.turn.selected:
                self.turn.selected = None
            elif self.turn.selected is None:
                self.turn.selected = clicked
            else: # currently moves every army but one
                clicked.armies += self.turn.selected.armies - 1
                self.turn.selected.armies = 1
                self.end_turn()
            return True

        if self.turn.stage == Stage.PLACE_ARMIES:
            self.territories[territory_id].armies += 1
            self.armies_remaining[player] -= 1
            if self.armies_remaining[player] == 0:
                self.turn.stage = Stage.ATTACK
            return True

        self.turn.selected = self.territories[territory_id]
        return True

    def selectable_cards(self, player: Player) -> list[int]:
        # wildcards are always selectable.
        if player != self.turn.player or ((not player.hand.can_use()) or len(self.turn.selected_cards) == 3):
            return []
        
        # two are selected
        if len(self.turn.selected_cards) == 2:
            ci1, ci2 = self.turn.selected_cards[0:2]
            # either are a wildcard
            if player.hand.cards[ci1].wildcard or player.hand.cards[ci2].wildcard:
                return [i for i in range(len(player.hand.cards)) if i not in (ci1, ci2)]
            # same armies
            if player.hand.cards[ci1].army == player.hand.cards[ci2].army:
                return [i for i in range(len(player.hand.cards)) if i not in (ci1, ci2) and 
                        (player.hand.cards[i].army == player.hand.cards[ci1].army or player.hand.cards[i].wildcard)]
            # different armies
            return [i for i in range(len(player.hand.cards)) if i not in (ci1, ci2) and (player.hand.cards[i].wildcard or
                    (player.hand.cards[i].army != player.hand.cards[ci1].army and player.hand.cards[i].army != player.hand.cards[ci2].army))]

        return [i for i in range(len(player.hand.cards)) if i not in (self.turn.selected_cards)]


    # def auto_use_cards(self, player: Player):
    #     if player != self.turn.player or not player.hand.can_use():
    #         return
        
    #     #if has a wildcard:
        

    def select_card(self, player: Player, card: int):
        if player != self.turn.player:
            return

        # deselecting a card
        if card in self.turn.selected_cards:
            self.turn.selected_cards.remove(card)
            return

        #check legality
        if card not in self.selectable_cards(player):
            return

        self.turn.selected_cards.append(card)
        
        # if 3 have been selected, submit
        if len(self.turn.selected_cards) == 3:
            cards = [x for x in player.hand.cards if player.hand.cards.index(x) in self.turn.selected_cards]
            self.turn.selected_cards = []
            for card in cards:
                player.hand.cards.remove(card)
            self.turn.cards_submitted += 1
            self.armies_remaining[player] += 2 + 2 * self.turn.cards_submitted + max(0, self.turn.cards_submitted - 5)



    def attack_roll(self, player: Player) -> bool:
        """Roll max dice for both sides. Called by the Roll button."""
        if (self.turn.stage != Stage.ATTACK or player != self.turn.player
                or self.turn.selected is None or self.battle.attacked is None):
            return False
        defender = self.battle.attacked.owner
        if defender is None:
            return False
        if not self.select_dice(player, self.active_dice(player)):
            return False
        if not self.select_dice(defender, self.active_dice(defender)):
            return False
        return self.do_damage()

    def _reset_attack(self):
        self.battle.attacker_rolls = None
        self.battle.defender_rolls = None
        self.battle.attacked = None
        self.turn.selected = None

    def skip_attacking(self, player: Player):
        if player == self.turn.player and self.turn.stage == Stage.ATTACK:
            self.turn.stage = Stage.CHECK_DEFEAT

    def can_skip(self, player: Player) -> bool:
        if player != self.turn.player or self.turn.stage in (
                Stage.TERRITORY_REINFORCEMENT, Stage.TERRITORY_SELECTION, Stage.PLACE_ARMIES):
            return False

        if self.turn.stage == Stage.ATTACK:
            return True
        if self.turn.stage == Stage.TURN_IN_CARDS and len(player.hand.cards) < 5:
            return True

        return False


    def can_skip_fortify(self, player):
        return player == self.turn.player and self.turn.stage == Stage.FORTIFY

    def skip_fortify(self):
        """Skip fortifying. end_turn clears selection."""
        if self.turn.stage == Stage.FORTIFY:
            self.end_turn()

    def _start_turn(self, player: Player):
        # Automatically get `max(controlled_territories // 3, 3)` armies
        owned = len(player.controlled_territories(self.territories))
        self.armies_remaining[player] += max(owned // 3, 3)

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
            self.turn.stage = Stage.TURN_IN_CARDS
        # otherwise, move straight to Stage.place_armies
        else:
            self.turn.stage = Stage.PLACE_ARMIES


    def end_turn(self):
        if self.turn.stage == Stage.GAME_OVER:
            return
        self._reset_attack()
        assert self.turn.player is not None
        # one card per turn if the player conquered at least one territory
        if self.turn.conquered and self.cards:
            self.turn.player.hand.add_card(self.cards.pop())
        self.turn.conquered = False

        if self.turn.stage == Stage.ATTACK:
            self.turn.stage = Stage.FORTIFY
            return


        next_index = (self.players.index(self.turn.player) + 1) % len(self.players)
        self.turn.player = self.players[next_index]
        self._start_turn(self.turn.player)
        # Enable once PLACE_ARMIES is playable and start_play fills armies_remaining
        # if self.turn.stage not in (Stage.TERRITORY_SELECTION, Stage.TERRITORY_REINFORCEMENT):
        #     self._start_turn(self.turn.player)


    def do_damage(self):
        battle = self.battle
        attacker = self.turn.selected
        if (battle.attacker_rolls is None or battle.defender_rolls is None
                or battle.attacked is None or attacker is None):
            return False

        # keep a sorted copy for the UI, highest first
        battle.last_attacker_rolls = sorted(battle.attacker_rolls, reverse=True)
        battle.last_defender_rolls = sorted(battle.defender_rolls, reverse=True)

        attack = list(battle.last_attacker_rolls)
        defend = list(battle.last_defender_rolls)
        while attack and defend:
            # ties go to the defender
            if attack.pop(0) > defend.pop(0):
                battle.attacked.armies -= 1
            else:
                attacker.armies -= 1

        if battle.attacked.armies <= 0:
            # currently moves as many armies as dice rolled
            moved = len(battle.attacker_rolls)
            defender = battle.attacked.owner
            battle.attacked.owner = self.turn.player
            battle.attacked.armies = moved
            attacker.armies -= moved
            self.turn.conquered = True
            self._reset_attack()
            self._check_defeat(defender)
        else:
            battle.attacker_rolls = None
            battle.defender_rolls = None
            if attacker.armies < 2:
                self._reset_attack()
        return True

    def _check_defeat(self, defender):
        """Remove defender if they lost their last territory.
        Ends the game if only one player is left."""
        if defender is None or defender.controlled_territories(self.territories):
            return
        self.players.remove(defender)
        if len(self.players) == 1:
            self.turn.stage = Stage.GAME_OVER

#
# 1. Determine Play Order
# 2. Color Selection
# 3. Territory Selection (continues until no unclaimed territories)
# 4. Territory Reinforcement (continues until no remaining armies)
# 5. Move to Turns
