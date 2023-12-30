from Deck import Deck
from Card import Card
from time import perf_counter
from Board import Board

FACTIONS = {'Agua', 'Fuego', 'Luz', 'Planta', 'Aire'}

class Player():
    def __init__(self, factions) -> None:
        self.deck = Deck(factions, self)
        self.discard_pile = []
        self.hand = []
        self.columns = [[], [], [], [], []]
        self.columns_opponent = [[], [], [], [], []]
        self.score = 0


    def generateBoard(self):
        self.board = Board(self.columns, self.columns_opponent)
    

    def draw(self):
        while len(self.hand) < 7:
            self.hand.append(self.deck.list.pop(0))
        

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


    def _play(self, cards: list[Card], placements: list):
        if not self.play_placements_are_correct(cards, placements):
            raise Exception("Wrong play")

        for card, placement in zip(cards, placements):
            card.position = len(self.columns[placement])
            card.column = placement
            self.columns[placement].append(card)
            card.on_placement()

    def discard_from_hand(self, cards):
        for card in cards:
            self.hand.remove(card)
            self.discard_pile.append(card)


    def play_and_discard(self, cards, placements):
        self._play(cards, placements)
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

    def _activate(self, discarded_card: Card, placements: list[list], activateparams):
        cards: list[Card] = []
        for column, placement in placements:
            cards.append(self.columns[column][placement])

        if not self.activate_placements_are_correct(discarded_card, cards):
            raise Exception("Wrong activate")
        
        for card, parameters in zip(cards, activateparams):
            card.activate(parameters, self.columns, self.columns_opponent)

        self.discard_from_hand(discarded_card)
        
        




if __name__ == '__main__':
    player = Player(('Agua', 'Fuego', 'Aire', 'Planta'))
    player.draw()
    # print(len(player.deck.list))
    player.sort_hand()
    print(player.hand)
    print(player.hand[:3])
    player.play_and_discard(player.hand[:3], (1,2,3), [[],[],[],[],[]])
    print(player.hand)
