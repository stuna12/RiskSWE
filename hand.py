"""A player's hand of Risk cards."""

from card import Card
from cardcomponent import CardComponent

WIDTH_MUL = 1 / 20
HEIGHT_MUL = 1 / 10
PADDING_MUL = 1 / 5

class Hand:
    """Holds a player's cards and checks whether a set can be traded in."""

    def __init__(self) -> None:
        self.cards: list[Card] = []
        self.components: list[CardComponent] = []
        self.arranged: bool = True

    def add_card(self, card: Card) -> None:
        """Add a card to the hand."""
        self.cards.append(card)
        self.components.append(CardComponent(card))
        self.arranged = False

    def can_use(self) -> bool:
        """Return True if the hand contains a set that can be traded in."""
        # must have at least 3 cards
        if len(self.cards) < 3:
            return False

        # either has a wildcard, three of one type, or at least one of each
        has_wildcard = False
        types: list[int] = [0,0,0]
        for card in self.cards:
            if card.wildcard:
                has_wildcard = True
            else:
                types[card.army] += 1
        return has_wildcard or any(t >= 3 for t in types) or all(t >= 1 for t in types)

    def has_wildcard(self) -> bool:
        """Return True if hand contains at least one wildcard"""
        has_wildcard = False
        for card in self.cards:
            if card.wildcard:
                has_wildcard = True
        return has_wildcard

    def arrange_components(self, width: int, height: int):
        """Arranges CardComponent objects on the screen to ensure accurate placement"""
        num_cards = len(self.cards)
        card_width = width * WIDTH_MUL
        card_height = height * HEIGHT_MUL
        card_padding = card_width * PADDING_MUL
        total_width = card_width * num_cards + card_padding * (num_cards - 1)
        left = width / 2 - total_width / 2
        for i, comp in enumerate(self.components):
            comp.update_bounds(left + (card_width + card_padding) * i, 0,
                            card_width, card_height)
        self.arranged = True

    def hovered(self) -> int:
        """Returns the index of the card being hovered, returning -1 if no such card exists"""
        if not self.arranged:
            return -1
        for i, comp in enumerate(self.components):
            if comp.is_hovered:
                return i
        return -1

    def check_hover(self, mouse_x: int, mouse_y: int):
        """Checks if the given mouse coordinates fall into any subordinate card bounds"""
        if not self.arranged:
            return

        for component in self.components:
            component.check_hover(mouse_x, mouse_y)

    def draw(self, selectable: list[int], selected: list[int]):
        """Draws the hand to the screen"""
        for i, comp in enumerate(self.components):
            comp.active = i in selectable
            comp.selected = i in selected
            comp.draw()
