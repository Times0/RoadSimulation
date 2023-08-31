import pygame
import random
import math

import Common
from PathfindingAlgorithms import A_Path, makeGraph

# 25 pixel / metre
# Rotation: 0 = up, 180 = down, etc.

graph = makeGraph()

speeds = {"car": [40, 50], "truck": [30, 35], "bus": [20, 30]}

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, vehicleClass, start, user):
        pygame.sprite.Sprite.__init__(self)
        self.start = start
        self.end = Common.nodes[random.randint(0, len(Common.nodes)-1)]
        while self.start == self.end:
            self.end = Common.nodes[random.randint(0, len(Common.nodes)-1)]

        self.route = A_Path(self.start, self.end)

        for road in Common.edges:
            if road.start == self.start and road.end == self.route[1]:
                self.road = road
        
        self.angle = self.road.angle
        self.initAngle = self.angle

        self.image = pygame.image.load("assets/" + vehicleClass + ".png")
        self.image = pygame.transform.rotate(self.image, math.degrees(self.angle))
        self.rect = self.image.get_rect()

        self.type = vehicleClass

        self.x = self.road.start_x - self.rect[2]/2
        self.y = self.road.start_y - self.rect[3]/2

        self.rect.center = (self.road.start_x, self.road.start_y)

        self.velocity = 0
        self.speed = random.randint(speeds[vehicleClass][0], speeds[vehicleClass][1])
        self.acc = 0.005

        self.user = user
        
        Common.vehicles[Common.edges.index(self.road)].append(self)
        Common.sim.add(self)

    def reInit(self):
        self.route = A_Path(self.start, self.end)

        for road in Common.edges:
            if road.start == self.start and road.end == self.route[1]:
                self.road = road

        self.x = self.road.start_x - self.rect[2]/2
        self.y = self.road.start_y - self.rect[3]/2

        self.rect.center = (self.road.start_x, self.road.start_y)

        self.angle = self.road.angle
        self.image = pygame.transform.rotate(self.image, math.degrees(self.angle-self.initAngle))
        self.initAngle = self.angle

    def draw(self):
        self.rect = self.image.get_rect()
        Common.screen.blit(self.image, (self.x + Common.Shift[0], self.y + Common.Shift[1]))

    def move(self):
        self.x -= math.sin(self.angle) * self.velocity
        self.y -= math.cos(self.angle) * self.velocity
    
    def followRoute(self):
        roadLine = ((self.road.start_x, self.road.start_y), (self.road.start_x - math.sin(self.angle) * (self.road.length - 50), self.road.start_y - math.cos(self.angle) * (self.road.length - 50)))

        r = self.rect
        r.move_ip(self.x, self.y)

        #pygame.draw.line(Common.screen, (0, 255, 0), *roadLine)

        if not r.clipline(roadLine):
            Common.vehicles[Common.edges.index(self.road)].remove(self)
            if self.road.end == self.end:
                self.kill()
                del self
            else:
                for e in Common.edges:
                    if e.start == self.road.end and e.end == self.route[self.route.index(self.road.end) + 1]:
                        self.road = e
                        break
                self.angle = self.road.angle
                self.image = pygame.transform.rotate(self.image, math.degrees(self.angle-self.initAngle))
                self.initAngle = self.angle
                self.x = self.road.start_x - self.image.get_rect()[2]/2
                self.y = self.road.start_y - self.image.get_rect()[3]/2

                Common.vehicles[Common.edges.index(self.road)].append(self)
    
    def update(self):
        if self.velocity < abs(self.speed * 0.005) and self.velocity < abs(self.road.limit * 0.005):
            self.velocity += self.acc

    def detect(self):
        bDist = 30 + self.image.get_rect()[3] + (self.velocity * 100) # Max distance between car and object infront.

        x = self.x + self.image.get_rect().width / 2 #self.x - math.cos(self.angle) * self.rect[2]/2 + abs(math.sin(self.angle) * self.rect[3]/2)
        y = self.y + self.image.get_rect().height /2 #self.y + abs(math.sin(self.angle) * self.rect[2]/2) - math.cos(self.angle) * self.rect[3]/2

        raycast = ((x, y), (x - math.sin(self.angle) * bDist, y - math.cos(self.angle) * bDist))

        pygame.draw.line(Common.screen, (0, 255, 0), (raycast[0][0] + Common.Shift[0], raycast[0][1] + Common.Shift[1]), (raycast[1][0] + Common.Shift[0], raycast[1][1] + Common.Shift[1]), 3)    # Visible drawing of raycast line        
        
        s = False

        if self.road.end.colCheck() == True and s == False:
            if self.road.end.border.clipline(raycast):
                k = math.sqrt((x - self.road.end.border.clipline(raycast)[1][0])**2 + (y - self.road.end.border.clipline(raycast)[1][1])**2) - self.image.get_rect().height
                if k < 25:
                        self.velocity = 0
                        s = True

        for bar in Common.barriers:
            if bar.clipline(raycast) and s == False:
                t = math.sqrt((x - bar.clipline(raycast)[1][0])**2 + (y - bar.clipline(raycast)[1][1])**2) - self.image.get_rect().height
                #print(t)
                if t > 11 and t < self.image.get_rect().height:
                    self.velocity = 0
                    s = True

        for car in Common.vehicles[Common.edges.index(self.road)]:
            if car != self:
                r = car.image.get_rect()
                h = r[3]
                r.move_ip(car.x, car.y)
                if r.clipline(raycast) and s == False:
                    t = math.sqrt((x - r.clipline(raycast)[1][0])**2 + (y - r.clipline(raycast)[1][1])**2) - h
                    if t < h:
                        self.velocity = 0
                        s = True
                    else:
                        s = True
                        v = car.velocity
                        if self.velocity > v:
                            self.velocity *= ((t) / (bDist + h))