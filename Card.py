from random import choice,choices
from Effect import *

FACTIONS = ('Agua', 'Fuego', 'Luz', 'Planta', 'Aire')

class Card():
    def random(placed = True):
        card = Card(
            choice([5,6,7]), 
            choice(FACTIONS)            
            )
        if placed: 
            card.column = choice([0,1,2,3,4,5]) 
            card.position = choice([0,1,2]) 
        else: card.column = None 
            
        return card

    def __init__(self, health, faction) -> None:
        self.health = health
        self.health_left = health
        self.faction = faction
        self.column = None
        self.position = None

    def __str__(self) -> str:
        return f"{self.faction}: {self.health_left}/{self.health}"
    
    def __repr__(self) -> str:
        return f"{self.faction}: {self.health_left}/{self.health}"
    
    def activate(self, columns, columns_opponent, specific_parameters = []):
        match self.faction:
            case 'Fuego':
                effect = Fire

        effect(self, columns, columns_opponent, specific_parameters).activate()

    

if __name__ == '__main__':
    x = Card(6, 'Fuego')
    x.column = 2
    x.position = 0

    x.activate()