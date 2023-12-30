from Card import Card
from colorama import Fore

class Board():
    def __init__(self) -> None:
        self.columns1 = [[],[],[],[],[]]
        self.columns2 = [[],[],[],[],[]]

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

    def place_card(self, card: Card, column, opponent = False):
        columns = self.columns2 if opponent else self.columns1

        columns[column].append(card)
        card.column = column
        card.position = len(columns[column]) - 1


    def refresh(self): pass

class BoardTest(Board):
    def __init__(self) -> None:
        super().__init__()
        self.place_card(Card(7, 'Luz'), 1)
        self.place_card(Card(7, 'Fuego'), 1)
        self.place_card(Card(6, 'Fuego'), 2)
        self.place_card(Card(7, 'Agua'), 2)
        self.place_card(Card(5, 'Fuego'), 3)

        self.place_card(Card(5, 'Luz'), 1, opponent = True)
        self.place_card(Card(6, 'Tierra'), 2, opponent = True)
        self.place_card(Card(5,  'Planta'), 2, opponent = True)
        self.place_card(Card(7, 'Tierra'), 3, opponent = True)

if __name__ == '__main__':
    board = BoardTest()
    # board.columns1 = [[], [], [Card.random(), Card.random()], [Card.random()], []]
    # board.columns2 = [[Card.random(),], [Card.random(),], [Card.random(), Card.random(), Card.random()], [Card.random()], []]

    # print(board.columns1)
    # print(board.columns2)

    print(board)
    # print(board.columns1[2][0])
    card: Card = board.columns1[2][0] 
    card.activate(board.columns1, board.columns2)
    card.activate(board.columns1, board.columns2)
    card2: Card = board.columns1[1][0]
    card2.activate(board.columns1, board.columns2, (2, 1))
    card3: Card = board.columns1[2][1]
    print(board)
    card3.activate(board.columns1, board.columns2, 3)
    print(card3.position, card3.column)
    print(board)