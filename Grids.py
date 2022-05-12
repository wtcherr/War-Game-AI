from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty
from Cells import SquareCell, cellState


class SquareGrid(GridLayout):
    gridSize = NumericProperty(0)

    def __init__(self, sz, **kwargs):
        super().__init__(**kwargs)
        self.gridSize = sz
        self.create_cells()

    def create_cells(self):
        self.cells = [[SquareCell(i, j, self.gridSize) for j in range(
            self.gridSize)] for i in range(self.gridSize)]
        for i in range(self.gridSize):
            for j in range(self.gridSize):
                self.add_widget(self.cells[i][j])

    def handle_selected_cell(self, cell):
        self.parent.handle_selected_cell(cell)

    def get_moves(self, player):
        moves = []
        i = player.i
        j = player.j
        if i == -1 and j == -1:
            for x in self.cells:
                for y in x:
                    if y.state != cellState.occupied:
                        moves.append(y)
            return moves
        dx = [1, 0, 0, -1]
        dy = [0, 1, -1, 0]
        for k in range(len(dx)):
            idx = dx[k]+i
            idy = dy[k]+j
            if self.valid_cell(idx, idy) and self.cells[idx][idy].state != cellState.occupied:
                moves.append(self.cells[idx][idy])
        return moves

    def show_available_moves(self, player):
        i = player.i
        j = player.j
        if i == -1 and j == -1:
            for i in self.cells:
                for j in i:
                    if j.state != cellState.occupied:
                        j.state = cellState.available
            return
        dx = [1, 0, 0, -1]
        dy = [0, 1, -1, 0]
        for k in range(len(dx)):
            idx = dx[k]+i
            idy = dy[k]+j
            if self.valid_cell(idx, idy) and self.cells[idx][idy].state == cellState.unavailable:
                self.cells[idx][idy].state = cellState.available

    def dim_all_unoccupied(self):
        for i in self.cells:
            for j in i:
                if j.state != cellState.occupied:
                    j.state = cellState.unavailable

    def valid_cell(self, i, j):
        return i >= 0 and i < self.gridSize and j >= 0 and j < self.gridSize

    def occupy(self, cell, player):
        cell.occupy(player)

    def get_cells(self):
        return self.cells

    def get_size(self):
        return self.gridSize
