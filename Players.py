import random
import math
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ColorProperty

# Player Parent Class


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
        # returning the selected cell by the human player
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
        # selecting random move from the available moves
        cells = self.grid.get_moves(self)
        return random.choice(cells)


class GreedyPlayer(Player):
    def __init__(self, id, **kwargs):
        super().__init__(id, **kwargs)

    def getMove(self):
        # selecting the maximum cell from the available moves
        cells = self.grid.get_moves(self)
        maxValue = 0
        maxCell = None
        for cell in cells:
            if maxValue < cell.get_value():
                maxValue = cell.get_value()
                maxCell = cell
        return maxCell


class AIPlayer(Player):
    def __init__(self, id, depth=5, alphabeta=False, **kwargs):
        super().__init__(id, **kwargs)
        self.depth = depth
        self.alphabeta = alphabeta

    def getMove(self):
        # function the returns the cell of the selected best move by the AI player

        # converting the grid to game state (occupied 1,occupied 2,position 1,position 2)
        state = self.getGameState(self.grid)
        # returning the move for the current player's turn whether maximizer or minimizer
        return self.findMaximizerBestMove(state, self.depth) if self.isMaximizerTurn(state) else self.findMinimizerBestMove(state, self.depth)

    def findMaximizerBestMove(self, state, depth):
        # function that checks the evaluation all possible moves in a position using minimax algorithm and returns the best move for maximizer
        (occupied1, occupied2, position1, position2) = state
        sz = self.grid.get_size()
        # getting all valid moves
        moves = self.getValidMoves(state, position1)
        maxValue = -math.inf
        maxMove = 0
        # looping through all moves
        for move in moves:
            # creating new state with the current move applied to it
            nxtState = (occupied1 | move, occupied2, move, position2)

            # calling the minimax algorithm on the new state
            moveValue = self.miniMax(nxtState, depth, -math.inf, math.inf)
            # maximizing the value of the best move
            if maxValue < moveValue:
                maxValue = moveValue
                maxMove = move
        # converting the move to cell in a grid
        if maxMove != 0:
            # finding the bit of the move
            moveBit = math.log2(maxMove)
            # finding (x,y) coordinate of the move
            x = int(moveBit/sz)
            y = int(moveBit % sz)
            return self.grid.cells[x][y]
        else:
            return None

    def findMinimizerBestMove(self, state, depth):
        # function that checks the evaluation all possible moves in a position using minimax algorithm and returns the best move for minimizer
        (occupied1, occupied2, position1, position2) = state
        sz = self.grid.get_size()

        # looping through all moves
        moves = self.getValidMoves(state, position2)
        minValue = math.inf
        minMove = 0
        for move in moves:
            # creating new state with the current move applied to it
            nxtState = (occupied1, occupied2 | move, position1, move)

            # calling the minimax algorithm on the new state
            moveValue = self.miniMax(nxtState, depth, -math.inf, math.inf)

            # maximizing the value of the best move
            if minValue > moveValue:
                minValue = moveValue
                minMove = move
        # converting the move to cell in a grid
        if minMove != 0:
            # finding the bit of the move
            moveBit = math.log2(minMove)
            # finding (x,y) coordinate of the move
            x = int(moveBit/sz)
            y = int(moveBit % sz)
            return self.grid.cells[x][y]
        else:
            return None

    def miniMax(self, state, depth, alpha, beta):
        # function that explores the game state tree and maximizing the moves for the maximizer and minimizing the move for the minimizer
        # returns the final evaluation of the terminal state
        (occupied1, occupied2, position1, position2) = state

        # if we consumed the depth or reached a terminal state we return the evaluation of the state
        if depth <= 0 or self.hasMove(state) == False:
            return self.evaluate(state)

        # if it is the maximizer's tunr we find the maximum move
        if self.isMaximizerTurn(state):
            moves = self.getValidMoves(state, position1)
            best = -math.inf
            # looping through all possible moves
            for move in moves:
                # getting the evaluation after applying the current move
                eval = self.miniMax(
                    (occupied1 | move, occupied2, move, position2), depth-1, alpha, beta)

                # maximizing the best evaluation
                best = max(best, eval)

                # if alpha beta pruning we prune the rest of the moves if we already found a better one
                if self.alphabeta == True:
                    # maximizing the alpha
                    alpha = max(alpha, eval)
                    # if beta less equal than alpha we break and discontinue searching the rest of the moves
                    if beta <= alpha:
                        break
            return best
        # else if it is the minimizer's turn we find the minimum move
        else:
            moves = self.getValidMoves(state, position2)
            best = math.inf
            # looping through all possible moves
            for move in moves:
                # getting the evaluation after applying the current move
                eval = self.miniMax(
                    (occupied1, occupied2 | move, position1, move), depth-1, alpha, beta)

                # minimizing the best evaluation
                best = min(best, eval)

                # if alpha beta pruning we prune the rest of the moves if we already found a better one
                if self.alphabeta == True:
                    # minimizing the beta
                    beta = min(beta, eval)
                    # if beta less equal than alpha we break and discontinue searching the rest of the moves
                    if beta <= alpha:
                        break
            return best

    def hasMove(self, state):
        # function to check if there is a move available from current state of game
        (occupied1, occupied2, position1, position2) = state
        position = 0
        if self.isMaximizerTurn(state):
            position = position1
        else:
            position = position2
        moves = self.getValidMoves(state, position)
        return len(moves) > 0

    def getValidMoves(self, state, position):
        # function to get all available moves from given position on given game state
        sz = self.grid.get_size()
        # for first move only
        moves = []

        # if player is not on the grid all moves are available
        if position == 0:
            for i in range(sz*sz):
                moves.append(1 << i)
        else:
            # getting all horizontal and vertical moves from position
            moves = [(position >> 1), (position << 1),
                     (position >> sz), (position << sz)]

        # returning all the valid moves from the possible moves
        return [move for move in moves if self.validMove(move, state, position)]

    def validMove(self, move, state, position):
        # Function checking if the given move is valid from given position on given game state
        (occupied1, occupied2, position1, position2) = state
        sz = self.grid.get_size()

        # checking if the move is on the same column or row as position
        if move != 0 and position != 0:
            moveX = int(int(math.log2(move)) / sz)
            moveY = int(int(math.log2(move)) % sz)
            positionX = int(int(math.log2(position)) / sz)
            positionY = int(int(math.log2(position)) % sz)
            if moveX != positionX and moveY != positionY:
                return False

        # checking if the move inside the bounds of grid and is not on an occupied cell
        return move > 0 and move < (1 << (sz*sz)) and int(move).bit_count() == 1 and (occupied1 & move) == 0 and (occupied2 & move) == 0

    def isMaximizerTurn(self, state):
        # function that takes state of game and returns which players turn it is
        (occupied1, occupied2, position1, position2) = state
        # if the number of occupied cells by both player is the same
        # then it is player 1 turn (return true)
        # otherwise, it is player 2 turn (return false)
        bits1 = int(occupied1).bit_count()
        bits2 = int(occupied2).bit_count()
        return bits1 == bits2

    def evaluate(self, state):
        # function that takes state of game and returns the difference between the scores of player 1 and player 2
        sz = self.grid.get_size()
        cells = self.grid.get_cells()
        (occupied1, occupied2, position1, position2) = state
        value1 = 0
        value2 = 0
        # calculating the score of player 1
        for i in range(sz*sz):
            if ((occupied1 >> i) & 1):
                x = int(i / sz)
                y = int(i % sz)
                value1 += cells[x][y].get_value()

        # calculating the score of player 2
        for i in range(sz*sz):
            if ((occupied2 >> i) & 1):
                x = int(i / sz)
                y = int(i % sz)
                value2 += cells[x][y].get_value()

        return value1-value2

    def getGameState(self, grid):
        # Function that takes the grid and converts it into state tuple
        # state tuple is 4 decimal numbers representing:
        #   cells occupied by player 1
        #   cells occupied by player 2
        #   current cell of player 1 (power of 2 coordinate)
        #   current cell of player 2 (power of 2 coordinate)

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
        # getting the coordinates of current player
        (p1x, p1y) = self.get_position()
        # getting the coordinates of other player
        (p2x, p2y) = self.other_player.get_position()

        # calculating the power of 2 cell coordinate of current and other player
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
