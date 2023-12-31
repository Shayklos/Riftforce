from Card import Card

class Faction():
    HEALTH_LOW = 5
    HEALTH_MID = 6
    HEALTH_HIGH = 7

    NUM_LOW = 4
    NUM_MID = 3
    NUM_HIGH = 2

    def __init__(self, faction, owner) -> None:
        self.cards =  Faction.NUM_LOW*[Card(Faction.HEALTH_LOW, faction, owner)]\
                    + Faction.NUM_MID*[Card(Faction.HEALTH_MID, faction, owner)]\
                    + Faction.NUM_HIGH*[Card(Faction.HEALTH_HIGH, faction, owner)]                 

