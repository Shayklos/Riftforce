from Faction import Faction
from random import shuffle
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Player import Player

class Deck():
    def __init__(self, factions, owner) -> None:
        # self.owner: Player = owner
        self.list: list = []
        for faction in factions:
            self.list += Faction(faction, owner).cards

        self.shuffle()

    def __repr__(self) -> str:
        s = ""
        for card in self.list:
            s += f"{card.faction}: {card.health_left}/{card.health}, "

        return s
    
    def shuffle(self):
        shuffle(self.list)
    
# print(Deck(('Water', 'Fire')).deck[0] )