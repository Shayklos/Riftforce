from __future__ import annotations
from random import choice,choices
from Effect import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Player import Player


FACTIONS = ('Agua', 'Fuego', 'Luz', 'Planta', 'Aire', 'Rayo', 'Hielo', 'Tierra', 'Cristal', 'Sombra')
FACTION_EMOJI = {'Agua' : '💧',
                 'Planta':'🍀',
                 'Rayo' :'⚡',
                 'Aire': '☁',
                 'Hielo':'❄',
                 'Tierra':'🟤',
                 'Luz':'💡',
                 'Cristal':'💎',
                 'Fuego':'🔥',
                 'Sombra':'🌑'
}

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

    def __init__(self, health, faction, owner) -> None:
        self.owner: Player = owner
        self.health = health
        self.health_left = health
        self.faction = faction
        self.column = None
        self.position = None
        self.effect: Effect = self.getEffect()

    def __str__(self) -> str:
        return f"{self.health_left}{FACTION_EMOJI[self.faction]}{self.health}"
    

    def __repr__(self) -> str:
        return f"{self.faction}: {self.health_left}/{self.health}"
    

    def getEffect(self):
        ('Agua', 'Fuego', 'Luz', 'Planta', 'Aire', 'Rayo', 'Hielo', 'Tierra', 'Cristal', 'Sombra')
        match self.faction:
            case 'Fuego': effect = Fire
            case 'Luz': effect = Light    
            case 'Agua': effect = Water
            case 'Planta': effect = Plant
            case 'Aire': effect = Air
            case 'Rayo': effect = Thunderbolt
            case 'Hielo': effect = Ice
            case 'Tierra': effect = Earth
            case 'Cristal': effect = Crystal
            case 'Sombra': effect = Shadow
        return effect(self, self.owner)

    def activate(self, specific_parameters = []): self.effect.activate(specific_parameters)
    def on_placement(self): self.effect.on_placement()
    def on_death(self): self.effect.on_death()
    

if __name__ == '__main__':
    x = Card(6, 'Fuego')
    x.column = 2
    x.position = 0

    x.activate()