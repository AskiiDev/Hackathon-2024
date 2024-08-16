#import mapgen
import pygame
from math import pi, sin, cos

MAP = [[1, 1, 1, 1, 1, 1, 1],
       [1, 0, 0, 0, 0, 0, 1],
       [1, 0, 0, 0, 0, 0, 1],
       [1, 0, 0, 0, 0, 0, 1],
       [1, 0, 0, 1, 0, 0, 1],
       [1, 0, 0, 0, 0, 0, 1],
       [1, 0, 0, 0, 0, 0, 1],
       [1, 1, 1, 1, 1, 1, 1]]

MAP_WIDTH = len(MAP)
MAP_HEIGHT = len(MAP[0])


WIDTH = 800
HEIGHT = 600

HALF_PI = 1.57

RENDER_DISTANCE = 10
ACCURACY = 2
RAY_STEP_SIZE = 0.07


running = True

pygame.init()
clock = pygame.time.Clock()
display = pygame.display.set_mode((WIDTH, HEIGHT))

player_coords = {'x': 2, 'y': 2}
player_rot = 0

FOV = HALF_PI / 2
WALK_SPEED = 1
TURN_SPEED = 5

MOVE_MAP = {pygame.K_w: 'w',
            pygame.K_s: 's',
            pygame.K_a: 'a',
            pygame.K_d: 'd'}


# -----------------------------------------------------------------------------------------------

def get_forward_vector(theta):
    return round(cos(theta), ACCURACY), round(sin(theta), ACCURACY)


def get_right_vector(theta):
    return round(cos(theta - HALF_PI), ACCURACY), round(sin(theta - HALF_PI), ACCURACY)


def try_move(vx, vy):
    dx = vy * WALK_SPEED
    dy = vx * WALK_SPEED

    player_coords['x'] += dx
    player_coords['y'] += dy

    if MAP[int(player_coords['x'])][int(player_coords['y'])] == 1:
        player_coords['x'] -= dx
        player_coords['y'] -= dy


def try_move_forward(delta, fv):
    fvx, fvy = get_forward_vector(player_rot)
    try_move(delta * fvx * fv, delta * fvy * fv)


def try_move_right(delta, rv):
    rvx, rvy = get_right_vector(player_rot)
    try_move(delta * rvx * rv, delta * rvy * rv)

    
def turn():



def input_handler():
    pressed = pygame.key.get_pressed()
    move = [MOVE_MAP[key] for key in MOVE_MAP if pressed[key]]

    if 'w' in move:
        try_move_forward(delta_time, 1)
    if 's' in move:
        try_move_forward(delta_time, -1)
    if 'a' in move:
        try_move_right(delta_time, 1)
    if 'd' in move:
        try_move_right(delta_time, -1)

# -----------------------------------------------------------------------------------------------


def ray_cast():
    for x in range(WIDTH):
        ray_angle = (player_rot - FOV / 2) + (x / WIDTH) * FOV
        eye_x = sin(ray_angle)
        eye_y = cos(ray_angle)

        wall_distance = 0

        hit_wall = False

        while not hit_wall and wall_distance < RENDER_DISTANCE:
            wall_distance += RAY_STEP_SIZE

            zx = player_coords['x'] + eye_x * wall_distance
            zy = player_coords['y'] + eye_y * wall_distance

            if zx < 0 or zx >= MAP_WIDTH or zy < 0 or zy >= MAP_HEIGHT:
                hit_wall = True
                wall_distance = RENDER_DISTANCE
            elif MAP[int(zx)][int(zy)] == 1:
                hit_wall = True
        #ceiling = 200 * (wall_distance / RENDER_DISTANCE)**2
        ceiling = HEIGHT / 2 - HEIGHT / wall_distance
        floor = HEIGHT - 2 * ceiling

        print(ceiling)

        pygame.draw.rect(display, (int(100 * (1 - wall_distance / RENDER_DISTANCE)), 0, 0), pygame.Rect(x, ceiling, 1, floor))



while running:
    display.fill((0, 0, 0))
    delta_time = 1 / clock.tick(60)

    input_handler()
    ray_cast()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
