from cgitb import text
import random
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from Cells import SquareCell, cellColors, cellState
from Grids import SquareGrid
from kivy.clock import Clock
from Players import AIPlayer, HumanPlayer, MaxPlayer, RandomPlayer
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label


class GameOverScreen(Screen):
    pass


class GameScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        game = Game()
        Clock.schedule_interval(game.update, 1.0/60.0)
        self.add_widget(game)


class Game(BoxLayout):
    currentPlayer = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.grid = SquareGrid(4)
        self.add_widget(self.grid)
        self.create_players(2)
        self.bind(currentPlayer=self.update_player_color)
        #self.currentPlayer = random.choice(self.players)
        self.currentPlayer = self.players[0]
        self.otherPlayer = self.players[1]

    def update(self, dt):
        if self.is_finished() == False:
            self.play()

    def handle_selected_cell(self, cell):
        self.currentPlayer.set_selected_cell(cell)

    def create_players(self, numberOfPlayers):
        self.players = []
        self.players.append(AIPlayer(1))
        self.players.append(AIPlayer(2))
        scoreLayout = BoxLayout(size_hint=(0.3, 1), orientation='vertical')
        for player in self.players:
            scoreLayout.add_widget(player)
        self.add_widget(scoreLayout)

    def is_finished(self):
        return self.has_move() == False

    def play(self):
        self.grid.show_available_moves(self.currentPlayer)
        self.currentPlayer.set_grid(self.grid)
        self.currentPlayer.set_other_player(self.otherPlayer)
        cell = self.currentPlayer.getMove()
        if cell != None:
            self.submit_current_move(cell)
            self.grid.dim_all_unoccupied()
            self.next_player()

    def has_move(self):
        moves = self.grid.get_moves(self.currentPlayer)
        return len(moves) != 0

    def next_player(self):
        tempPlayer = self.currentPlayer
        self.currentPlayer = self.otherPlayer
        self.otherPlayer = tempPlayer

    def submit_current_move(self, cell):
        self.grid.occupy(cell, self.currentPlayer)

    def update_player_color(self, a, b):
        cellColors.color[cellState.occupied] = self.currentPlayer.color


sm = ScreenManager()


class WarGameApp(App):
    def build(self):
        game = GameScreen(name='game')
        gameover = GameOverScreen(name='game over')
        sm.add_widget(game)
        sm.add_widget(gameover)
        return sm


if __name__ == '__main__':
    WarGameApp().run()
