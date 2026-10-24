from player import Player
from country import Country

class HumanPlayer(Player):
    def place_unoccupied(self, territories: list[Country]) -> int:
        raise NotImplementedError  # TODO: driven by GUI clicks

    def place_occupied(self, territories: list[Country]) -> int:
        raise NotImplementedError  # TODO: driven by GUI clicks
