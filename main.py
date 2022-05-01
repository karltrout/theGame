# the Game
import math
import random
from enum import Enum
from typing import List, Dict

import kivy
from kivy import Logger
from kivy.app import App
from kivy.graphics import Color, Rectangle, Ellipse, Line, Rotate, PushMatrix, PopMatrix
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget

from Graph import Graph

kivy.require('2.1.0')


class FixType(Enum):
    GATE = (18, Color(1, 0, 0, 1))
    GROUND_FIX = (18, Color(0, 0, 1, 1))
    RUNWAY = (30, Color(0, 1, 0, 1))

    def __init__(self, size, color):
        self.size = size
        self.color = color


class Fix(Widget):
    fix_type: FixType = None
    id = None
    moves: Dict = {"left": None,
                   "right": None,
                   "forward": None,
                   "no_opt": None}

    def __init__(self, pos: List, fix_type: FixType, **kwargs):
        super().__init__(**kwargs)
        self.id = id(self)
        self.fix_type = fix_type
        self.size = (self.fix_type.size, self.fix_type.size)
        self.pos = pos
        self.color = self.fix_type.color
        for key in self.moves.keys():
            self.moves[key] = self
        self.bind(pos=self._update)

    def _update(self, *_):
        self.center = (self.pos[0] + (self.fix_type.size / 2), self.pos[1] + (self.fix_type.size / 2))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            Logger.info(f"You touched Fix {self}! at {touch.pos}")


class Aircraft(Image):
    location_fix: Fix = None
    id = None

    def __init__(self, location_fix: Fix, size, angle, **kwargs):
        super().__init__(**kwargs)
        self.id = id(self)
        self.source = 'graphics/airplaneIcon.png'
        self.keep_ratio = True
        self.size = (10 * size, 10 * size)  # the -10 inverts the image so that it faces downward
        self.angle = angle
        self.update_location(location_fix)

    def update(self):
        self.center = self.location_fix.center

    def update_location(self, new_location_fix: Fix):
        self.location_fix = new_location_fix
        self.update()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            Logger.info(f"You touched {self.id}! at {touch.pos}")
            return True


class Board(Widget):
    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)
        self.bind(pos=self._paint, size=self._paint)
        self.gate_positions: List[Fix] = [Fix(pos=[0, 0], fix_type=FixType.GATE) for _ in range(6)]
        self.fix_l1_positions: List[Fix] = [Fix(pos=[0, 0], fix_type=FixType.GROUND_FIX) for _ in range(5)]
        self.fix_l2_positions: List[Fix] = [Fix(pos=[0, 0], fix_type=FixType.GROUND_FIX) for _ in range(2)]
        self.fix_l3_positions: List[Fix] = [Fix(pos=[0, 0], fix_type=FixType.GROUND_FIX) for _ in range(2)]
        self.fix_l4_positions: List[Fix] = [Fix(pos=[0, 0], fix_type=FixType.RUNWAY) for _ in range(1)]
        self.fix_l5_positions: List[Fix] = [Fix(pos=[0, 0], fix_type=FixType.RUNWAY) for _ in range(1)]
        self.active_aircraft: List[Aircraft] = []
        self.graph = self._create_graph()

    def _create_graph(self) -> Graph:
        graph = Graph()
        for i, fix in enumerate(self.fix_l1_positions):
            gate = self.gate_positions[i]
            gate.moves["right"] = fix
            graph.add_edge((gate, fix))
            gate_1 = self.gate_positions[i + 1]
            gate.moves["left"] = fix
            graph.add_edge((gate_1, fix))

        # connect L1 nodes to l2 nodes
        for i in range(5):  # there is a more pythonic way to do this
            for fix_l1 in self.fix_l1_positions[i * 2:(i * 3) + 3]:
                for fix_l2 in self.fix_l2_positions[i:i + 1]:
                    graph.add_edge((fix_l1, fix_l2))

        # connect L2 fixes
        graph.add_edge((self.fix_l2_positions[0], self.fix_l2_positions[1]))

        # connect l2 nodes to L3 nodes
        for i in range(2):
            graph.add_edge(((self.fix_l2_positions[i]), (self.fix_l3_positions[i])))

        # connect L3 nodes
        graph.add_edge(((self.fix_l3_positions[0]), (self.fix_l3_positions[1])))

        # connect l3 nodes to L4 nodes
        for fix_l3 in self.fix_l3_positions:
            for fix_l4 in self.fix_l4_positions:
                graph.add_edge((fix_l3, fix_l4))

        # connect l4 nodes to l5 nodes
        for fix_l4 in self.fix_l4_positions:
            for fix_l5 in self.fix_l5_positions:
                graph.add_edge((fix_l4, fix_l5))

        Logger.info(f'number of vertices in matrix {graph.n}')
        Logger.info(f'number of edges in matrix {graph.m}')
        return graph

    def start_game(self):
        start_pos = random.choice(self.gate_positions)
        new_aircraft = Aircraft(location_fix=start_pos, size=5, angle=180)
        self.active_aircraft.append(new_aircraft)
        self.add_widget(new_aircraft)

    def _paint(self, *_):
        self._clear()
        top_spacing = 50
        start_height = self.height - top_spacing
        height_spacing = self.height / 6
        boarder_width = 5
        # boarder space is the spacing around the fixes
        boarder_space = self.width - (2 * boarder_width)
        # Add some things
        with self.canvas:
            Color(0.2, 0.2, 0.2, .5)
            # board area has a reduction of 5 pixel border
            Rectangle(pos=(self.x + boarder_width, self.y + boarder_width),
                      size=(self.width - (2 * boarder_width), self.height - (2 * boarder_width)))

            # gates start 60 px inside boarder of 5
            gate_separation = math.floor((boarder_space - 60) / 5)
            for idx, gate in enumerate(self.gate_positions):
                gate.pos = ((idx * gate_separation) + 25, start_height - (0 * height_spacing))

            f1_separation = math.floor((boarder_space - gate_separation - top_spacing) / 4)
            for idx, gate in enumerate(self.fix_l1_positions):
                f1_position = ((idx * f1_separation) + 25 + (gate_separation / 2), start_height - (1 * height_spacing))
                gate.pos = f1_position

            f2_separation = math.floor((boarder_space - f1_separation - top_spacing) / 2)
            for idx, gate in enumerate(self.fix_l2_positions):
                gate.pos = ((idx * f2_separation) + f1_separation + 25 + (f1_separation / 2),
                            start_height - (2 * height_spacing))

            f3_separation = math.floor((boarder_space - f1_separation - top_spacing) / 2)
            for idx, gate in enumerate(self.fix_l3_positions):
                gate.pos = ((idx * f3_separation) + f1_separation + 25 + (f1_separation / 2),
                            start_height - (3 * height_spacing))

            for idx, gate in enumerate(self.fix_l4_positions):
                gate.pos = (math.floor(boarder_space / 2), start_height - (4 * height_spacing))

            for idx, gate in enumerate(self.fix_l5_positions):
                gate.pos = (math.floor(boarder_space / 2), start_height - (5 * height_spacing))

            # draw lines from l1 positions to gate positions
            Color(0, 0, 1, .5)
            for i, fix in enumerate(self.fix_l1_positions):
                gate = self.gate_positions[i]
                Line(points=gate.center + fix.center, width=2)
                gate_1 = self.gate_positions[i + 1]
                Line(points=gate_1.center + fix.center, width=2)

            # draw lines from L1 positions to l2 positions
            for i in range(5):
                for fix_l1 in self.fix_l1_positions[i * 2:(i * 3) + 3]:
                    for fix_l2 in self.fix_l2_positions[i:i + 1]:
                        Line(points=fix_l1.center + fix_l2.center, width=2)

            # connect L2 fixes
            Line(points=self.fix_l2_positions[0].center + self.fix_l2_positions[1].center, width=2)

            # draw lines from l2 positions to L3 positions
            for i in range(2):
                fix_l2 = self.fix_l2_positions[i]
                fix_l3 = self.fix_l3_positions[i]
                # draw line from this l3 position to the 2 l2 positions
                Line(points=fix_l2.center + fix_l3.center, width=2)

            # connect L3 fixes
            fix1_l3 = self.fix_l3_positions[0]
            fix2_l3 = self.fix_l3_positions[1]
            Line(points=fix1_l3.center + fix2_l3.center, width=2)

            # draw lines from l3 positions to L4 position
            for fix_l3 in self.fix_l3_positions:
                for fix_l4 in self.fix_l4_positions:
                    Line(points=fix_l3.center + fix_l4.center, width=2)

            # draw line(s) from l4 positions to l5 position
            for fix_l4 in self.fix_l4_positions:
                for fix_l5 in self.fix_l5_positions:
                    Line(points=fix_l4.center + fix_l5.center, width=2)

            Color(1, 0, 0, 1)
            for gate in self.gate_positions:
                Ellipse(pos=gate.pos, size=gate.size)
            for l1_fix in self.fix_l1_positions:
                Ellipse(pos=l1_fix.pos, size=l1_fix.size)
            for l2_fix in self.fix_l2_positions:
                Ellipse(pos=l2_fix.pos, size=l2_fix.size)
            for l3_fix in self.fix_l3_positions:
                Ellipse(pos=l3_fix.pos, size=l3_fix.size)

            Ellipse(pos=fix_l4.pos, size=fix_l4.size)
            Ellipse(pos=fix_l5.pos, size=fix_l5.size)

        # Redraw active aircraft
        for aircraft in self.active_aircraft:
            self.remove_widget(aircraft)
            aircraft.update()
            self.add_widget(aircraft)

    def _clear(self):
        self.canvas.clear()


class GameWindow(FloatLayout):
    def __init___(self, **kwargs):
        super(GameWindow, self).__init__(**kwargs)


class TheGame(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_button = Button(text="Start", size_hint=(.10, .05), pos=(20, 20))
        self.the_board = Board()
        self.rect = None

    def build(self):
        self.root = GameWindow()
        self.root.bind(size=self._paint, pos=self._paint)
        # background color of the app
        with self.root.canvas.before:
            Color(0.1, 0.1, 0.2, 1)
            self.rect = Rectangle(size=self.root.size, pos=self.root.pos)

        self.root.add_widget(self.the_board)
        self.start_button.bind(on_press=self.start_game)
        self.root.add_widget(self.start_button)
        return self.root

    def start_game(self, _):
        Logger.info(msg=f'The Game has Started!')
        self.the_board.start_game()

    def _paint(self, instance, _):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


if __name__ == '__main__':
    TheGame().run()
