import random

import pygame
from pygame import Color

pygame.font.init()
font = pygame.font.SysFont("Arial", 30)

VEHICLE_SIZE = 50
VEHICLE_SPEED = 200  # pixels per second

available_vehicles = ["car", "bus", "truck"]  # files names in assets/


def create_default_graph():
    graph_roads = WeightedGraph()

    node_coordinates = [
        ("A", 100, 100),
        ("B", 400, 150),
        ("C", 350, 500),
        ("D", 100, 500),
        ("E", 700, 300),
        ("F", 500, 100),
        ("G", 200, 200),
        ("H", 900, 300),
        ("I", 800, 200),
        ("J", 900, 400)
    ]

    # Add nodes to the graph
    for name, x, y in node_coordinates:
        graph_roads.add_node(Node(name, x, y))

    graph_roads.get_node("A").add_signal()
    graph_roads.get_node("C").add_signal()
    graph_roads.get_node("E").add_signal()
    graph_roads.get_node("G").add_signal()

    # Add edges to the graph
    graph_roads.add_edge("A", "B")
    graph_roads.add_edge("A", "G")
    graph_roads.add_edge("A", "D")
    graph_roads.add_edge("B", "C")
    graph_roads.add_edge("B", "F")
    graph_roads.add_edge("C", "E")
    graph_roads.add_edge("C", "J")
    graph_roads.add_edge("D", "G")
    graph_roads.add_edge("E", "H")
    graph_roads.add_edge("E", "I")
    graph_roads.add_edge("F", "G")
    graph_roads.add_edge("F", "J")
    graph_roads.add_edge("G", "H")
    graph_roads.add_edge("H", "I")
    graph_roads.add_edge("I", "J")

    return graph_roads


class Node:
    def __init__(self, name, x, y):
        self.size = 30
        self.name = name
        self.x = x
        self.y = y

        self.signal = None

    def add_signal(self):
        self.signal = Signal()

    def distance(self, other: "Node"):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def update(self, dt):
        if self.signal is not None:
            self.signal.update(dt)

    def draw(self, win):
        pygame.draw.circle(win, Color("darkblue"), (self.x, self.y), self.size)
        text = font.render(self.name, True, Color("white"))
        win.blit(text, text.get_rect(center=(self.x, self.y)))

        if self.signal is not None:
            img = self.signal.get_image()
            win.blit(img, img.get_rect(center=(self.x - self.size, self.y)))

    def __str__(self):
        return f"'{self.name}' at ({self.x}, {self.y})"

    def __repr__(self):
        return str(self)

    def is_way_free(self):
        if self.signal is None:
            return True
        return self.signal.state == Signal.GREEN


def get_distance(pos1, pos2):
    return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5


def draw_transparent_rect_with_border_radius(screen, rect, border_radius, color, alpha):
    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(surf, color, surf.get_rect().inflate(-1, -1), border_radius=border_radius)
    surf.set_alpha(alpha)
    screen.blit(surf, rect)


class File:
    def __init__(self):
        self.list = []

    def add(self, vehicle):
        self.list.append(vehicle)

    def remove(self):
        self.list.pop(0)  # Pop the first element of the list

    def nb_car_in_front(self, vehicle):
        return self.list.index(vehicle)

    def len(self):
        return len(self.list)


class WeightedGraph:
    def __init__(self):
        self.graph: dict[Node, list[Node]] = {}
        self.weights: dict[tuple[Node, Node], float] = {}

        self.edges_occupancy: dict[tuple[Node, Node], File] = {}

    def add_node(self, node: Node):
        self.graph[node] = []

    def add_edge(self, name1: str, name2: str):
        node1, node2 = self.get_node(name1), self.get_node(name2)
        self.graph[node1].append(node2)
        self.graph[node2].append(node1)
        self.weights[(node1, node2)] = node1.distance(node2)
        self.weights[(node2, node1)] = node1.distance(node2)

        self.edges_occupancy[(node1, node2)] = File()
        self.edges_occupancy[(node2, node1)] = File()

    def get_node(self, name: str):
        for node in self.graph:
            if node.name == name:
                return node
        raise ValueError(f"Node '{name}' not found in graph")

    def get_neighbors(self, node: Node):
        return self.graph[node]

    def get_weight(self, node1: Node, node2: Node):
        return self.weights[(node1, node2)]

    def shortest_path(self, start: str, end: str) -> tuple[list[Node], float]:
        """
        Returns the shortest path between start and end node and the total distance
        """

        start, end = self.get_node(start), self.get_node(end)

        distances = {node: float("inf") for node in self.graph}
        previous_nodes = {node: None for node in self.graph}
        distances[start] = 0

        nodes = self.graph.copy()

        while nodes:
            current_node = min(nodes, key=lambda node: distances[node])
            nodes.pop(current_node)

            for neighbor in self.get_neighbors(current_node):
                new_distance = distances[current_node] + self.get_weight(current_node, neighbor)

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous_nodes[neighbor] = current_node

        path = []
        current_node = end

        while current_node is not None:
            path.append(current_node)
            current_node = previous_nodes[current_node]

        path = path[::-1]
        return path, distances[end]

    def add_vehicle_on(self, edge: tuple[Node, Node], vehicle):
        self.edges_occupancy[edge].add(vehicle)
        self.edges_occupancy[edge[1], edge[0]].add(1)

    def free_vehicle_on(self, edge: tuple[Node, Node]):
        self.edges_occupancy[edge].remove()
        self.edges_occupancy[edge[1], edge[0]].remove()

    def clear(self):
        for edge in self.edges_occupancy:
            self.edges_occupancy[edge] = File()


class GraphUi:
    def __init__(self, graph: WeightedGraph):
        self.graph: WeightedGraph = graph

    def update(self, dt):
        for node in self.graph.graph:
            node.update(dt)

    def draw(self, win):
        """Draw the graph on the screen"""
        for node1 in self.graph.graph:
            for node2 in self.graph.graph[node1]:
                pygame.draw.line(win, Color("black"), (node1.x, node1.y), (node2.x, node2.y), 5)
        for node in self.graph.graph:
            node.draw(win)

    def get_node_at(self, pos):
        """Return the node at the given position"""
        for node in self.graph.graph:
            if get_distance((node.x, node.y), pos) <= node.size:
                return node
        return None


def resize_image(image, size=None, vertical=None, horizontal=None):
    if size is not None:
        return pygame.transform.scale(image, (size, size))
    elif vertical is not None:
        ratio = vertical / image.get_height()
        return pygame.transform.scale(image, (int(image.get_width() * ratio), vertical))
    elif horizontal is not None:
        ratio = horizontal / image.get_width()
        return pygame.transform.scale(image, (horizontal, int(image.get_height() * ratio)))
    else:
        raise ValueError("You must specify at least one argument")


class Vehicle:
    colors = ["red", "blue", "green", "yellow", "purple", "orange", "pink", "brown", "black"]
    color_index = 0

    def __init__(self, graph: WeightedGraph, start: str, end: str):
        self.image = pygame.image.load(f"assets/{random.choice(available_vehicles)}.png")
        self.image = resize_image(self.image, vertical=VEHICLE_SIZE)

        self.graph = graph
        self.start = start
        self.end = end

        self.path, cost = self.graph.shortest_path(self.start, self.end)
        self.path_index = 0

        self.pos = pygame.Vector2(self.path[self.path_index].x, self.path[self.path_index].y)

        self.speed = VEHICLE_SPEED
        self.direction = pygame.Vector2(0, 0)

        self.color = Color(Vehicle.colors[Vehicle.color_index])
        Vehicle.color_index = (Vehicle.color_index + 1) % len(Vehicle.colors)

        self.distance = 0
        self.total_distance = cost

        self.current_edge = (self.path[self.path_index], self.path[self.path_index + 1])
        self.graph.add_vehicle_on(self.current_edge, self)

    def compute_direction(self):
        self.direction = pygame.Vector2(self.path[self.path_index + 1].x - self.pos.x,
                                        self.path[self.path_index + 1].y - self.pos.y).normalize()

    def update(self, dt):
        """
        Update the vehicle position
        :param dt: Time delta, amount of time passed since the last update (usually in seconds)
        :return:
        """

        if not self.direction:
            self.compute_direction()

        next_node = self.path[self.path_index + 1]
        distance_to_next_node = self.pos.distance_to(pygame.Vector2(next_node.x, next_node.y))

        if distance_to_next_node < self.speed * dt:  # Arrived at the next node
            if not next_node.is_way_free():  # Wait for green signal
                return
            self.path_index += 1
            self.graph.free_vehicle_on(self.current_edge)
            if self.path_index == len(self.path) - 1:
                return
            self.current_edge = (self.path[self.path_index], self.path[self.path_index + 1])
            self.graph.add_vehicle_on(self.current_edge, self)
            self.compute_direction()
        else:  # Not arrived at the next node yet
            distance_to_next_node = self.pos.distance_to(pygame.Vector2(next_node.x, next_node.y))
            if distance_to_next_node < self.graph.edges_occupancy[self.current_edge].nb_car_in_front(self) * 50:
                return
            self.pos += self.direction * self.speed * dt
            self.distance += self.speed * dt

    def draw(self, win, show_distance=True):
        # Rotate the image
        angle = self.direction.angle_to(pygame.Vector2(0, -1))
        rotated_image = pygame.transform.rotate(self.image, angle)
        win.blit(rotated_image, rotated_image.get_rect(center=(self.pos.x, self.pos.y)))

        if show_distance:
            text = font.render(f"{self.distance:.0f} →  {self.total_distance:.0f}", True, Color("white"))
            draw_transparent_rect_with_border_radius(win,
                                                     text.get_rect(midbottom=(self.pos.x, self.pos.y)).inflate(10, 10),
                                                     border_radius=10, color=self.color, alpha=100)

            win.blit(text, text.get_rect(midbottom=(self.pos.x, self.pos.y)))

    def draw_path(self, win):
        if not self.path:
            return
        for i in range(len(self.path) - 1):
            pygame.draw.line(win, self.color, (self.path[i].x, self.path[i].y),
                             (self.path[i + 1].x, self.path[i + 1].y), 5)

    def is_finished(self):
        return self.path_index == len(self.path) - 1


img_signal_green = pygame.image.load("assets/Signals/green.png")
img_signal_yellow = pygame.image.load("assets/Signals/yellow.png")
img_signal_red = pygame.image.load("assets/Signals/red.png")

img_signal_green = resize_image(img_signal_green, vertical=50)
img_signal_yellow = resize_image(img_signal_yellow, vertical=50)
img_signal_red = resize_image(img_signal_red, vertical=50)


class Signal:
    GREEN = 0
    YELLOW = 1
    RED = 2
    TIME_GREEN = 5
    TIME_YELLOW = 2
    TIME_RED = 5

    def __init__(self):
        self.state = random.choice([Signal.GREEN, Signal.YELLOW, Signal.RED])
        self.timer = random.random() * 5
        self.images = {
            Signal.GREEN: img_signal_green,
            Signal.YELLOW: img_signal_yellow,
            Signal.RED: img_signal_red
        }

    def update(self, dt):
        self.timer += dt
        if self.state == Signal.GREEN and self.timer >= Signal.TIME_GREEN:
            self.state = Signal.YELLOW
            self.timer = 0
        elif self.state == Signal.YELLOW and self.timer >= Signal.TIME_YELLOW:
            self.state = Signal.RED
            self.timer = 0
        elif self.state == Signal.RED and self.timer >= Signal.TIME_RED:
            self.state = Signal.GREEN
            self.timer = 0

    def get_image(self):
        return self.images[self.state]
