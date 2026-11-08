"""Risk cards: creation, decks, and dealing."""

from __future__ import annotations
from typing import TYPE_CHECKING

# fixes circular import issue, as Hand is only used for type checking in this class
if TYPE_CHECKING:
    from hand import Hand

TERRITORY_COUNT = 42

class Card:
    """A Risk card showing a territory and army type, or a wildcard."""

    def __init__(self, territory: int, army: int, wildcard: bool):
        self.territory = territory
        self.army = army
        self.wildcard = wildcard

    @classmethod
    def new_wildcard(cls) -> "Card":
        """Create a wildcard."""
        return cls(-1, -1, True)

    @classmethod
    def new_card(cls, territory: int, army: int) -> "Card":
        """Create a regular territory card."""
        return cls(territory, army, False)

    @classmethod
    def new_deck(cls, keep_wilds: bool = True) -> list["Card"]:
        """Build a full (unshuffled) deck, optionally including two wildcards."""
        deck: list[Card] = []
        tc = TERRITORY_COUNT//3
        for army in range(3):
            for territory in range(tc):
                deck.append(Card.new_card(territory + tc * army, army))
        if keep_wilds:
            deck.append(Card.new_wildcard())
            deck.append(Card.new_wildcard())
        return deck

    @classmethod
    def draw(cls, hands: list["Hand"], deck: list["Card"], n: int):
        """Deal n cards to each hand, round-robin, from the top of the deck."""
        num_hands = len(hands)

        for i in range(n * num_hands):
            index = i % num_hands
            hands[index].add_card(deck.pop())

    def army_name(self):
        """Return the display name of this card's army type."""
        if self.army == 0:
            return "Infantry"
        if self.army == 1:
            return "Cavalry"
        return "Artillery"
