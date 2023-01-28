"""
Simple Spaceship Simulation

"""

import random
import typing
import numpy as np

random.seed(42)

h = 0.2  # time step Δt

class Agent():
    vmax = 15.0

    @staticmethod
    def square_distance(x: np.ndarray) -> np.ndarray:
        """
        Calculates the square of the norm of the input vector.

        Args:
            x: the vector

        Returns:
            Square of the norm of the input vector
        """
        return x.dot(x)

    def __init__(self, agent_id: int, agent_type: int, x: float, y: float, z: float):
        self.type = agent_type
        self.id = agent_id

        # https://stackoverflow.com/questions/43541934/implementing-3d-vectors-in-python-numpy-vs-x-y-z-fields
        # initial position, velocity, and acceleration/force
        self.position = np.array([x, y, z], dtype=np.float64)
        self.velocity = np.array([0, 0, 0], dtype=np.float64)
        self.force = np.array([0, 0, 0], dtype=np.float64)

        # inital values
        self.is_alive = True
        self.target = None
        self.targeted = 0
        self.energy = 100
        self.neighbors = []

    def hit(self, systemtime:int, output_file: typing.TextIO, damage: float=1.0):
        """
        This agent received a hit from another agent.

        Args:
            systemtime: The current time step of the simulation.
            output_file: An open file descriptor which accepts the output of the simulation.
            damage (optional): The amount of damage per hit (multiplied by h)
        """

        self.energy = self.energy - h * damage  # damage per shot

        if self.energy < 0:
            if self.target:
                self.target.targeted -= 1

            self.is_alive = False
            print(f"{systemtime}, Explosion, {self.id}", file=output_file)
            print('agent', self.id, 'dies @', systemtime)

    def find_target(self, agents: typing.List['Agent'], min_distance: float=np.inf, max_targets=8):
        """
        Find a new target if existing target is too far away or none has been assigned yet.

        Args:
            agents: All agents in the simulation that can be a target
            min_distance (optional): Distance of target to be found
        """
        if self.target:
            distance = Agent.square_distance(self.position - self.target.position)
            if distance > min_distance or random.random()<0.01:
                self.target.targeted -= 1
                self.target = None

        if not self.target:
            min_distance_tmp = min_distance
            for a in agents:
                if a.type is not self.type and a.is_alive and a.targeted < max_targets:
                    distance = Agent.square_distance(self.position - a.position)
                    if distance < min_distance_tmp:
                        min_distance_tmp = distance
                        self.target = a

            if self.target:
                self.target.targeted += 1

    def attack(self, systemtime: int, output_file: typing.TextIO, min_distance: float=0, probability: float=0.08):
        """
        Shoot at the target if close enough.

        Args:
            systemtime: The current time step of the simulation.
            output_file: An open file descriptor which accepts the output of the simulation.
            distance (float, optional): _description_. Defaults to 0.
            probability (float, optional): _description_. Defaults to 0.08.
        """
        if self.target:
            distance = Agent.square_distance(self.position - self.target.position)

            if distance < min_distance:
                if random.random() <= probability:  # shoot not too often, reloading or sth
                    print(f"{systemtime}, Shot, {self.id}, {self.target.id}", file=output_file)
                    self.target.hit(systemtime, output_file, damage=2.5)

    def reset_neighbor_cache(self, agents: typing.List['Agent'], min_distance: float=np.inf):
        """
        Reset the neighbor cache.

        Args:
            agents: All agents in the simulation that can affect this agent.
            min_distance (float, optional): _description_. Defaults to np.inf.
        """
        self.neighbors = []
        for a in agents:
            if a is not self and a.is_alive:
                distance = Agent.square_distance(self.position - a.position)
                if distance < min_distance:
                    self.neighbors.append(a)

    def calculate_force_social(self) -> np.ndarray:
        """
        Social interaction between agents.

        Returns:
            np.ndarray: A vector containing the force that pushes away from other agents.
        """
        force = np.array([0, 0, 0], dtype=np.float64)
        for a in self.neighbors:
            distance = np.linalg.norm(self.position - a.position)

            if distance < 2:
                factor = 2 / np.exp(0.5 * 2)
            else:
                factor = distance / np.exp(0.5 * distance)

            force = force + factor * (self.position - a.position)

        return force

    def calculate_force_center(self) -> np.ndarray:
        """
        Calculate desire to go to center of simulation 0/0/0 if too far out. a bit up 0, 0, -50

        Returns:
            np.ndarray: A vector containing the force that pulls towards the center.
        """
        direction = (self.position)
        distance = np.linalg.norm(direction)

        factor = distance ** 2 / 1000000
        return factor * (-direction / distance)

    def calculate_force_nofly_zone(self) -> np.ndarray:
        """
        Avoid the space station located at 0, 500, 40 with a radius of apprx 180

        Returns:
            np.ndarray: A vector containing the force that pushes away from the space station.
        """
        station = np.array([0, 500, 40], dtype=np.float64)
        direction = (self.position - station)
        distance = np.linalg.norm(direction)

        factor = min(0.2, np.exp(-(distance-180)/12))  # soft transition
        direction = direction / distance
        return factor * direction

    def calculate_force_target(self) -> np.ndarray:
        """
        Move in the direction of the target, if any

        Returns:
            np.ndarray: A vector containing the force that pulls towards the assigned target.
        """
        if self.target:
            direction = (self.target.position - self.position)
            return direction / np.linalg.norm(direction)

        return np.array([0, 0, 0], dtype=np.float64)

    def update(self, systemtime: int, agents: typing.List['Agent'], output_file: typing.TextIO):
        """
        Update agent's acceleration based on various forces.

        Args:
            systemtime: The current time step of the simulation.
            output_file: An open file descriptor which accepts the output of the simulation.
            agents: All agents currently in the simulation.
        """

        if not self.is_alive:
            return

        # attack targets
        if self.target and (self.target not in agents or not self.target.is_alive):  # target is dead, don't chase it further
            self.target = None

        self.find_target(agents, min_distance=100**2)
        self.attack(systemtime, output_file, min_distance=500)  # was 350

        # the neighbor cache is for faster access to agents nearby
        if systemtime % 10 == 0:
            self.reset_neighbor_cache(agents, min_distance=10000)

        # calculate the forces
        f_social = self.calculate_force_social()
        f_center = self.calculate_force_center()
        f_nofly = self.calculate_force_nofly_zone()
        f_target = self.calculate_force_target()

        force = 0.2 * f_social + 0.4 * f_center + 0.1 * f_nofly + 0.4 *f_target

        # update direction based on the forces 
        # Leapfrog integration (https://en.wikipedia.org/wiki/Leapfrog_integration)
        self.velocity = self.velocity + h * 0.5 * (self.force + force)
        self.force = force

        # slow down agent if it moves faster than its max velocity ... like drag or speed limits?
        velocity = np.linalg.norm(self.velocity)
        if velocity > (Agent.vmax * h):
            self.velocity = self.velocity / velocity * (Agent.vmax * h)

    def move(self, systemtime: int, output_file: typing.TextIO):
        """
        Update agent's position based on acceleration.

        Args:
            systemtime: The current time step of the simulation.
            output_file: An open file descriptor which accepts the output of the simulation.
       """
        if self.is_alive:
            # update position based on velocity and a half step of the force (Leapfrog)
            delta_position = h * self.velocity + (0.5 * self.force) * h ** 2

            # slow down agent if it moves faster than its max velocity
            delta_position_norm = np.linalg.norm(delta_position)
            if delta_position_norm > (Agent.vmax * h):
                delta_position = delta_position / delta_position_norm * (Agent.vmax * h)

            self.position = self.position + delta_position

            message = f"{systemtime}, Position, {self.id}, "
            message += f"{self.position[0]}, {self.position[1]}, {self.position[2]}, "
            message += f"{self.velocity[0]}, {self.velocity[1]}, {self.velocity[2]}, "
            message += f"{self.force[0]}, {self.force[1]}, {self.force[2]}"
            print(message, file=output_file)

def main():
    # open and initialize the the ouput file
    output_file = open('output.csv', 'w')
    print(0, ',', 'Title', ',', 'Simple Spaceship Simulation', file=output_file)
    print(0, ',', 'Scene', ',', 0, ',', 0, ',', 1280,  file=output_file)

    # create initial agents
    agents = []
    missiles = []
    agent_ids = 0
    for i in range(400):
        x = random.randint(-1000, -500) if i%2 == 0 else random.randint(500, 1000)
        y = random.randint(-1000, 1000)
        z = random.randint( 250, 500)
        agents.append(Agent(agent_id=agent_ids, agent_type=i%2, x=x, y=y, z=z))
        print(f"0, Agent, {agent_ids}, {i%2}", file=output_file)
        agent_ids = agent_ids + 1

    for systemtime in range(12500):
        # move all agents to new position first, so all positions are known
        for a in agents:
            a.move(systemtime, output_file)

        # update all agents velocity and do other stuff like shooting
        for a in agents:
            a.update(systemtime, agents, output_file)

        # handle dead agents (not too often)
        if systemtime % 100 == 0:
            agents = [a for a in agents if a.is_alive is True]
            missiles = [m for m in missiles if m.is_alive is True]

        if systemtime % 100 == 0:
            print('+++', systemtime, len(agents))

    print('Survivers:', len(agents), [a.id for a in agents])

if __name__ == "__main__":
    main()
