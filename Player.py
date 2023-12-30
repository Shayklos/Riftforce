from Deck import Deck
from time import perf_counter

FACTIONS = {'Agua', 'Fuego', 'Luz', 'Planta', 'Aire'}

class Player():
    def __init__(self, factions) -> None:
        self.deck = Deck(factions)

        self.discard_pile = []
        self.hand = []


    def draw(self):
        while len(self.hand) < 7:
            self.hand.append(self.deck.list.pop(0))
        

    def sort_hand(self):
        self.hand.sort(key = lambda card : (card.health, card.faction))


    def play_placements_are_correct(self, cards, placements):
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

    def _play(self, cards, placements, columns):
        if not self.play_placements_are_correct(cards, placements):
            raise Exception("Wrong play")

        for card, placement in zip(cards, placements):
            columns[placement].append(card)


    def discard_from_hand(self, cards):
        for card in cards:
            self.hand.remove(card)
            self.discard_pile.append(card)


    def play_and_discard(self, cards, placements, columns):
        self._play(cards, placements, columns)
        self.discard_from_hand(cards)




if __name__ == '__main__':
    player = Player(('Agua', 'Fuego', 'Aire', 'Planta'))
    player.draw()
    # print(len(player.deck.list))
    player.sort_hand()
    print(player.hand)
    print(player.hand[:3])
    player.play_and_discard(player.hand[:3], (1,2,3), [[],[],[],[],[]])
    print(player.hand)

