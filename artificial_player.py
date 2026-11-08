"""
Module containing AI for Risk
"""

from country import Country
from player import Player

class ArtificialPlayer(Player):
    """
    Prototype I for AI player for Risk. Uses heuristic rules
    to determine the best moves at each phase of the game.
    """

    def border_threat(self, territory: Country, territories: list[Country]) -> int:
        """
        Determines the 'border threat' a territory has.
        Returns the highest number of troops an adjacent
        enemy territory has.
        """

        return max((
            territories[i].armies for i in territory.adj
            if territories[i].owner != self),
        default=0)


    def reinforcement_priority(self, territory: Country, territories: list[Country],
                               placements: list[Country]) -> int:
        """
        Determines the priority that a territory
        needs to be reinforced by, taking into account
        the border threat, the current amount of troops,
        and planned amount of troops to be reinforced to
        the territory.
        """
        planned = territory.armies + placements.count(territory)
        return self.border_threat(territory, territories) - planned


    def attack_advantage(self, *pair) -> int:
        """
        Returns the difference of troops in the
        attacking territory vs the defending territory,
        leaving one in the attacking territory.

        Used as a max() key, hense the *pair arg field.
        """
        return pair[0].armies - 1 - pair[1].armies


    def reinforce(self, troops: int, territories: list[Country]) -> list[Country]:
        """
        Returns a list of territories in which one troop will be added to. 
        Some territories can appear more than once.
        """
        mine = self.controlled_territories(territories)

        border = [
            territory for territory in mine
            if any(territories[i].owner != self for i in territory.adj)
        ]

        placements = []
        for _ in range(troops):
            best = border[0]
            for territory in border:
                if (self.reinforcement_priority(territory, territories, placements)
                        > self.reinforcement_priority(best, territories, placements)):
                    best = territory

            placements.append(best)

        return placements


    def attack(self, territories: list[Country]) -> tuple[Country, Country] | None:
        """
        Returns the best territory to attack from own territory. 
        Returns None if no territories are worth attacking.
        """
        candidates = [
            (mine, territories[j])
            for mine in self.attackable_territories(territories)
            for j in mine.adj if territories[j].owner != self
        ]

        if not candidates:
            return None

        best = max(candidates, key=self.attack_advantage)

        if self.attack_advantage(*best) < 1:
            return None

        return best


    def fortify(self, territories: list[Country]) -> tuple[Country, Country, int] | None:
        """
        Returns the territory that needs the most fortification, if it can be fortified. 
        Returns None otherwise.
        """
        best: tuple[Country, Country, int] | None = None
        best_amount = 0

        for source in self.controlled_territories(territories):
            spare = max(0, source.armies - 1 - self.border_threat(source, territories))

            if spare == 0:
                continue

            for destination_id in source.adj:
                destination = territories[destination_id]
                if destination.owner != self:
                    continue

                need = self.border_threat(destination, territories) + 1 - destination.armies

                amount = min(spare, need)
                if amount > best_amount:
                    best = (source, destination, amount)
                    best_amount = amount

        return best
