#import mapgen
import pygame
from math import pi, sin, cos

MAP = [[1, 1, 1, 1, 1, 1, 1],
       [1, 0, 0, 0, 0, 0, 1],
       [1, 0, 0, 0, 0, 0, 1],
       [1, 0, 0, 0, 0, 0, 1],
       [1, 0, 1, 0, 2, 0, 1],
       [1, 0, 1, 1, 1, 0, 1],
       [1, 0, 0, 0, 0, 0, 1],
       [1, 1, 1, 1, 1, 1, 1]]

TEMP_WALL = 2

MAP_WIDTH = len(MAP)
MAP_HEIGHT = len(MAP[0])

HUD_OFFSET = 150
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
TURN_SPEED = 0.003

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
    if MAP[int(player_coords['x'])][int(player_coords['y'])] == TEMP_WALL:
        player_coords['x'] -= dx

    player_coords['y'] += dy
    if MAP[int(player_coords['x'])][int(player_coords['y'])] == TEMP_WALL:
        player_coords['y'] -= dy


def try_move_forward(delta, fv):
    fvx, fvy = get_forward_vector(player_rot)
    try_move(delta * fvx * fv, delta * fvy * fv)


def try_move_right(delta, rv):
    rvx, rvy = get_right_vector(player_rot)
    try_move(delta * rvx * rv, delta * rvy * rv)


def turn():
    pass


def input_handler(delta_time):
    global player_rot

    pressed = pygame.key.get_pressed()
    move = [MOVE_MAP[key] for key in MOVE_MAP if pressed[key]]

    pygame.mouse.set_pos(100, 100)
    player_rot += pygame.mouse.get_rel()[0] * TURN_SPEED

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
            elif MAP[int(zx)][int(zy)] == TEMP_WALL:
                hit_wall = True

        ceiling = (HEIGHT - 150) / 2 - (HEIGHT - 150) / wall_distance
        floor = (HEIGHT - 150) - 2 * ceiling

        pygame.draw.rect(display, (int(200 * (1 - wall_distance / RENDER_DISTANCE)), 0, 0), pygame.Rect(x, ceiling, 1, floor))


def render_hud():
    pygame.draw.rect(display, (200, 200, 0), pygame.Rect(0, HEIGHT - 150, WIDTH, 150))


def init():
    global running
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)

    while running:
        display.fill((0, 0, 0))
        delta_time = 1 / clock.tick(60)

        input_handler(delta_time)
        ray_cast()
        render_hud()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit()
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()


init()