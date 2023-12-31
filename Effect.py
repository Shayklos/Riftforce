from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Card import Card
    from Player import Player

from colorama import Fore
import logging


def inRange(i) -> bool: 
    return -1 < i < 5

def exists(list, i) -> bool:
    if i < 0: return False
    try:
        list[i]
    except IndexError:
        return False
    return True

class Effect():
    def __init__(self, card, owner: Player) -> None:
        self.card: Card = card
        self.owner: Player = owner
        self.has_killed = False

    def on_placement(self): return 
    def on_death(self): self.owner.opponents_score += 1
    def on_kill(self): return

    def deal_damage(self, amount: int, relative_column: int = 0, where: int = 0, opponent: bool = True):

        #Select set of columns where damage is going to be dealt
        columns = self.owner.columns_opponent if opponent else self.owner.columns

        #Check if there is a card in the given position
        if not inRange(self.card.column + relative_column) or not exists(columns[self.card.column + relative_column], where):
            logging.warning(Fore.YELLOW + f"Daño fuera de rango, amount:{amount}, relative_column:{relative_column}, self.card.column:{self.card.column}, where:{where}" + Fore.WHITE)
            return
        
        #Reduce damaged card's health
        columns[self.card.column + relative_column][where].health_left -= amount
        logging.info(Fore.GREEN + f"DAÑO: amount:{amount}, relative_column:{relative_column}, self.card.column:{self.card.column}, where:{where}" + Fore.WHITE)

        #Destroy card if health is reduced to 0
        if columns[self.card.column + relative_column][where].health_left <= 0:                                 #If card was destroyed
            logging.debug(Fore.MAGENTA + f"{columns[self.card.column + relative_column][where]}" + Fore.WHITE)
            destroyed_card: Card = columns[self.card.column + relative_column]\
                                    .pop(columns[self.card.column + relative_column][where].position)           #remove it from the column
            for card in columns[self.card.column + relative_column][where:]:                                    #and adjust cards above it 
                card.position -= 1                                                                              #to one position below

            #Activate card on_kill effect
            self.on_kill()
            self.has_killed = True

            #Activate destroyed_card on_death effect
            destroyed_card.on_death()

    def heal(self, placement: list[int, int], amount: int = 1):
        #Position of the card to be healed
        column, where = placement

        #Check if there is a card in the given position
        if not inRange(column) or not exists(self.owner.columns[column], where):
            logging.warning(Fore.YELLOW + f"Cura fuera de rango, amount:{amount}, column:{column}, where:{where}" + Fore.WHITE)
            return

        #Health should be the minimum between max health and current health + amount to be healed
        self.owner.columns[column][where].health_left = min(
            self.owner.columns[column][where].health, 
            self.owner.columns[column][where].health_left + amount
            )
        logging.info(Fore.GREEN + f"CURA: amount:{amount}, self.card.column:{self.card.column}, where:{where}" + Fore.WHITE)
        
    def move(self, column_destination: int, card_placement: list[int, int] | None = None, own_card = True, switch = False):
        #Select set of columns
        columns = self.owner.columns if own_card else self.owner.columns_opponent
        
        #Select card to move, defaults to self.card
        if card_placement:
            column, where = card_placement
            if not inRange(column) or not exists(columns[column], where):
                logging.warning(Fore.YELLOW + f"Movimiento fuera de rango, column_destination: {column_destination}, card_placement: {card_placement}, own_card: {own_card}, switch: {switch}" + Fore.WHITE)
                return
            card =  columns[column][where]
        else: 
            card = self.card

        #Remove card from current column, move it to the last position of the column to move
        columns[card.column].remove(card)
        columns[column_destination].append(card)
        logging.info(Fore.GREEN + f"MOVIMIENTO {self.card}: column_destination: {column_destination}, card_placement: {card_placement}, own_card: {own_card}, switch: {switch}" + Fore.WHITE)
        
        #Update card placement
        card.column = column_destination
        card.position = len(columns[column_destination]) - 1 


class Fire(Effect):
    """
    Place 3 damage on the first enemy at this location.
    Place 1 damage on the ally directly behind this fire.
    """
    def __init__(self, card, owner) -> None:
        super().__init__(card, owner)

    def activate(self, _):
        self.deal_damage(3)
        self.deal_damage(1, where = self.card.position + 1, opponent=False)


class Light(Effect):
    """
    Place 3 damage on the first enemy at this location.
    Remove 1 damage from this Light or any ally.
    """
    def __init__(self, card, owner) -> None:
        super().__init__(card, owner)

    def activate(self, heal_placement : (int, int)):
        self.deal_damage(2)
        self.heal(heal_placement)


class Water(Effect):
    """
    Place 2 damage on the first enemy at this location.
    Move this water to an adjacent location.
    Place 1 damage on the first enemy at the new location.
    """
    def __init__(self, card, owner) -> None:
        super().__init__(card, owner)

    def activate(self, column_to_move):
        self.deal_damage(2)
        assert abs(self.card.column - column_to_move) == 1, "Water didn't move to adjacent position"
        self.move(column_to_move)
        self.deal_damage(1)


class Plant(Effect):
    """
    Place 2 damage on the first enemy in an adjacent location.
    Move this enemy to the location of this Plant.
    """
    def __init__(self, card, owner) -> None:
        super().__init__(card, owner)

    def activate(self, column):
        assert abs(column - self.card.column) == 1, 'Destiny column is not adyacent to Plant\'s column'
        self.deal_damage(2, column - self.card.column)
        if self.has_killed: #It should move the *damaged* enemy
            self.has_killed = False
            return
        self.move(self.card.column, (column, 0), own_card = False)


class Air(Effect):
    """
    Move this Air to any other location.
    Place 1 damage each on the first enemy at the new and the adjacent locations.
    """
    def __init__(self, card, owner) -> None:
        super().__init__(card, owner)

    def activate(self, specific_parameters = None):
        pass


class Thunderbolt(Effect):
    """
    Place 2 damage on any enemy at this location.
    If the thunderbolt destroys this enemy repeat this ability once immediately.
    """
    def __init__(self, card, owner) -> None:
        super().__init__(card, owner)

    def activate(self, specific_parameters = None):
        pass


class Ice(Effect):
    """
    If there is damage on the last enemy at this location place 4 damage on it.
    Otherwise, place 1 damage on it.
    """
    def __init__(self, card, owner) -> None:
        super().__init__(card, owner)

    def activate(self, specific_parameters = None):
        pass


class Earth(Effect):
    """
    When you play this Earth place 1 damage on each enemy at this location.
    Place 2 damage on the first enemy at this location.
    """
    def __init__(self, card, owner) -> None:
        super().__init__(card, owner)

    def on_placement(self):
        column = self.owner.columns_opponent[self.card.column]
        for card in column:
            self.deal_damage(1, where = card.position)

    def activate(self, specific_parameters = None):
        self.deal_damage(2)


class Crystal(Effect):
    """
    Place 4 damage on the first enemy at this location.
    When this Crystal is destroyed your opponent gains +1 Riftforce.
    """
    def __init__(self, card, owner) -> None:
        super().__init__(card, owner)

    def activate(self, specific_parameters = None):
        pass


class Shadow(Effect):
    """
    Move this Shadow to any other location
    Place 1 damage on the first enemy at the new location
    If the Shadows destroys this enemy gain +1 Riftforce
    """
    def __init__(self, card, owner) -> None:
        super().__init__(card, owner)

    def activate(self, specific_parameters = None):
        pass