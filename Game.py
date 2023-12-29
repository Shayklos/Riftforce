from Player import Player
from Board import Board


class Game():
    def __init__(self) -> None:
        self.player1 = Player({'Agua', 'Fuego'}) 
        self.player2 = Player({'Luz', 'Tierra'}) 

        self.board = Board()
        self.turn = True #True -> player1, False -> player2


if __name__ == '__main__':
    game = Game()
    game.player1.draw()
    game.player1.sort_hand()
    print(game.player1.hand[:3])
    game.player1.play(game.player1.hand[:3], (3,1,2), game.board.columns1)
    print(game.board)


