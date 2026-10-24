from hand import Hand
from abc import ABC, abstractmethod
from country import Country

class Player(ABC):
    def __init__(self, color: tuple[int, ...], name: str = "Player") -> None:
        self.color = color
        self.name = name
        self.hand = Hand()
    
    def controlled_territories(self, territories: list[Country]) -> list[Country]:
        controlled = []
        for territory in territories:
            if territory.owner == self:
                controlled.append(territory)
        return controlled
    
    def attackable_territories(self, territories: list[Country]) -> list[Country]:
        attackable = set()
        for territory in self.controlled_territories(territories):
            for candidate in territory.neighbors:
                if candidate.owner != self:
                    attackable.add(territory)
        return list(attackable)

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
