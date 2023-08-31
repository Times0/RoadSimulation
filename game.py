from typing import Optional

import pygame
from PygameUIKit import Group, button
from pygame import Color
from pygame.locals import *

from config import *
from objects import GraphUi, create_default_graph, Node, Vehicle

image_pause = pygame.image.load("assets/GUI/Stop.png")
image_play = pygame.image.load("assets/GUI/Start.png")

image_reset = pygame.image.load("assets/GUI/Restart.png")


class Game:
    def __init__(self, win):
        self._is_paused = None
        self.game_is_on = True
        self.win = win

        self.graph = create_default_graph()
        self.graph_ui = GraphUi(self.graph)

        self.selected_node: Optional[Node] = None
        self.vehicles: list[Vehicle] = []

        self.ui = Group()
        self.btn_reset = button.ButtonPngIcon(image_reset, self.reset, inflate=15, ui_group=self.ui)
        self.btn_pause = button.ButtonTwoStates(image_pause, image_play, self.pause, inflate=15, ui_group=self.ui)

    def run(self):
        clock = pygame.time.Clock()
        while self.game_is_on:
            dt = clock.tick(FPS) / 1000
            self.events()
            self.update(dt)
            self.draw(self.win)

    def events(self):
        for event in pygame.event.get():
            self.ui.handle_event(event)
            if event.type == pygame.QUIT:
                self.game_is_on = False
            elif event.type == MOUSEBUTTONDOWN and event.button == 1 and not self._is_paused:
                if self.graph_ui.get_node_at(event.pos) is None:
                    self.selected_node = None

                if self.selected_node is None:
                    node = self.graph_ui.get_node_at(event.pos)
                    if node is not None:
                        self.selected_node = node
                elif self.selected_node != self.graph_ui.get_node_at(event.pos):
                    vehicle = Vehicle(self.graph, self.selected_node.name, self.graph_ui.get_node_at(event.pos).name)
                    self.vehicles.append(vehicle)

    def update(self, dt):
        if not self._is_paused:
            for vehicle in self.vehicles:
                vehicle.update(dt)
                if vehicle.is_finished():
                    self.vehicles.remove(vehicle)
            self.graph_ui.update(dt)

    def draw(self, win):
        if not self._is_paused:
            self.draw_game(win)
        self.draw_ui(win)
        pygame.display.flip()

    def draw_game(self, win):
        self.win.fill(Color(224, 224, 224))
        self.graph_ui.draw(win)

        for vehicle in self.vehicles:
            vehicle.draw_path(win)
        for vehicle in self.vehicles:
            vehicle.draw(win)

        # draw selected node
        if self.selected_node is not None:
            pygame.draw.circle(win, Color("red"), (self.selected_node.x, self.selected_node.y),
                               self.selected_node.size + 5, 2)

    def draw_ui(self, win):
        self.btn_reset.draw(win, 10, 10)
        self.btn_pause.draw(win, 60, 10)

    def reset(self):
        self.vehicles.clear()

    def pause(self):
        self._is_paused = not self._is_paused
