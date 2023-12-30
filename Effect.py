from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Card import Card
    from Player import Player

from colorama import Fore
import logging
logging.basicConfig(level=logging.DEBUG, format = "%(levelname)s:%(message)s")

def inRange(i):
    return -1 < i < 5

def exists(list, i):
    if i < 0: return False
    try:
        list[i]
    except IndexError:
        return False
    return True

class Effect():
    def __init__(self, card, owner: Player) -> None:
        self.card: Card = card
        self.columns: list[list[Card]] = owner.columns
        self.columns_opponent = owner.columns_opponent 

    def on_placement(self): return 
    def on_death(self): return

    def deal_damage(self, amount, relative_column = 0, where = 0, opponent = True):
        columns = self.columns_opponent if opponent else self.columns
        if not inRange(self.card.column + relative_column) or not exists(columns[self.card.column + relative_column], where):
            logging.error(Fore.RED + f"Daño fuera de rango, amount:{amount}, relative_column:{relative_column}, self.card.column:{self.card.column}, where:{where}" + Fore.WHITE)
            return
        columns[self.card.column + relative_column][where].health_left -= amount
        logging.info(Fore.GREEN + f"DAÑO: amount:{amount}, relative_column:{relative_column}, self.card.column:{self.card.column}, where:{where}" + Fore.WHITE)

        if columns[self.card.column + relative_column][where].health_left <= 0:                                              #If card was destroyed
            logging.debug(Fore.MAGENTA + f"{columns[self.card.column + relative_column][where]}" + Fore.WHITE)
            destroyed_card = columns[self.card.column + relative_column]\
                                .pop(columns[self.card.column + relative_column][where].position)                           #remove it from the column
            for card in columns[self.card.column + relative_column][where:]:                                                 #and adjust cards above it 
                card.position -= 1                                                                                           #to one position below



    def heal(self, placement, amount = 1):
        column, where = placement
        if not inRange(column) or not exists(self.columns[column], where):
            logging.error(Fore.RED + f"Cura fuera de rango, amount:{amount}, column:{column}, where:{where}" + Fore.WHITE)
            return
        
        #Health should be the minimum between max health and current health + amount to be healed
        self.columns[column][where].health_left = min(self.columns[column][where].health, self.columns[column][where].health_left + amount)
        logging.info(Fore.GREEN + f"CURA: amount:{amount}, self.card.column:{self.card.column}, where:{where}" + Fore.WHITE)
        
    def move(self, column: int, card_to_move = False, switch = False):
        card = card_to_move if card_to_move else self.card
        
        self.columns[card.column].remove(card)
        self.columns[column].append(card)
        card.column = column
        card.position = len(self.columns[column]) - 1 


class Fire(Effect):
    def __init__(self, card, columns, columns_opponent) -> None:
        super().__init__(card, columns, columns_opponent)

    def activate(self, specific_parameters = None):
        self.deal_damage(3)
        self.deal_damage(1, where = self.card.position + 1, opponent=False)


class Light(Effect):
    #Specific parameter: heal position
    def __init__(self, card, columns, columns_opponent) -> None:
        super().__init__(card, columns, columns_opponent)

    def activate(self, specific_parameters = None):
        self.deal_damage(2)
        self.heal(specific_parameters)


class Water(Effect):
    def __init__(self, card, columns, columns_opponent) -> None:
        super().__init__(card, columns, columns_opponent)

    def activate(self, specific_parameters = None):
        self.deal_damage(2)

        self.move(specific_parameters)
        self.deal_damage(1)


class Plant(Effect):
    def __init__(self, card, columns, columns_opponent) -> None:
        super().__init__(card, columns, columns_opponent)

    def activate(self, specific_parameters = None):
        pass


class Air(Effect):
    def __init__(self, card, columns, columns_opponent) -> None:
        super().__init__(card, columns, columns_opponent)

    def activate(self, specific_parameters = None):
        pass


class Thunderbolt(Effect):
    def __init__(self, card, columns, columns_opponent) -> None:
        super().__init__(card, columns, columns_opponent)

    def activate(self, specific_parameters = None):
        pass


class Ice(Effect):
    def __init__(self, card, columns, columns_opponent) -> None:
        super().__init__(card, columns, columns_opponent)

    def activate(self, specific_parameters = None):
        pass


class Earth(Effect):
    def __init__(self, card, columns, columns_opponent) -> None:
        super().__init__(card, columns, columns_opponent)

    def activate(self, specific_parameters = None):
        pass


class Crystal(Effect):
    def __init__(self, card, columns, columns_opponent) -> None:
        super().__init__(card, columns, columns_opponent)

    def activate(self, specific_parameters = None):
        pass


class Shadow(Effect):
    def __init__(self, card, columns, columns_opponent) -> None:
        super().__init__(card, columns, columns_opponent)

    def activate(self, specific_parameters = None):
        pass