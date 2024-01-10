from __future__ import annotations
from random import choice,choices
from Effect import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Player import Player


FACTION_EMOJI = {'Water' : '💧',
                 'Plant':'🍀',
                 'Thunderbolt' :'⚡',
                 'Air': '🌪',
                 'Ice':'❄',
                 'Earth':'✊🏾',
                 'Light':'💡',
                 'Crystal':'💎',
                 'Fire':'🔥',
                 'Shadow':'🌑',
                 'Beast':'🐺',
                 'Sand':'⏳',
                 'Lava':'🌋',
                 'Sound':'🎶',
                 'Acid':'💀',
                 'Love':'💜',
                 'Star':'🌠',
                 'Magnet':'🧲'

}
FACTIONS = list(FACTION_EMOJI.keys())

class Card():
    def random(placed = True):
        card = Card(
            choice([5,6,7]), 
            choice(FACTIONS),
            None           
            )
        if placed: 
            card.column = choice([0,1,2,3,4,5]) 
            card.position = choice([0,1,2]) 
        else: card.column = None 
            
        return card

    def __init__(self, health: int, faction: str, owner: Player) -> None:
        self.owner: Player = owner
        self.health: int = health
        self.health_left: int = health
        self.faction: str = faction
        assert faction in FACTIONS
        self.column: int | None = None
        self.position: int | None = None
        self.effect: Effect = self.getEffect()

    def __str__(self) -> str:
        return f"{self.health_left}{FACTION_EMOJI[self.faction]}{self.health}"
    

    def __repr__(self) -> str:
        return f"{self.faction}: {self.health_left}/{self.health}"
    
    def isCompatible(self, cards: list[Card]) -> bool:
        if len(cards) > 2: return False 
        numbers = [self.health]
        factions = [self.faction]
        for card in cards:
            numbers.append(card.health)
            factions.append(card.faction)

        return len(set(numbers)) == 1 or len(set(factions)) == 1

    def isDamaged(self) -> bool:
        return bool(self.health - self.health_left)

    def getEffect(self):
        match self.faction:
            case 'Fire': effect = Fire
            case 'Light': effect = Light    
            case 'Water': effect = Water
            case 'Plant': effect = Plant
            case 'Air': effect = Air
            case 'Thunderbolt': effect = Thunderbolt
            case 'Ice': effect = Ice
            case 'Earth': effect = Earth
            case 'Crystal': effect = Crystal
            case 'Shadow': effect = Shadow
            case 'Beast': effect = Beast
            case 'Sand': effect = Sand
            case 'Lava': effect = Lava
            case 'Sound': effect = Sound
            case 'Acid': effect = Acid
            case 'Love': effect = Love
            case 'Star': effect = Star
            case 'Magnet': effect = Magnet
        return effect(self)

    def activate(self, specific_parameters = None): self.effect.activate(specific_parameters)
    def on_placement(self, param = None): self.effect.on_placement(param)
    def on_death(self): self.effect.on_death()
    def on_kill(self): self.effect.on_kill()