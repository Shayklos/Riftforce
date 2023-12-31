from Player import Player
from Board import Board
from Card import Card
import logging 
logging.basicConfig(level=logging.INFO, format = "%(levelname)s:%(message)s")

class Game():
    def __init__(self, player1: Player, player2: Player) -> None:
        self.player1: Player = player1
        self.player2: Player = player2

        self.link_players()
        
        self.board = Board(self.player1, self.player2)
        self.isPlayer1Turn = True #True -> player1, False -> player2

    def __str__(self) -> str:
        return f"[Player 1] {self.player1.score} - {self.player2.score} [Player 2]\n{self.board}"

    def link_players(self):
        self.player1.columns = self.player2.columns_opponent
        self.player1.columns_opponent = self.player2.columns
        self.player1.score = self.player2.opponents_score


if __name__ == '__main__':
    # player1 = Player({'Agua', 'Fuego', 'Luz', 'Tierra'})
    player1 = Player(('Tierra','Tierra'))
    player2 = Player({'Cristal', 'Planta', 'Hielo', 'Sombra'})
    game = Game(player1, player2)
    board = game.board
    # board.place_card(Card(7, 'Luz', player1), 1)
    # board.place_card(Card(7, 'Fuego', player1), 1)
    # board.place_card(Card(6, 'Fuego', player1), 2)
    # board.place_card(Card(7, 'Agua', player1), 2)
    # board.place_card(Card(5, 'Fuego', player1), 3)

    # board.place_card(Card(5, 'Luz', player2), 1)
    board.place_card(Card(6, 'Tierra', player2), 2)
    # board.place_card(Card(5,  'Planta', player2), 2)
    # board.place_card(Card(7, 'Tierra', player2), 3)
    # board.place_card(Card(5, 'Luz', player2), 0)
    # board.place_card(Card(7, 'Tierra', player2), 2)
    # board.place_card(Card(5,  'Planta', player2), 4)
    # board.place_card(Card(5, 'Tierra', player2), 3)

    # print(board)
    # card: Card = board.columns1[2][0] 
    # card.activate()
    # card.activate()
    # card2: Card = board.columns1[1][0]
    # card2.activate((2, 1))
    # card3: Card = board.columns1[2][1]
    # card3.activate(3)
    # print(card3.position, card3.column)
    # print(board)
    # game.player1.draw()
    # game.player1.sort_hand()
    # print("hand", game.player1.hand)
    # game.player1._play(game.player1.hand[:3], (1,2,3))
    # card_earth = Card(5, 'Tierra', player1)
    enemy_card = Card(7, 'Fuego', player2)
    card_plant = Card(6, 'Planta', player1)
    # board.place_card(card_earth, 3)
    board.place_card(enemy_card, 3)
    board.place_card(card_plant, 2)
    card_plant.activate(3)
    enemy_card.activate()
    print(game)



