from kivy.properties import NumericProperty, ColorProperty
from kivy.uix.boxlayout import BoxLayout
import math


class MaxEvaluator(BoxLayout):
    evaluation = NumericProperty(0)
    bestMove = NumericProperty(0)
    current_player_color = ColorProperty()
    other_player_color = ColorProperty()
    winpercentage = NumericProperty(0.9)

    def __init__(self, depth=13, alphabeta=False, **kwargs):
        super().__init__(**kwargs)
        self.memo = {}
        self.depth = depth
        self.alphabeta = alphabeta
        self.maxValue = 0
        self.maxMove = 0
        self.minValue = 0
        self.minMove = 0

    def get_evaluation(self):
        state = self.getGameState(self.grid)
        return self.maxValue if self.isMaximizerTurn(state) else self.minValue

    def get_best_move(self):
        state = self.getGameState(self.grid)
        sz = self.grid.get_size()
        if self.isMaximizerTurn(state):
            if self.maxMove > 0 and self.maxMove < (1 << sz*sz):
                maxMoveBit = math.log2(self.maxMove)
                maxMoveX, maxMoveY = int(maxMoveBit / sz), int(maxMoveBit % sz)
                return maxMoveX*sz+maxMoveY
            return self.maxMove
        else:
            if self.minMove > 0 and self.minMove < (1 << sz*sz):
                minMoveBit = math.log2(self.minMove)
                minMoveX, minMoveY = int(minMoveBit/sz), int(minMoveBit % sz)
                return minMoveX*sz+minMoveY
            return self.minMove

    def set_game(self, game):
        self.game = game
        self.grid = self.game.grid
        self.current_player = self.game.currentPlayer
        self.other_player = self.game.otherPlayer
        state = self.getGameState(self.grid)
        if self.isMaximizerTurn(state):
            self.current_player_color = self.current_player.color
            self.other_player_color = self.other_player.color
            self.findMaximizerBestMove(state, self.depth)
        else:
            self.current_player_color = self.other_player.color
            self.other_player_color = self.current_player.color
            self.findMinimizerBestMove(state, self.depth)
        self.evaluation = self.get_evaluation()
        self.bestMove = self.get_best_move()
        self.updateWinPercentage()

    def updateWinPercentage(self):
        sz = self.grid.get_size()
        factor = 25
        scale = sz*factor
        self.winpercentage = max(0, min(1, (self.evaluation+scale)/(2*scale)))

    def findMaximizerBestMove(self, state, depth):
        (occupied1, occupied2, position1, position2) = state
        sz = self.grid.get_size()
        moves = self.getValidMoves(state, position1)
        self.maxValue = -math.inf
        self.maxMove = 0
        for move in moves:
            nxtState = (occupied1 | move, occupied2, move, position2)
            moveValue = self.miniMax(nxtState, depth, -math.inf, math.inf)
            if self.maxValue < moveValue:
                self.maxValue = moveValue
                self.maxMove = move
        if self.maxMove != 0:
            moveBit = math.log2(self.maxMove)
            x = int(moveBit/sz)
            y = int(moveBit % sz)
            return self.grid.cells[x][y]
        else:
            return None

    def findMinimizerBestMove(self, state, depth):
        (occupied1, occupied2, position1, position2) = state
        sz = self.grid.get_size()
        moves = self.getValidMoves(state, position2)
        self.minValue = math.inf
        self.minMove = 0
        for move in moves:
            nxtState = (occupied1, occupied2 | move, position1, move)
            moveValue = self.miniMax(nxtState, depth, -math.inf, math.inf)
            if self.minValue > moveValue:
                self.minValue = moveValue
                self.minMove = move
        if self.minMove != 0:
            moveBit = math.log2(self.minMove)
            x = int(moveBit/sz)
            y = int(moveBit % sz)
            return self.grid.cells[x][y]
        else:
            return None

    def miniMax(self, state, depth, alpha, beta):
        (occupied1, occupied2, position1, position2) = state
        if depth <= 0 or self.hasMove(state) == False:
            return self.evaluate(state)
        if state in self.memo:
            return self.memo[state]
        if self.isMaximizerTurn(state):
            moves = self.getValidMoves(state, position1)
            best = -math.inf
            for move in moves:
                eval = self.miniMax(
                    (occupied1 | move, occupied2, move, position2), depth-1, alpha, beta)
                best = max(best, eval)
                if self.alphabeta == True:
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            self.memo[state] = best
            return best
        else:
            moves = self.getValidMoves(state, position2)
            best = math.inf
            for move in moves:
                eval = self.miniMax(
                    (occupied1, occupied2 | move, position1, move), depth-1, alpha, beta)
                best = min(best, eval)
                if self.alphabeta == True:
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            self.memo[state] = best
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
                if cells[i][j].get_owner() == self.current_player:
                    if self.current_player.id == 1:
                        occupied1 |= (1 << (i*sz+j))  # 2^(i*sz+j)
                    elif self.current_player.id == 2:
                        occupied2 |= (1 << (i*sz+j))
                elif cells[i][j].get_owner() == self.other_player:
                    if self.other_player.id == 1:
                        occupied1 |= (1 << (i*sz+j))  # 2^(i*sz+j)
                    elif self.other_player.id == 2:
                        occupied2 |= (1 << (i*sz+j))
        (p1x, p1y) = self.current_player.get_position()
        (p2x, p2y) = self.other_player.get_position()
        if p1x != -1 and p1y != -1:
            if self.current_player.id == 1:
                position1 = (1 << (p1x*sz+p1y))
            elif self.current_player.id == 2:
                position2 = (1 << (p1x*sz+p1y))
        if p2x != -1 and p2y != -1:
            if self.other_player.id == 1:
                position1 = (1 << (p2x*sz+p2y))
            elif self.other_player.id == 2:
                position2 = (1 << (p2x*sz+p2y))

        return occupied1, occupied2, position1, position2
