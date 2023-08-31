import pygame

# Range of possible max speeds for cars and trucks

clock = pygame.time.Clock()

nodes = []
edges = []

vehicles = []  # List of vehicles based on where they are

graph = None
poles = []

sim = pygame.sprite.Group()

pygame.display.set_caption('Pathfinding Traffic Model')
screen = pygame.display.set_mode((960, 720))

Shift = [0, 0]
Scale = 1

lights = []
barriers = []
