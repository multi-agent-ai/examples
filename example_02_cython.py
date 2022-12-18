"""
python setup.py build_ext --inplace
"""

import random

from datetime import datetime
random.seed(datetime.now().timestamp())

WORLD_WIDTH = 2560
WORLD_HEIGHT = 1440

from agent import Agent

class Predator(Agent):
    def __init__(self, x=None, y=None, world_width=0, world_height=0):
        super().__init__(world_width=world_width, world_height=world_height)
        self.vmax = 2.5

class Prey(Agent):
    def __init__(self, x=None, y=None, world_width=0, world_height=0):
        super().__init__(world_width=world_width, world_height=world_height)
        self.vmax = 2.0

class Plant(Agent):
    def __init__(self, x=None, y=None, world_width=0, world_height=0):
        super().__init__(world_width=world_width, world_height=world_height)
        self.vmax = 0


def main():
    # open the ouput file
    f = open('output.csv', 'w')
    print(0, ',', 'Title', ',', 'Predator Prey Relationship / Example 02 / Cython', file=f)

    # create initial agents
    preys = [Prey(world_width=WORLD_WIDTH, world_height=WORLD_HEIGHT) for i in range(10)]
    predators = [Predator(world_width=WORLD_WIDTH, world_height=WORLD_HEIGHT) for i in range(10)]
    plants = [Plant(world_width=WORLD_WIDTH, world_height=WORLD_HEIGHT) for i in range(100)]

    timestep = 0
    while timestep < 10000:
        # update all agents
        #[f.update([]) for f in plants]  # no need to update the plants; they do not move
        [a.update(plants) for a in preys]
        [a.update(preys) for a in predators]

        # handle eaten and create new plant
        plants = [p for p in plants if p.is_alive is True]
        plants = plants + [Plant(world_width=WORLD_WIDTH, world_height=WORLD_HEIGHT) for i in range(2)]

        # handle eaten and create new preys
        preys = [p for p in preys if p.is_alive is True]

        for p in preys[:]:
            if p.energy > 5:
                p.energy = 0
                preys.append(Prey(x = p.x + random.randint(-20, 20), y = p.y + random.randint(-20, 20), world_width=WORLD_WIDTH, world_height=WORLD_HEIGHT))

        # handle old and create new predators
        predators = [p for p in predators if p.age < 2000]

        for p in predators[:]:
            if p.energy > 10:
                p.energy = 0
                predators.append(Predator(x = p.x + random.randint(-20, 20), y = p.y + random.randint(-20, 20), world_width=WORLD_WIDTH, world_height=WORLD_HEIGHT))

        # write data to output file
        #[print(timestep, ',', 'Position', ',', 'Predator', ',', a.x, ',', a.y, file=f) for a in predators]
        #[print(timestep, ',', 'Position',  ',', 'Prey', ',', a.x, ',', a.y, file=f) for a in preys]
        #[print(timestep, ',', 'Position',  ',', 'Plant', ',', a.x, ',', a.y, file=f) for a in plants]

        timestep = timestep + 1

    print(len(predators), len(preys), len(plants))

if __name__ == "__main__":
    main()
