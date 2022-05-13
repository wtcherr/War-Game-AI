from cgitb import text
from enum import auto
import random
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from Cells import SquareCell, cellColors, cellState
from Grids import SquareGrid
from kivy.clock import Clock
from Players import AIPlayer, HumanPlayer, GreedyPlayer, RandomPlayer
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

# Game class


class Game(BoxLayout):
    currentPlayer = ObjectProperty()
    fps = NumericProperty(0)

    def __init__(self, **kw):
        super().__init__(**kw)
        # creating the grid of certain size
        self.grid = SquareGrid(5)
        # creating the players
        self.create_players(2)
        # adding the created grid to the game layout
        self.add_widget(self.grid)
        # binding update of color depending on current player
        self.bind(currentPlayer=self.update_player_color)
        # assigning the current and other player
        self.currentPlayer = self.players[0]
        self.otherPlayer = self.players[1]
        # initializing turn and autoplay buttons
        self.turn = False
        self.autoplay = False
        # creating the evaluator for the game
        self.create_evaluator()
        # adding UI for the game
        self.create_user_interface()
        self.bind(fps=self.update_fps)

    def update(self, dt):
        # update function is called every frame (Game Main Loop)

        # getting the current frames per seconds
        self.fps = Clock.get_rfps()

        # getting the evaluators evaluation and best move suggestion
        self.evaluation, self.bestMove = self.evaluator.get_evaluation(
        ), self.evaluator.get_best_move()

        if self.is_finished() == False:
            # displaying the available moves for current player
            self.grid.show_available_moves(self.currentPlayer)

            # checking if autoplay is enabled
            if self.autoplay == True:
                self.turn = True

            # checking if we can play the current turn
            if self.turn == True:
                self.play()

    def handle_selected_cell(self, cell):
        self.currentPlayer.set_selected_cell(cell)

    def create_players(self, numberOfPlayers):
        # function to create the players and add them to the UI
        self.players = []
        #self.players.append(AIPlayer(1, depth=13, alphabeta=True))
        self.players.append(AIPlayer(1, depth=10, alphabeta=True))
        self.players.append(AIPlayer(2, depth=10))

        # creating layout for the scores
        scoreLayout = BoxLayout(size_hint=(0.3, 1), orientation='vertical')

        # adding the player scores on the layout
        for player in self.players:
            scoreLayout.add_widget(player)

        # adding the score layout to game layout
        self.add_widget(scoreLayout)

    def is_finished(self):
        return self.has_move() == False

    def play(self):
        # function that performs the current player move

        # giving the current player the grid
        self.currentPlayer.set_grid(self.grid)

        # giving the current player the other player
        self.currentPlayer.set_other_player(self.otherPlayer)

        # asking the current player for a move
        cell = self.currentPlayer.getMove()

        # if we have a move
        if cell != None:
            # asking the game to submit the current players move
            self.submit_current_move(cell)
            self.grid.dim_all_unoccupied()
            # calling for next players turn
            self.next_player()

    def has_move(self):
        # function to check if the current player has any moves available
        moves = self.grid.get_moves(self.currentPlayer)
        return len(moves) != 0

    def next_player(self):
        # switching turn
        tempPlayer = self.currentPlayer
        self.currentPlayer = self.otherPlayer
        self.otherPlayer = tempPlayer

        # giving the evaluator the new state of the game
        self.evaluator.set_game(self)
        self.turn = False

    def next_turn(self, a):
        self.turn = True

    def auto_play(self, a):
        # toggling the autoplay state
        self.autoplay ^= 1

    def submit_current_move(self, cell):
        # applying the current move on the grid by telling the grid to occupy the selected cell by the current player
        self.grid.occupy(cell, self.currentPlayer)
        self.turn = True

    def update_player_color(self, a, b):
        cellColors.color[cellState.occupied] = self.currentPlayer.color

    def create_user_interface(self):
        # making the UI Layout
        UILayout = BoxLayout(size_hint=(0.2, 1), orientation='vertical')

        # adding autoplay and next turn buttons
        nextTurnBtn = Button(text="Next Turn", on_press=self.next_turn)
        autoPlayBtn = ToggleButton(text="Auto Play", on_press=self.auto_play)
        playBtnsLayout = BoxLayout(size_hint=(1, 0.2))
        playBtnsLayout.add_widget(nextTurnBtn)
        playBtnsLayout.add_widget(autoPlayBtn)
        UILayout.add_widget(playBtnsLayout)

        # adding fps counter label
        self.fpsLabel = Label(text="FPS: "+str(self.fps), size_hint=(1, 0.2))
        UILayout.add_widget(self.fpsLabel)

        # adding the evaluator UI
        UILayout.add_widget(self.evaluator)

        # adding the UI Layout to Game Layout
        self.add_widget(UILayout)

    def update_fps(self, a, b):
        # update the frames per second label
        self.fpsLabel.text = "FPS: "+str(int(self.fps))

    def create_evaluator(self):
        # creates the game evaluator
        self.evaluator = MaxEvaluator(alphabeta=True)

        # giving the evaluator the initial state of the game
        self.evaluator.set_game(self)


sm = ScreenManager()


class WarGameApp(App):
    # building the application
    def build(self):
        # creating different screens
        game = GameScreen(name='game')
        gameover = GameOverScreen(name='game over')
        # adding the screens to the screen manager
        sm.add_widget(game)
        sm.add_widget(gameover)
        return sm


if __name__ == '__main__':
    WarGameApp().run()
