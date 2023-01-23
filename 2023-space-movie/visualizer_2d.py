import pygame
from pygame.locals import (K_ESCAPE, KEYDOWN)
import click

# Define constants for the screen width and height
SCREEN_WIDTH = 2560
SCREEN_HEIGHT = 1440

@click.command(help="Displays the content of a simulations output file in a 2-dimensional window.")
@click.option('--agentids', '-a', is_flag=True, default=False, help="Displays the aagent IDs.")
@click.option('--filename', '-f', default='output.csv', help="The simulation file to read.")
def main(filename: str = '', record: bool = False, agentids: bool = False):
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Run until the user asks to quit
    running = True
    last_timestep = 0
    with open('output.csv') as f:
        for line in f:
            # check user input events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False

            if not running:
                break

            items = [x.strip() for x in line.split(',')]
            timestep = int(items[0])
            items_type = items[1]

            if items_type == 'Position':
                agent_id, x, y = items[2:5]
                agent_id = int(agent_id)

                screen_x = float(x) + SCREEN_WIDTH / 2
                screen_y = float(y) + SCREEN_HEIGHT / 2
                if agent_id % 2 == 0:
                    color = (255, 0, 0)
                elif agent_id %2 == 1:
                    color = (0, 255, 0)
                else:
                    color = (255, 255, 0)

                pygame.draw.circle(screen, color, (screen_x, screen_y), 1)

                if agentids:
                    font = pygame.font.SysFont('opensans', 12)
                    text_surface = font.render(f'{agent_id}', False, (128, 128, 128))
                    screen.blit(text_surface, (screen_x, screen_y))


            if timestep > last_timestep:
                last_timestep = timestep
                pygame.display.flip()
                screen.fill((0, 0, 0))
                clock.tick(24)

    # Done! Time to quit.
    pygame.quit()

if __name__ == "__main__":
    main()
