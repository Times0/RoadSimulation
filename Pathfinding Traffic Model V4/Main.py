import random

import pygame

import Common
import PathfindingAlgorithms as path
from GUI import Button, screenMove, zoom
from RoadFeatures import Node, Edge, TrafficLight
from VehicleClasses import Vehicle


def initialise():
    global c, a, y
    a = None  # Car
    y = False

    Common.Difference = [0, 0]
    Common.hold = False

    Common.nodes = []
    Common.edges = []
    Common.poles = []

    Common.nodes.append(Node((120, 180), "Roundabout", "0"))
    Common.nodes.append(Node((320, 290), "Intersection", "1"))
    Common.nodes.append(Node((350, 520), "Intersection", "2"))
    Common.nodes.append(Node((420, 410), "Roundabout", "3"))
    Common.nodes.append(Node((490, 310), "Intersection", "4"))
    Common.nodes.append(Node((520, 470), "Intersection", "5"))
    Common.nodes.append(Node((720, 140), "Intersection", "6"))
    Common.nodes.append(Node((800, 320), "Intersection", "7"))
    Common.nodes.append(Node((920, 270), "Intersection", "8"))

    Common.edges.append(Edge(Common.nodes[0], Common.nodes[1], 30))
    Common.edges.append(Edge(Common.nodes[1], Common.nodes[0], 30))
    Common.edges.append(Edge(Common.nodes[1], Common.nodes[4], 40))
    Common.edges.append(Edge(Common.nodes[4], Common.nodes[1], 40))
    Common.edges.append(Edge(Common.nodes[4], Common.nodes[3], 40))
    Common.edges.append(Edge(Common.nodes[3], Common.nodes[4], 40))
    Common.edges.append(Edge(Common.nodes[3], Common.nodes[2], 40))
    Common.edges.append(Edge(Common.nodes[3], Common.nodes[5], 40))
    Common.edges.append(Edge(Common.nodes[5], Common.nodes[3], 40))
    Common.edges.append(Edge(Common.nodes[4], Common.nodes[6], 40))
    Common.edges.append(Edge(Common.nodes[6], Common.nodes[4], 40))
    Common.edges.append(Edge(Common.nodes[5], Common.nodes[7], 40))
    Common.edges.append(Edge(Common.nodes[7], Common.nodes[5], 40))
    Common.edges.append(Edge(Common.nodes[7], Common.nodes[8], 40))
    Common.edges.append(Edge(Common.nodes[8], Common.nodes[7], 40))
    Common.edges.append(Edge(Common.nodes[2], Common.nodes[0], 40))  # Not real road

    Common.vehicles = [[] for _ in range(len(Common.edges))]
    Common.lights = [[] for _ in range(len(Common.nodes))]

    global button1, button2
    button1 = Button(Common.screen.get_size()[0] / 2 - 35, 11, ["Start", "Stop"])
    button2 = Button(Common.screen.get_size()[0] / 2 + 35, 11, ["Restart", "Restart"])

    Common.graph = path.makeGraph()

    light = TrafficLight((100, 100), Common.edges[0], 4)


def checkEdge(road):
    for edge in Common.edges:
        if road.start == edge.start and road.end == road.end:
            return True
    return False


def draw():
    Common.screen.fill((255, 255, 255))
    drawRoads()
    drawVehicles()

    sub = Common.screen.subsurface(480 - (480 / Common.Scale), 360 - (360 / Common.Scale), 960 / Common.Scale,
                                   720 / Common.Scale)
    pygame.image.save(sub, "temp.jpg")
    temp = pygame.image.load("temp.jpg")
    temp = pygame.transform.scale(temp, (960, 720))

    Common.screen.blit(temp, (0, 0))

    pygame.draw.rect(Common.screen, (185, 200, 204), (0, 0, Common.screen.get_size()[0], 50))
    pygame.draw.line(Common.screen, (0, 0, 0), (0, 50), (Common.screen.get_size()[0], 50), 2)
    button1.draw()
    button2.draw()

    pygame.display.flip()


def drawVehicles():
    for car in Common.sim:
        car.draw()
        car.followRoute()


def drawRoads():
    for node in Common.nodes:
        node.draw()
    for road in Common.edges:
        road.draw()
        road.weight = len(Common.vehicles[Common.edges.index(road)]) * 50
    for sys in Common.lights:
        for light in sys:
            light.draw()


def update():
    for road in Common.vehicles:
        for car in road:
            car.update()
            car.detect()
            car.move()
    for node in Common.nodes:
        node.status = node.colCheck()
    for sys in Common.lights:
        for light in sys:
            light.update()

    if pygame.time.get_ticks() % 10 == 0:
        Common.nodes[random.choice([0, 7])].spawn()
        Common.nodes[random.choice([2, 8])].spawn()

    pathfinding()

    # print(Common.barriers)


def pathfinding():
    global a, y
    pos = pygame.mouse.get_pos()

    p = 2
    for node in Common.nodes:
        if node not in Common.poles:
            r = node.image.get_rect()
            r.move_ip(node.x, node.y)
            if r.collidepoint(pos) and pygame.mouse.get_pressed()[0]:
                if len(Common.poles) == 0:
                    Common.poles.append(node)
                elif len(Common.poles) == 1:
                    Common.poles.append(node)

    if len(Common.poles) == 2 and a not in Common.sim and y == False:
        a = Vehicle("car", Common.poles[0], True)
        a.start = Common.poles[0]
        a.end = Common.poles[1]
        a.reInit()
        y = True

    if y == True and a not in Common.sim:
        Common.poles = []
        y = False

    o = ["Start1", "End1"]
    for i in range(len(Common.poles)):
        Common.poles[i].image = pygame.image.load("assets/Node/" + o[i] + ".png")

    for n in Common.nodes:
        if n not in Common.poles:
            n.image = pygame.image.load("assets/Node/Node1.png")


def main():
    pygame.init()

    global test
    while True:

        if not button1.click():
            update()
        if button2.click():
            Common.sim.empty()
            Common.graph = None
            button2.clicked = False
            initialise()
        screenMove()
        zoom()
        draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()


initialise()
main()
