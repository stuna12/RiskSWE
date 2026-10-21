from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hand import Hand # fixes circular import issue, as Hand is only used for type checking in this class

TERRITORY_COUNT = 42

class Card:
    def __init__(self, territory: int, army: int, wildcard: bool):
        self.territory = territory
        self.army = army
        self.wildcard = wildcard

    @classmethod
    def new_wildcard(cls) -> "Card":
        return cls(-1, -1, True)

    @classmethod
    def new_card(cls, territory: int, army: int) -> "Card":
        return cls(territory, army, False)

    @classmethod
    def new_deck(cls, keep_wilds: bool = True) -> list["Card"]:
        deck = []
        tc = TERRITORY_COUNT//3
        for army in range(3):
            for territory in range(tc):
                deck.append(Card.new_card(territory + tc * army, army))
        if keep_wilds:
            deck.append(Card.new_wildcard())
            deck.append(Card.new_wildcard())
        return deck

    @classmethod
    def draw(cls, hands: list["Hand"], deck: list["Card"], n: int) -> list["Card"]:
        num_hands = len(hands)

        for i in range(n * num_hands):
            index = i % num_hands
            hands[index].add_card(deck.pop())
