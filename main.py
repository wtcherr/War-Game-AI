from cgitb import text
from enum import auto
import random
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from Cells import SquareCell, cellColors, cellState
from Grids import SquareGrid
from kivy.clock import Clock
from Players import AIPlayer, HumanPlayer, MaxPlayer, RandomPlayer
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from Evaluators import MaxEvaluator


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
    fps = NumericProperty(0)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.grid = SquareGrid(5)
        self.create_players(2)
        self.add_widget(self.grid)
        self.bind(currentPlayer=self.update_player_color)
        # self.currentPlayer = random.choice(self.players)
        self.currentPlayer = self.players[0]
        self.otherPlayer = self.players[1]
        self.turn = False
        self.autoplay = False
        self.create_evaluator()
        self.create_user_interface()
        self.bind(fps=self.update_fps)

    def update(self, dt):
        self.fps = Clock.get_rfps()
        self.evaluation, self.bestMove = self.evaluator.get_evaluation(
        ), self.evaluator.get_best_move()
        if self.is_finished() == False:
            self.grid.show_available_moves(self.currentPlayer)
            if self.autoplay == True:
                self.turn = True
            if self.turn == True:
                self.play()

    def handle_selected_cell(self, cell):
        self.currentPlayer.set_selected_cell(cell)

    def create_players(self, numberOfPlayers):
        self.players = []
        self.players.append(HumanPlayer(1))
        self.players.append(AIPlayer(2, depth=13, alphabeta=True))
        scoreLayout = BoxLayout(size_hint=(0.3, 1), orientation='vertical')
        for player in self.players:
            scoreLayout.add_widget(player)
        self.add_widget(scoreLayout)

    def is_finished(self):
        return self.has_move() == False

    def play(self):
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
        self.evaluator.set_game(self)
        self.turn = False

    def next_turn(self, a):
        self.turn = True

    def auto_play(self, a):
        self.autoplay ^= 1

    def submit_current_move(self, cell):
        self.grid.occupy(cell, self.currentPlayer)
        self.turn = True

    def update_player_color(self, a, b):
        cellColors.color[cellState.occupied] = self.currentPlayer.color

    def create_user_interface(self):
        UILayout = BoxLayout(size_hint=(0.3, 1), orientation='vertical')
        nextTurnBtn = Button(text="Next Turn", on_press=self.next_turn)
        autoPlayBtn = ToggleButton(text="Auto Play", on_press=self.auto_play)
        playBtnsLayout = BoxLayout(size_hint=(1, 0.2))
        playBtnsLayout.add_widget(nextTurnBtn)
        playBtnsLayout.add_widget(autoPlayBtn)
        UILayout.add_widget(playBtnsLayout)
        self.fpsLabel = Label(text="FPS: "+str(self.fps), size_hint=(1, 0.2))
        UILayout.add_widget(self.evaluator)
        UILayout.add_widget(self.fpsLabel)
        self.add_widget(UILayout)

    def update_fps(self, a, b):
        self.fpsLabel.text = "FPS: "+str(int(self.fps))

    def update_best_move(self, a, b):
        self.bestMoveLabel.text = "Best Move: "+str(self.bestMove)

    def update_evaluation(self, a, b):
        self.evaluationLabel.text = "Evaluation: "+str(self.evaluation)

    def create_evaluator(self):
        self.evaluator = MaxEvaluator(alphabeta=True)
        self.evaluator.set_game(self)


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
