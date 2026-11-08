"""Base player class shared by human and AI players."""

from abc import ABC

from arcade.types import Color

from country import Country
from hand import Hand

class Player(ABC):
    """Common player state: color, name, and hand of cards."""

    def __init__(self, color: Color, name: str = "Player") -> None:
        self.color: Color = color
        self.name: str = name
        self.hand: Hand = Hand()

    def controlled_territories(self, territories: list[Country]) -> list[Country]:
        """Return the territories owned by this player."""
        controlled: list[Country] = []
        for territory in territories:
            if territory.owner == self:
                controlled.append(territory)
        return controlled

    def attackable_territories(self, territories: list[Country]) -> list[Country]:
        """Return owned territories that border at least one enemy territory."""
        attackable: list[Country] = []
        for territory in self.controlled_territories(territories):
            # adj holds indices into `territories`
            if any(territories[j].owner != self for j in territory.adj):
                attackable.append(territory)
        return attackable

    def available_troops(self, territories: list[Country]):
        """Return the number of reinforcement troops available this turn."""
        available = 0
        # The number of territories you occupy
        available += max(3, len(self.controlled_territories(territories))//3)
        # The value of the continents you control (TODO)

        # The value of the matched sets of RISK cards you trade in  (TODO)
        # The specific territory pictured on a traded-in card       (TODO)

        return available
