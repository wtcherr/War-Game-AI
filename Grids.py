from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty
from Cells import SquareCell, cellState


class SquareGrid(GridLayout):
    gridSize = NumericProperty(0)

    def __init__(self, sz, **kwargs):
        super().__init__(**kwargs)
        self.gridSize = sz
        # creating grid cells
        self.create_cells()

    def create_cells(self):
        # creating the cells matrix
        self.cells = [[SquareCell(i, j, self.gridSize) for j in range(
            self.gridSize)] for i in range(self.gridSize)]

        # adding the cells to the grid layout
        for i in range(self.gridSize):
            for j in range(self.gridSize):
                self.add_widget(self.cells[i][j])

    def handle_selected_cell(self, cell):
        self.parent.handle_selected_cell(cell)

    def get_moves(self, player):
        # function to get all available moves for a player
        moves = []
        i = player.i
        j = player.j

        # if the player is not on the grid all cells are available if not occupied by other player
        if i == -1 and j == -1:
            for x in self.cells:
                for y in x:
                    if y.state != cellState.occupied:
                        moves.append(y)
            return moves

        # looping on the horizontal and vertical neighboring cells of the player
        dx = [1, 0, 0, -1]
        dy = [0, 1, -1, 0]
        for k in range(len(dx)):
            idx = dx[k]+i
            idy = dy[k]+j
            # if it is not occupied by any player we add it to the available moves
            if self.valid_cell(idx, idy) and self.cells[idx][idy].state != cellState.occupied:
                moves.append(self.cells[idx][idy])
        return moves

    def show_available_moves(self, player):

        # function to show all available moves for a player
        i = player.i
        j = player.j

        # if the player is not on the grid all cells are available if not occupied by other player
        if i == -1 and j == -1:
            for i in self.cells:
                for j in i:
                    if j.state != cellState.occupied:
                        j.state = cellState.available
            return

        # looping on the horizontal and vertical neighboring cells of the player
        dx = [1, 0, 0, -1]
        dy = [0, 1, -1, 0]
        for k in range(len(dx)):
            idx = dx[k]+i
            idy = dy[k]+j
            # if it is not occupied by any player we add it to the available moves
            if self.valid_cell(idx, idy) and self.cells[idx][idy].state == cellState.unavailable:
                self.cells[idx][idy].state = cellState.available

    def dim_all_unoccupied(self):
        # resitting all unoccupied cells as unavailable
        for i in self.cells:
            for j in i:
                if j.state != cellState.occupied:
                    j.state = cellState.unavailable

    def valid_cell(self, i, j):
        # checking if a cell coordinate is inside the bounds of the grid
        return i >= 0 and i < self.gridSize and j >= 0 and j < self.gridSize

    def occupy(self, cell, player):
        cell.occupy(player)

    def get_cells(self):
        return self.cells

    def get_size(self):
        return self.gridSize
