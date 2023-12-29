from Card import Card

class Faction():
    def __init__(self, faction) -> None:
        self.cards = 4*[Card(5, faction)] + 3*[Card(6, faction)] + 2*[Card(7, faction)]

