import pygame
import math
import random

import Common

import VehicleClasses as veh

class Node():
    def __init__(self, pos, type, n):
        self.x = pos[0] - 25 - Common.Difference[0]
        self.y = pos[1] - 25 - Common.Difference[1]
        self.type = type # Type of traffic features at node, i.e. intersection, roundabout, etc.

        self.image = pygame.image.load("assets/Node/Node1.png")

        self.parent = self
        self.f = 0

        self.n = n

        self.status = False
        self.border = pygame.rect.Rect(self.x - 12.5, self.y - 12.5, 75, 75)
    
    def draw(self):
        Common.screen.blit(self.image, (self.x + Common.Shift[0], self.y + Common.Shift[1]))

        pygame.draw.rect(Common.screen, (100, 100, 100), (self.x - 12.5 + Common.Shift[0], self.y - 12.5 + Common.Shift[1], 75, 75), 5)

    def cost(self, dest):
        w = 0
        for road in Common.edges:
            if road.start == self.parent and road.end == self:
                w = road.weight
                break
        return w + self.parent.f + findDist(self, dest)
    
    def spawn(self):
        if self.status == False:
            q = veh.Vehicle(random.choice(["car", "car", "car", "car", "car", "truck", "bus"]), self, False)

    def colCheck(self):
        border = pygame.rect.Rect(self.x - 12.5, self.y - 12.5, 75, 75)
        for car in Common.sim:
            #if car is not veh:
                r = car.image.get_rect()
                r.move_ip(car.x, car.y)

                if r.colliderect(border) == True:
                    Common.barriers.append(self.border)
                    return True
        if self.border in Common.barriers:
            Common.barriers.remove(self.border)
        return False
        
class Edge():
    def __init__(self, start, end, limit):
        self.start = start
        self.end = end
        self.weight = 0
        self.angle = self.getAngle()

        self.start_x = start.x + 25 + math.cos(self.angle) * 25 - Common.Difference[0]
        self.start_y = start.y + 25 - math.sin(self.angle) * 25 - Common.Difference[1]
        self.end_x = end.x + 25 + math.cos(self.angle) * 25 - Common.Difference[0]
        self.end_y = end.y + 25 - math.sin(self.angle) * 25 - Common.Difference[1]

        self.length = math.sqrt((self.end.x - self.start.x)**2 + (self.end.y - self.start.y)**2)

        self.limit = limit #speed limit

    def getAngle(self):
        # c^2 = a^2 + b^2 - 2abcosC
        # a = b = l

        # Angle = arccos((c^2 - a^2 - b^2) / -2ab)
        
        l = math.sqrt((self.end.x - self.start.x)**2 + (self.end.y - self.start.y)**2)
        c = math.sqrt((self.end.x - self.start.x)**2 + (self.end.y - self.start.y + l)**2)
        cosAngle = (c**2 - 2 * l**2) / (-2 * l**2)

        if self.start.x <= self.end.x:
            return -math.acos(cosAngle)
        return math.acos(cosAngle)


    def draw(self): 
        roadLine = ((self.start_x + Common.Shift[0], self.start_y + Common.Shift[1]), (self.end_x + Common.Shift[0], self.end_y + Common.Shift[1]))
        pygame.draw.line(Common.screen, self.getCol(), *roadLine, 5)
    
    def getCol(self):
        for car in Common.sim:
            if car.user == True:
                route_roads = []
                for i in range(0, len(car.route)-1):
                    for e in Common.edges:
                        if e.start == car.route[i] and e.end == car.route[i+1]:
                            route_roads.append(e)
                if self in route_roads:
                    return (0, 255, 153)
        return (52,52,52)

def findDist(s, e):
    return math.sqrt((s.x - e.x)**2 + (s.y - e.y)**2)

class TrafficLight():
    def __init__(self, pos, road, system):
        self.x = pos[0]
        self.y = pos[1]

        self.road = road
        self.angle = road.angle - math.pi/2

        self.status = "green"
        self.prev = "green"
        self.tick = 0

        Common.lights[system].append(self)

        self.cross = pygame.image.load("assets/cross.png")
        self.rect = self.cross.get_rect()
        self.rect.move_ip(self.x, self.y)
        pygame.transform.rotate(self.cross, math.degrees(self.angle))

    def draw(self):
        image = pygame.image.load("assets/signals/" + self.status + ".png")
        Common.screen.blit(image, (self.x + 15 + Common.Shift[0], self.y + 15 + Common.Shift[1]))

        Common.screen.blit(self.cross, (self.x, self.y))

    def signals(self):
        if self.status == "green" and self.tick > 1000:
            self.tick = 0
            self.status = "yellow"
            self.prev = "green"
        if self.status == "yellow":
            if self.tick > 400:
                self.tick = 0
                if self.prev == "green":
                    self.status = "red"
                else: 
                    self.status = "green"
                    Common.barriers.remove(self.rect)
            else:
                if self.prev == "green":
                    Common.barriers.append(self.rect)
        if self.status == "red" and self.tick > 1000:
            self.tick = 0
            self.status = "green"
            self.prev = "red"
        
        return self.status
        
    def update(self):
        self.status = self.signals()
        self.tick += 1
