import pygame

from config import WIDTH, HEIGHT
from game import Game

if __name__ == '__main__':
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pathfinding Traffic Model")
    game = Game(win)
    game.run()
    pygame.quit()
    exit()
