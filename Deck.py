from Faction import Faction
from random import shuffle


class Deck():
    def __init__(self, factions) -> None:
        self.list: list = []
        for faction in factions:
            self.list += Faction(faction).cards

        self.shuffle()

    def __repr__(self) -> str:
        s = ""
        for card in self.list:
            s += f"{card.faction}: {card.health_left}/{card.health}, "

        return s
    
    def shuffle(self):
        shuffle(self.list)
    
# print(Deck(('Agua', 'Fuego')).deck[0] )