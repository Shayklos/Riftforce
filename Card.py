from random import choice,choices
FACTIONS = ('Agua', 'Fuego', 'Luz', 'Planta', 'Aire')

class Card():
    def random():
        return Card(
            choice([5,6,7]), 
            choice(FACTIONS)            
            )

    def __init__(self, health, faction) -> None:
        self.health = health
        self.health_left = health
        self.faction = faction

    def __str__(self) -> str:
        return f"{self.faction}: {self.health_left}/{self.health}"
    
    def __repr__(self) -> str:
        return f"{self.faction}: {self.health_left}/{self.health}"
    

if __name__ == '__main__':
    x = Card.random()
    print(x)