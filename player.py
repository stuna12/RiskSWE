from hand import Hand
from abc import ABC, abstractmethod
from country import Country
from arcade.types import Color

class Player(ABC):
    def __init__(self, color: Color, name: str = "Player") -> None:
        self.color: Color = color
        self.name: str = name
        self.hand: Hand = Hand()
    
    def controlled_territories(self, territories: list[Country]) -> list[Country]:
        controlled = []
        for territory in territories:
            if territory.owner == self:
                controlled.append(territory)
        return controlled
    
    def attackable_territories(self, territories: list[Country]) -> list[Country]:
        attackable = []
        for territory in self.controlled_territories(territories):
            # adj holds indices into `territories`
            if any(territories[j].owner != self for j in territory.adj):
                attackable.append(territory)
        return attackable

    def available_troops(self, territories):
        available = 0
        # The number of territories you occupy
        available += max(3, len(self.controlled_territories(territories))//3)
        # The value of the continents you control (TODO)
        
        # The value of the matched sets of RISK cards you trade in  (TODO)
        # The specific territory pictured on a traded-in card       (TODO)

        return available

    @abstractmethod
    def place_unoccupied(self, territories: list[Country]) -> int:
        pass
    
    @abstractmethod
    def place_occupied(self, territories: list[Country]) -> int:
        pass
