import random
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ColorProperty, ObjectProperty, NumericProperty
import enum


class cellState(enum.Enum):
    unavailable = 1
    occupied = 2
    available = 3


class cellColors():
    color = {cellState.unavailable: (random.random(), random.random(), random.random(), 0.2),
             cellState.occupied: (random.random(), random.random(), random.random(), 1),
             cellState.available: (0.9, 0.8, 0.8, 0.5)}


class SquareCell(BoxLayout):
    value = NumericProperty(0)
    color = ColorProperty()
    state = ObjectProperty()
    i = NumericProperty()
    j = NumericProperty()
    gridSize = NumericProperty()

    def __init__(self, i, j, gsz, ** kwargs):
        super().__init__(**kwargs)
        self.i = i
        self.j = j
        self.gridSize = gsz
        self.value = random.randint(1, 99)
        self.color = random.random(), random.random(), random.random(), 1
        self.bind(state=self.update_color)
        self.state = cellState.unavailable
        self.owner = None

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            if self.state == cellState.available:
                self.parent.handle_selected_cell(self)
            return True
        else:
            return super(SquareCell, self).on_touch_down(touch)

    def update_color(self, a, b):
        self.color = cellColors.color[self.state]

    def occupy(self, player):
        self.owner = player
        self.state = cellState.occupied
        player.occupy(self)

    def isOccupied(self):
        return self.state == cellState.occupied

    def get_value(self):
        return self.value

    def get_owner(self):
        return self.owner
