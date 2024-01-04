from __future__ import annotations
from Card import Card
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Player import Player
from colorama import Fore

class Board():
    def __init__(self, player: Player, opponent: Player) -> None:
        self.columns1 = player.columns
        self.columns2 = opponent.columns
        self.player = player
        self.opponent = opponent

    def __str__(self) -> str:
        max_columns1 = max((len(column) for column in self.columns1))
        max_columns2 = max((len(column) for column in self.columns2))

        s = Fore.WHITE
        for height in reversed(range(max_columns2)):
            for column in self.columns2:
                if len(column) > height:
                    s += f" {column[height]} "
                else:
                    s += '      '
            s += '\n'
        
        s += ' ----  ----  ----  ----  ---- \n'
        for height in range(max_columns1):
            for column in self.columns1:
                if len(column) > height:
                    s += f" {column[height]} "
                else:
                    s += '      '
            s += '\n'
        return s

    def place_card(self, card: Card, column):
        card.owner.play([card], [column])