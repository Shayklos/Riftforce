from Deck import Deck
from Card import Card
from time import perf_counter
from Board import Board
import logging
from colorama import Fore 

class Player():
    def __init__(self, factions: list[str]) -> None:
        self.discard_pile: list[Card] = []
        self.hand: list[Card] = []
        self.columns: list[list[Card]] = [[], [], [], [], []]
        self.columns_opponent: list[list[Card]] = [[], [], [], [], []]
        self.score: list[int] = [0]             #scores are list to use reference instead of value
        self.opponents_score: list[int] = [0]
        self.deck = Deck(factions, self)
        self.factions: list[str] = factions

    def __str__(self) -> str:
        s = "Factions: "
        for faction in self.factions:
            s += f"{faction}, "
        s = s[:-2] + ". "
        s += f"Cards discarded: {len(self.discard_pile)}. Cards in hand: {len(self.hand)}. Score: {self.score}. "

        return s

    def generateBoard(self):
        self.board = Board(self.columns, self.columns_opponent)

    def draw(self):
        while len(self.hand) < 7:
            if len(self.deck.list):
                self.hand.append(self.deck.list.pop(0))

            else:
                self.deck.list = self.discard_pile
                self.deck.shuffle()

                self.discard_pile = []

    def sort_hand(self):
        self.hand.sort(key = lambda card : (card.health, card.faction))

    def play_placements_are_correct(self, cards: list[Card], placements: list) -> bool: 
        #Check cards are valid
        if len(cards) > 3:
            print("Como mucho puedes jugar tres cartas en un turno.")
            return False

        #Check placements are valid
        if len(placements) != len(cards):
            print(f"Distinto número de placements ({len(placements)}) y cards ({len(cards)})")
            return False
        
        health = {card.health for card in cards}
        if len(health) != 1:
            faction = {card.faction for card in cards}
            if len(faction) != 1:
                print("Las cartas deben de ser todas de la misma facción o todas del mismo número")
                return False

        if len(set(placements)) != 1: #len(set(placements)) == 1 implies all cards are played into the same column (allowed) 
            #Check the placements are consecutive: if they are the differences between a number and the next is always +- one (if the vector is sorted)
            differences_set = set()
            sorted_placements = sorted(placements)
            for i in range(len(placements) - 1): 
                differences_set.add(sorted_placements[i+1]-sorted_placements[i])
            if differences_set != {1}:
                print("Los placements no son ni adyacentes ni únicos")
                return False

        return True

    def play(self, cards: list[Card], placements: list, on_placement_parameters = None):
        logging.debug(Fore.MAGENTA + str(self.columns_opponent) + Fore.WHITE)
        if not self.play_placements_are_correct(cards, placements):
            raise Exception("Wrong play")

        if on_placement_parameters is None:
            on_placement_parameters = [None]*len(cards)
            
        for card, placement, parameter in zip(cards, placements, on_placement_parameters):
            card.position = len(self.columns[placement])
            card.column = placement
            self.columns[placement].append(card)
            card.on_placement(parameter)

    def discard_from_hand(self, cards):
        for card in cards:
            self.hand.remove(card)
            self.discard_pile.append(card)

    def play_and_discard(self, cards, placements):
        self.play(cards, placements)
        self.discard_from_hand(cards)

    def activate_placements_are_correct(self, discarded_card: Card, cards: list[Card]) -> bool: 

        #Check number of cards is valid
        if len(cards) > 3:
            print("Como mucho puedes activar tres cartas en un turno.")
            return False

        health = {card.health for card in cards}
        if health != {discarded_card.health}:
            faction = {card.faction for card in cards}
            if faction != {discarded_card.faction}:
                print("Las cartas deben de ser todas de la misma facción que la carta descartada o todas del mismo número que la carta descartada")
                return False
        return True

    def activate_and_discard(self, discarded_card: Card, cards: list[Card], cards_parameters : list[list | int | None] = [None, None, None]):
        if not self.activate_placements_are_correct(discarded_card, cards):
            raise Exception("Wrong activate")
        
        for card, parameters in zip(cards, cards_parameters):
            logging.info(Fore.GREEN + f"Activating {card} card with parameters {parameters}." + Fore.WHITE)
            card.activate(parameters)

        self.discard_from_hand([discarded_card])

    def activate(self, card: Card, card_parameters = None):
        logging.info(Fore.GREEN + f"Activating {card} card with parameters {card_parameters}." + Fore.WHITE)
        card.activate(card_parameters)

    def controled_factions(self) -> int:
        controled = 0
        for player_column, opponent_column in zip(self.columns, self.columns_opponent):
            if len(player_column) and not len(opponent_column):
                controled += 1
        return controled
