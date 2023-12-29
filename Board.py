from Card import Card

class Board():
    def __init__(self) -> None:
        self.columns1 = [[],[],[],[],[]]
        self.columns2 = [[],[],[],[],[]]

    def __str__(self) -> str:
        max_columns1 = max((len(column) for column in self.columns1))
        max_columns2 = max((len(column) for column in self.columns2))

        s = ""
        for height in reversed(range(max_columns2)):
            for column in self.columns2:
                if len(column) > height:
                    s += f" {column[height].health_left}{column[height].faction[:2]}{column[height].health} "
                else:
                    s += '      '
            s += '\n'
        
        s += ' ----  ----  ----  ----  ---- \n'
        for height in range(max_columns1):
            for column in self.columns1:
                if len(column) > height:
                    s += f" {column[height].health_left}{column[height].faction[:2]}{column[height].health} "
                else:
                    s += '      '
            s += '\n'


        return s


if __name__ == '__main__':
    board = Board()
    board.columns1 = [[], [], [Card.random(), Card.random()], [Card.random()], []]
    board.columns2 = [[Card.random(),], [Card.random(),], [Card.random(), Card.random(), Card.random()], [Card.random()], []]

    print(board.columns1)
    print(board.columns2)

    print(board)