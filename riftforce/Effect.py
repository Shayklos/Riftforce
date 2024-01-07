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
    if i is None: return False
    if i < 0: return False
    try:
        list[i]
    except IndexError:
        return False
    return True

class Effect():
    def __init__(self, card) -> None:
        self.card: Card = card
        self.owner: Player = self.card.owner
        self.has_killed = False

    def on_placement(self, param = None): return 
    def on_death(self): self.owner.opponents_score[0] += 1
    def on_kill(self): return

    def damage(self, amount: int, relative_column: int = 0, where: int = 0, opponent: bool = True):

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
    def __init__(self, card) -> None:
        super().__init__(card)

    def activate(self, _):
        self.damage(3)
        self.damage(1, where = self.card.position + 1, opponent=False)


class Light(Effect):
    """
    Place 3 damage on the first enemy at this location.
    Remove 1 damage from this Light or any ally.
    """
    def __init__(self, card) -> None:
        super().__init__(card)

    def activate(self, heal_placement : (int, int)):
        self.damage(2)
        self.heal(heal_placement)


class Water(Effect):
    """
    Place 2 damage on the first enemy at this location.
    Move this water to an adjacent location.
    Place 1 damage on the first enemy at the new location.
    """
    def __init__(self, card) -> None:
        super().__init__(card)

    def activate(self, column_to_move):
        self.damage(2)
        assert abs(self.card.column - column_to_move) == 1, "Water didn't move to adjacent position"
        self.move(column_to_move)
        self.damage(1)


class Plant(Effect):
    """
    Place 2 damage on the first enemy in an adjacent location.
    Move this enemy to the location of this Plant.
    """
    def __init__(self, card) -> None:
        super().__init__(card)

    def activate(self, column):
        assert abs(column - self.card.column) == 1, 'Destiny column is not adyacent to Plant\'s column'
        self.damage(2, column - self.card.column)
        if self.has_killed: #It should move the *damaged* enemy
            self.has_killed = False
            return
        self.move(self.card.column, (column, 0), own_card = False)


class Air(Effect):
    """
    Move this Air to any other location.
    Place 1 damage each on the first enemy at the new and the adjacent locations.
    """
    def __init__(self, card) -> None:
        super().__init__(card)

    def activate(self, column_destination):
        assert column_destination != self.card.column, "El elemental de aire tiene que moverse"
        self.move(column_destination)
        self.damage(1, -1)
        self.damage(1, 0)
        self.damage(1, 1)


class Thunderbolt(Effect):
    """
    Place 2 damage on any enemy at this location.
    If the thunderbolt destroys this enemy repeat this ability once immediately.
    """
    def __init__(self, card) -> None:
        super().__init__(card)

    def activate(self, positions):
        self.damage(2, where = positions[0])
        if self.has_killed:
            self.damage(2, where = positions[1])
            self.has_killed = False


class Ice(Effect):
    """
    If there is damage on the last enemy at this location place 4 damage on it.
    Otherwise, place 1 damage on it.
    """
    def __init__(self, card) -> None:
        super().__init__(card)

    def activate(self, _):
        try:
            card_to_be_damaged: Card = self.owner.columns_opponent[self.card.column][-1]
        except:
            logging.warning(Fore.YELLOW + f"{self.card} activated but didn't find anyone to damage. column: {self.card.column}" + Fore.WHITE)
            return 

        amount = 4 if card_to_be_damaged.isDamaged() else 1
        self.damage(amount, where = len(self.owner.columns_opponent[self.card.column])-1)


class Earth(Effect):
    """
    When you play this Earth place 1 damage on each enemy at this location.
    Place 2 damage on the first enemy at this location.
    """
    def __init__(self, card) -> None:
        super().__init__(card)

    def on_placement(self, _):
        column = self.owner.columns_opponent[self.card.column]
        for card in reversed(column):
            self.damage(1, where = card.position)

    def activate(self, _):
        self.damage(2)


class Crystal(Effect):
    """
    Place 4 damage on the first enemy at this location.
    When this Crystal is destroyed your opponent gains +1 Riftforce.
    """
    def __init__(self, card) -> None:
        super().__init__(card)

    def activate(self, _):
        self.damage(4)

    def on_death(self): self.owner.opponents_score[0] += 2


class Shadow(Effect):
    """
    Move this Shadow to any other location
    Place 1 damage on the first enemy at the new location
    If the Shadows destroys this enemy gain +1 Riftforce
    """
    def __init__(self, card) -> None:
        super().__init__(card)

    def activate(self, column_destination):
        assert column_destination != self.card.column, "El elemental de sombra tiene que moverse"
        self.move(column_destination)
        self.damage(1)

    def on_kill(self): self.owner.score[0] += 1

# --------- Riftforce Beyond ---------
    
class Beast(Effect):
    """
    Move this Beast to an adjacent location
    If there is damage on this Beast, place 3 damage on the first enemy at this location
    Otherwise, place 2 damage on it
    """
    def __init__(self, card) -> None:
        super().__init__(card)

    def activate(self, column_destination):
        assert abs(self.card.column - column_destination) == 1, "Beast didn't move to adjacent position"
        self.move(column_destination)
        self.damage(3) if self.card.isDamaged() else self.damage(2)


class Sand(Effect):
    """
    Move this Sand to any other location
    Place 1 damage on each enemy at this location
    Remove 1 damage from this Sand
    """
    def __init__(self, card) -> None:
        super().__init__(card)

    def activate(self, column_destination):
        assert column_destination != self.card.column, "Sand has to move"
        self.move(column_destination)

        column = self.owner.columns_opponent[column_destination] 
        for card in reversed(column):
            self.damage(1, where = card.position)

        self.heal((self.card.column, self.card.position))


class Lava(Effect):
    """
    Place 2 damage each on the first enemy at the adjacent locations
    Place 1 damage each on this Lava and all allies in front of this Lava
    """
    def __init__(self, card) -> None:
        super().__init__(card)

    def activate(self, _):
        self.damage(2, 1)
        self.damage(2, -1)

        splash = self.card.position
        while splash > -1:
            self.damage(1, where = splash, opponent=False)
            splash -= 1


class Sound(Effect):
    """
    Place 2 damage each on the first enemy at this location
    If the Music destroys this enemy, play it on your side of the Rift at an adjacent location
    """
    def __init__(self, card) -> None:
        super().__init__(card)

    def activate(self, column_destination):
        #If there are cards (to avoid IndexError) and first card will be killed
        if len(self.card.owner.columns_opponent[self.card.column]) and self.card.owner.columns_opponent[self.card.column][0].health_left <= 2:
            #Get card data and then place it on your board
            stolen_card: Card = self.card.owner.columns_opponent[self.card.column].pop(0)
            stolen_card.health_left = stolen_card.health
            stolen_card.owner = self.card.owner
            stolen_card.owner.play([stolen_card], [column_destination])
        else:
            self.damage(2)


class Acid(Effect):
    """
    Place 3 damage on the first enemy at this location
    Place 1 damage on the second enemy at this location
    If this Acid destroys an enemy gain no Riftforce
    Aclaration: If the first 3 damage kill the enemy, the 1 damage will kill the now-second, before third, card
    """
    def __init__(self, card) -> None:
        super().__init__(card)

    def activate(self, _):
        #Make sure the score before and after damaging is the same
        current_score = self.owner.score[0]
        self.damage(3)
        if self.has_killed:
            self.damage(1)
        else:
            self.damage(1, where = 1)
        self.has_killed = False
        self.owner.score[0] = current_score


class Star(Effect):
    """
    Place 2 damage on the first enemy at this location
    If you have less than 7 elementals in your hand, draw 1 elemental
    """
    def __init__(self, card) -> None:
        super().__init__(card)

    def activate(self, _):
        self.damage(2)
        if len(self.owner.hand) < 7:
            if len(self.owner.deck.list):
                self.owner.hand.append(self.owner.deck.list.pop(0))
            else:
                self.owner.deck.list = self.owner.discard_pile
                self.owner.deck.shuffle()

                self.owner.discard_pile = []


class Love(Effect):
    """
    When you play this Love, remove all dammage from one ally at this location
    Place 2 damage on the first enemy at this location
    """
    def __init__(self, card) -> None:
        super().__init__(card)

    def activate(self, _):
        self.damage(2)

    def on_placement(self, card_position_to_heal):
        self.heal((self.card.column, card_position_to_heal), amount = 99)


class Magnet(Effect):
    """
    Place 2 damage on the last enemy at this location
    Move this enemy and this Magnet to and adjacent location 
    Aclaration: Magnet cannot stay in the same location
    """
    def __init__(self, card) -> None:
        super().__init__(card)

    def activate(self, column_destination):
        assert abs(self.card.column - column_destination) == 1, "Magnet didn't move to adjacent position"

        try:
            card_to_be_damaged: Card = self.owner.columns_opponent[self.card.column][-1]
        except:
            logging.warning(Fore.YELLOW + f"{self.card} activated but didn't find anyone to damage. column: {self.card.column}" + Fore.WHITE)
            self.move(column_destination)
            return 

        if card_to_be_damaged.health_left <= 2:
            self.damage(2, where = len(self.owner.columns_opponent[self.card.column])-1)
            self.move(column_destination)

        else:
            self.damage(2, where = len(self.owner.columns_opponent[self.card.column])-1)
            self.move(column_destination)
            self.move(column_destination, (card_to_be_damaged.column, card_to_be_damaged.position), own_card=False)
        