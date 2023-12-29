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


    def play(self, cards, placements, columns):
        #Check cards are valid
        if len(cards) > 3:
            print("Demasiadas cartas")
            return

        health = {card.health for card in cards}
        if len(health) != 1:
            faction = {card.faction for card in cards}
            if len(faction) != 1:
                print("Selección inválida!")
                return 
            
        #Check placements are valid
        if len(placements) != len(cards):
            print("Distinto número de placements y cards")
            return

        if len(set(placements)) != 1:
            differences_set = set()
            sorted_placements = sorted(placements)
            for i in range(len(placements) - 1):
                differences_set.add(sorted_placements[i+1]-sorted_placements[i])
            print(differences_set)
            if differences_set != {1}:
                print("Los placements no son ni adyacentes ni únicos")
            

            

        for card, placement in zip(cards, placements):
            columns[placement].append(card)







if __name__ == '__main__':
    player = Player(('Agua', 'Fuego', 'Aire', 'Planta'))
    player.draw()
    # print(len(player.deck.list))
    player.sort_hand()
    # print(player.hand)
    player.play(player.hand)

