from card import Card

class Hand:
    
    def __init__(self) -> None:
        self.cards: list[Card] = []
    
    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    def can_use(self) -> bool:
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
        