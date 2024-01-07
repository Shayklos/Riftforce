from Player import Player
from Board import Board
from Card import Card, FACTIONS
import logging 
logging.basicConfig(level=logging.INFO, format = "%(levelname)s:%(message)s")
from random import randint, sample

class Game():
    def __init__(self, player1: Player, player2: Player) -> None:
        self.player1: Player = player1
        self.player2: Player = player2
        self.turn_number = 1

        self.link_players()

        self.board = Board(self.player1, self.player2)
        
        self.isPlayer1Turn = True
        self.board.place_card(self.player2.deck.list.pop(), 2) #Player 2 gets free elemental placed in the middle column
        
        self.player1.draw()
        self.player2.draw()
        self.player1.sort_hand()
        self.player2.sort_hand()



    def __str__(self) -> str:
        return f"[{self.turn_number}][Player 1] {self.player1.score[0]} - {self.player2.score[0]} [Player 2]\n{self.board}"

    def link_players(self):
        self.player1.columns = self.player2.columns_opponent
        self.player1.columns_opponent = self.player2.columns
        self.player1.score = self.player2.opponents_score
        self.player1.opponents_score = self.player2.score

    def change_turn(self, debug = False):
        if not debug:
            self.isPlayer1Turn = not self.isPlayer1Turn
        if self.isPlayer1Turn:
            self.turn_number += 1

    def isFinished(self):
        if not self.isPlayer1Turn: return False
        if self.player1.score[0] < 12 and self.player2.score[0] < 12 : return False
        if self.player1.score[0] == self.player2.score[0]: return False
        return True


class GameTest(Game):
    def __init__(self) -> None:
        super().__init__(Player(('Crystal','Love','Magnet','Water')), Player({'Acid', 'Beast', 'Sound', 'Earth'}))

        self.board.place_card(Card(6, 'Love', self.player1), 0)
        self.board.place_card(Card(5, 'Crystal', self.player1), 1)
        self.board.place_card(Card(6, 'Water', self.player1), 1)
        self.board.place_card(Card(5, 'Magnet', self.player1), 2)
        self.board.place_card(Card(6, 'Water', self.player1), 2)
        self.board.place_card(Card(5, 'Crystal', self.player1), 3)

        self.board.place_card(Card(7, 'Acid', self.player2), 0)
        self.board.place_card(Card(5, 'Beast', self.player2), 1)
        self.board.place_card(Card(7, 'Earth', self.player2), 1)

        self.board.place_card(Card(5, 'Beast', self.player2), 2)
        self.board.place_card(Card(5, 'Sound', self.player2), 2)
        self.board.place_card(Card(7, 'Beast', self.player2), 3)


        # for column in self.board.columns1:
        #     for card in column:
        #         card.health_left = randint(1,card.health-1)
        # for column in self.board.columns2:
        #     for card in column:
        #         card.health_left = randint(1,card.health-1)    

        

class Draft():
    def __init__(self, n_factions=8) -> None:
        self.factions = sample(FACTIONS, n_factions+2)
        self.player1_factions = [self.factions.pop(randint(0, len(self.factions) -1))]
        self.player2_factions = [self.factions.pop(randint(0, len(self.factions) -1))]
        self.isPlayer1Turn = True

    def __str__(self) -> str:
        return f"""Factions : {self.factions}\nPlayer 1: {self.player1_factions}\nPlayer 2: {self.player2_factions}"""

    def pick(self, faction):
        i = self.factions.index(faction)
        factions = self.player1_factions if self.isPlayer1Turn else self.player2_factions
        factions.append(self.factions.pop(i))
        self.isPlayer1Turn = not self.isPlayer1Turn

