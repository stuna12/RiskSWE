"""Human-controlled player."""

from player import Player
from country import Country

class HumanPlayer(Player):
    """A player whose moves come from GUI input."""

    def place_unoccupied(self, territories: list[Country]) -> int:
        """Choose an unclaimed territory to place an army on."""
        # human moves come from GUI clicks in game_view, not from this method
        raise NotImplementedError

    def place_occupied(self, territories: list[Country]) -> int:
        """Choose an owned territory to reinforce."""
        # human moves come from GUI clicks in game_view, not from this method
        raise NotImplementedError
