import random
import math
from turtle import pos
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ColorProperty


class Player(Widget):
    score = NumericProperty(0)
    color = ColorProperty()

    def __init__(self, id, **kwargs):
        super().__init__(**kwargs)
        self.selected_cell = None
        self.id = id
        self.i = -1
        self.j = -1
        self.color = random.random(), random.random(), random.random(), 1
        self.score = 0

    def getMove(self):
        pass

    def set_selected_cell(self, cell):
        pass

    def occupy(self, cell):
        self.score += cell.get_value()
        self.i, self.j = cell.i, cell.j

    def set_grid(self, grid):
        self.grid = grid

    def set_other_player(self, player):
        self.other_player = player

    def get_position(self):
        return self.i, self.j


class HumanPlayer(Player):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)

    def getMove(self):
        if self.selected_cell != None:
            cell = self.selected_cell
            self.set_selected_cell(None)
            return cell
        return None

    def set_selected_cell(self, cell):
        self.selected_cell = cell


class RandomPlayer(Player):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)

    def getMove(self):
        cells = self.grid.get_moves(self)
        return random.choice(cells)


class MaxPlayer(Player):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)

    def getMove(self):
        cells = self.grid.get_moves(self)
        maxValue = 0
        maxCell = None
        for cell in cells:
            if maxValue < cell.get_value():
                maxValue = cell.get_value()
                maxCell = cell
        return maxCell


class AIPlayer(Player):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)

    def getMove(self):
        state = self.getGameState(self.grid)
        return self.findMaximizerBestMove(state) if self.isMaximizerTurn(state) else self.findMinimizerBestMove(state)

    def findMaximizerBestMove(self, state):
        (occupied1, occupied2, position1, position2) = state
        sz = self.grid.get_size()
        moves = self.getValidMoves(state, position1)
        maxValue = -3000
        maxMove = 0
        for move in moves:
            nxtState = (occupied1 | move, occupied2, move, position2)
            moveValue = self.miniMax(nxtState)
            if maxValue < moveValue:
                maxValue = moveValue
                maxMove = move
        if maxMove != 0:
            moveBit = math.log2(maxMove)
            x = int(moveBit/sz)
            y = int(moveBit % sz)
            return self.grid.cells[x][y]
        else:
            return None

    def findMinimizerBestMove(self, state):
        (occupied1, occupied2, position1, position2) = state
        sz = self.grid.get_size()
        moves = self.getValidMoves(state, position2)
        minValue = 3000
        minMove = 0
        for move in moves:
            nxtState = (occupied1, occupied2 | move, position1, move)
            moveValue = self.miniMax(nxtState)
            if minValue > moveValue:
                minValue = moveValue
                minMove = move
        if minMove != 0:
            moveBit = math.log2(minMove)
            x = int(moveBit/sz)
            y = int(moveBit % sz)
            return self.grid.cells[x][y]
        else:
            return None

    def miniMax(self, state):
        (occupied1, occupied2, position1, position2) = state
        if self.hasMove(state) == False:
            return self.evaluate(state)
        if self.isMaximizerTurn(state):
            moves = self.getValidMoves(state, position1)
            best = -3000
            for move in moves:
                best = max(best, self.miniMax(
                    (occupied1 | move, occupied2, move, position2)))
            return best
        else:
            moves = self.getValidMoves(state, position2)
            best = 3000
            for move in moves:
                best = min(best, self.miniMax(
                    (occupied1, occupied2 | move, position1, move)))
            return best

    def hasMove(self, state):
        (occupied1, occupied2, position1, position2) = state
        position = 0
        if self.isMaximizerTurn(state):
            position = position1
        else:
            position = position2
        moves = self.getValidMoves(state, position)
        return len(moves) > 0

    def getValidMoves(self, state, position):
        sz = self.grid.get_size()
        # for first move only
        moves = []
        if position == 0:
            for i in range(sz*sz):
                moves.append(1 << i)
        else:
            moves = [(position >> 1), (position << 1),
                     (position >> sz), (position << sz)]
        return [move for move in moves if self.validMove(move, state, position)]

    def validMove(self, move, state, position):
        (occupied1, occupied2, position1, position2) = state
        sz = self.grid.get_size()
        if move != 0 and position != 0:
            moveX = int(int(math.log2(move)) / sz)
            moveY = int(int(math.log2(move)) % sz)
            positionX = int(int(math.log2(position)) / sz)
            positionY = int(int(math.log2(position)) % sz)
            if moveX != positionX and moveY != positionY:
                return False
        return move > 0 and move < (1 << (sz*sz)) and int(move).bit_count() == 1 and (occupied1 & move) == 0 and (occupied2 & move) == 0

    def isMaximizerTurn(self, state):
        (occupied1, occupied2, position1, position2) = state
        bits1 = int(occupied1).bit_count()
        bits2 = int(occupied2).bit_count()
        return bits1 == bits2

    def evaluate(self, state):
        sz = self.grid.get_size()
        cells = self.grid.get_cells()
        (occupied1, occupied2, position1, position2) = state
        value1 = 0
        value2 = 0
        for i in range(sz*sz):
            if ((occupied1 >> i) & 1):
                x = int(i / sz)
                y = int(i % sz)
                value1 += cells[x][y].get_value()
        for i in range(sz*sz):
            if ((occupied2 >> i) & 1):
                x = int(i / sz)
                y = int(i % sz)
                value2 += cells[x][y].get_value()
        return value1-value2

    def getGameState(self, grid):
        cells = grid.get_cells()
        sz = grid.get_size()
        occupied1 = 0  # occupied by player 1
        occupied2 = 0  # occupied by player 2
        position1 = 0
        position2 = 0
        for i in range(len(cells)):
            for j in range(len(cells[i])):
                if cells[i][j].get_owner() == self:
                    if self.id == 1:
                        occupied1 |= (1 << (i*sz+j))  # 2^(i*sz+j)
                    elif self.id == 2:
                        occupied2 |= (1 << (i*sz+j))
                elif cells[i][j].get_owner() == self.other_player:
                    if self.other_player.id == 1:
                        occupied1 |= (1 << (i*sz+j))  # 2^(i*sz+j)
                    elif self.other_player.id == 2:
                        occupied2 |= (1 << (i*sz+j))
        (p1x, p1y) = self.get_position()
        (p2x, p2y) = self.other_player.get_position()
        if p1x != -1 and p1y != -1:
            if self.id == 1:
                position1 = (1 << (p1x*sz+p1y))
            elif self.id == 2:
                position2 = (1 << (p1x*sz+p1y))
        if p2x != -1 and p2y != -1:
            if self.other_player.id == 1:
                position1 = (1 << (p2x*sz+p2y))
            elif self.other_player.id == 2:
                position2 = (1 << (p2x*sz+p2y))

        return occupied1, occupied2, position1, position2
