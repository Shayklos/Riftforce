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

        self.link_players()

        self.board = Board(self.player1, self.player2)
        self.isPlayer1Turn = True #True -> player1, False -> player2
        self.board.place_card(self.player2.deck.list.pop(), 2) #Player 2 gets free elemental placed in the middle column
        self.player1.draw()
        self.player2.draw()

    def __str__(self) -> str:
        return f"[Player 1] {self.player1.score[0]} - {self.player2.score[0]} [Player 2]\n{self.board}"

    def link_players(self):
        self.player1.columns = self.player2.columns_opponent
        self.player1.columns_opponent = self.player2.columns
        self.player1.score = self.player2.opponents_score
        self.player1.opponents_score = self.player2.score

class GameTest(Game):
    def __init__(self) -> None:
        super().__init__(Player(('Tierra','Tierra')), Player({'Cristal', 'Planta', 'Hielo', 'Sombra'}))

        self.board.place_card(Card(7, 'Luz', self.player1), 1)
        self.board.place_card(Card(7, 'Fuego', self.player1), 1)
        self.board.place_card(Card(6, 'Fuego', self.player1), 2)
        self.board.place_card(Card(7, 'Agua', self.player1), 2)
        self.board.place_card(Card(5, 'Fuego', self.player1), 3)

        self.board.place_card(Card(5, 'Luz', self.player2), 1)
        self.board.place_card(Card(7, 'Cristal', self.player2), 2)
        self.board.place_card(Card(5,  'Planta', self.player2), 2)
        self.board.place_card(Card(7, 'Tierra', self.player2), 3)
        self.board.place_card(Card(5, 'Luz', self.player2), 0)
        self.board.place_card(Card(7, 'Tierra', self.player2), 2)
        self.board.place_card(Card(5,  'Planta', self.player2), 4)
        self.board.place_card(Card(5, 'Tierra', self.player2), 3)

        for column in self.board.columns1:
            for card in column:
                card.health_left = randint(1,card.health-1)
        for column in self.board.columns2:
            for card in column:
                card.health_left = randint(1,card.health-1)    
        

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

if __name__ == '__main__':
    game = Game(Player(('Luz', 'Fuego')), Player(('Agua', 'Tierra')))
    # print(str(game))
    # print(game.player2.controled_factions())
    
    # draft = Draft()
    # print(draft)

