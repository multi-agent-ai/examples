import math
import random

import pygame
from pygame.locals import (K_ESCAPE, KEYDOWN)

SIMULATION_NAME = 'Multi-Agent AI'
SIMULATION_EXPERIMENT = 'Predator Prey Relationship / Example 01'

# Define constants for the screen width and height
SCREEN_WIDTH = 2560
SCREEN_HEIGHT = 1440

class Agent(pygame.sprite.Sprite):
    def __init__(self, size, color, x=None, y=None):
        super().__init__()

        # draw agent
        self.surf = pygame.Surface((2*size, 2*size), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.surf, color, (size, size), size)
        self.rect = self.surf.get_rect()

        # default values
        self.vmax = 2.0

        # initial position
        self.x = x if x else random.randint(0, SCREEN_WIDTH)
        self.y = y if y else random.randint(0, SCREEN_HEIGHT)

        # initial velocity
        self.dx = 0
        self.dy = 0

        # inital values
        self.is_alive = True
        self.target = None
        self.age = 0
        self.energy = 0

        # move agent on screen
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

    def update(self, screen, food=()):
        self.age = self.age + 1

        # we can't move, just update the screen
        if self.vmax == 0:
            screen.blit(self.surf, self.rect)
            return

        # target is dead, don't chase it further
        if self.target and not self.target.is_alive:
            self.target = None

        # eat the target if close enough
        if self.target:
            squared_dist = (self.x - self.target.x) ** 2 + (self.y - self.target.y) ** 2
            if squared_dist < 400:
                self.target.is_alive = False
                self.energy = self.energy + 1

        # agent doesn't have a target, find a new one
        if not self.target:
            min_dist = 9999999
            min_agent = None
            for a in food:
                if a is not self and a.is_alive:
                    sq_dist = (self.x - a.x) ** 2 + (self.y - a.y) ** 2
                    if sq_dist < min_dist:
                        min_dist = sq_dist
                        min_agent = a
            if min_dist < 100000:
                self.target = min_agent

        # initalize 'forces' to zero
        fx = 0
        fy = 0

        # move in the direction of the target, if any
        if self.target:
            fx += 0.1*(self.target.x - self.x)
            fy += 0.1*(self.target.y - self.y)

        # update our direction based on the 'force'
        self.dx = self.dx + 0.05*fx
        self.dy = self.dy + 0.05*fy

        # slow down agent if it moves faster than it max velocity
        velocity = math.sqrt(self.dx ** 2 + self.dy ** 2)
        if velocity > self.vmax:
            self.dx = (self.dx / velocity) * (self.vmax)
            self.dy = (self.dy / velocity) * (self.vmax)

        # update position based on delta x/y
        self.x = self.x + self.dx
        self.y = self.y + self.dy

        # ensure it stays within the screen window
        self.x = max(self.x, 0)
        self.x = min(self.x, SCREEN_WIDTH)
        self.y = max(self.y, 0)
        self.y = min(self.y, SCREEN_HEIGHT)

        # update graphics
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        screen.blit(self.surf, self.rect)

class Predator(Agent):
    def __init__(self, x=None, y=None):
        size = 4
        color = (255, 0, 0)
        super().__init__(size, color)
        self.vmax = 2.5

class Prey(Agent):
    def __init__(self, x=None, y=None):
        size = 3
        color = (255, 255, 255)
        super().__init__(size, color)
        self.vmax = 2.0

class Plant(Agent):
    def __init__(self, x=None, y=None):
        size = 2
        color = (0, 128, 0)
        super().__init__(size, color)
        self.vmax = 0

def main():
    # Import and initialize the pygame library
    pygame.init()
    clock = pygame.time.Clock()

    # Create the screen object
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f'Simulation')

    # create initial agents
    preys = [Prey() for i in range(10)]
    predators = [Predator() for i in range(10)]
    plants = [Plant() for i in range(100)]

    # Run until the user asks to quit
    running = True
    while running:
        # check user input events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

         # Fill the background
        screen.fill((11, 11, 11))

        # update all agents
        [f.update(screen) for f in plants]
        [a.update(screen, food=plants) for a in preys]
        [a.update(screen, food=preys) for a in predators]

        # handle eaten and create new plant
        plants = [p for p in plants if p.is_alive is True]
        plants = plants + [Plant() for i in range(2)]

        # handle eaten and create new preys
        preys = [p for p in preys if p.is_alive is True]

        for p in preys[:]:
            if p.energy > 5:
                p.energy = 0
                preys.append(Prey(x = p.x + random.randint(-20, 20), y = p.y + random.randint(-20, 20)))

        # handle old and create new predators
        predators = [p for p in predators if p.age < 2000]

        for p in predators[:]:
            if p.energy > 10:
                p.energy = 0
                predators.append(Predator(x = p.x + random.randint(-20, 20), y = p.y + random.randint(-20, 20)))

        # draw all changes to the screen
        pygame.display.flip()
        clock.tick(24)         # wait until next frame (at 60 FPS)

    # Done! Time to quit.
    pygame.quit()


if __name__ == "__main__":
    main()
