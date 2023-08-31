import pygame
from pygame.locals import *

import Common

class Button():
    def __init__(self, x, y, path):
        self.path = path
        self.image = pygame.image.load("assets/GUI/" + path[0] + ".png")
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

        self.t = 0
        
    def draw(self):
        pygame.draw.rect(Common.screen, (0,0,0), (self.rect.x - 12, self.rect.y - 7, self.rect.width + 24, self.rect.height + 14)) # outline
        pygame.draw.rect(Common.screen, (220,220,220), (self.rect.x - 10, self.rect.y - 5, self.rect.width + 20, self.rect.height + 10)) # background
        Common.screen.blit(self.image, (self.rect.x, self.rect.y)) # image
    
    def click(self):
        self.t += 1
        pos = pygame.mouse.get_pos()
         
        if self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] == 1 and self.t > 100:
            self.t = 0
            self.clicked = not self.clicked
            self.image = pygame.image.load("assets/GUI/" + self.path[self.clicked] + ".png")

        return self.clicked

def screenMove():
    keys = pygame.key.get_pressed()

    Common.Shift[0] += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 0.5
    Common.Shift[1] += (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * 0.5

def zoom():
    for event in pygame.event.get():
        if event.type == pygame.MOUSEWHEEL:
            Common.Scale *= (event.y * 1.5)
    
    if Common.Scale < 1:
        Common.Scale = 1