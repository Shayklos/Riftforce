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
        return f"[Player 1] {self.player1.score[0]} - {self.player2.score[0]} [Player 2]\n{self.board}"

    def link_players(self):
        self.player1.columns = self.player2.columns_opponent
        self.player1.columns_opponent = self.player2.columns
        self.player1.score = self.player2.opponents_score
        self.player1.opponents_score = self.player2.score