import mapgen
import pygame
from math import pi, sin, cos



MAP = [[1, 1, 1, 1, 1, 1, 1],
       [1, 0, 0, 0, 0, 0, 1],
       [1, 0, 0, 0, 0, 0, 1],
       [1, 0, 0, 0, 0, 0, 1],
       [1, 0, 0, 0, 0, 0, 1],
       [1, 0, 0, 0, 0, 0, 1],
       [1, 0, 0, 0, 0, 0, 1],
       [1, 1, 1, 1, 1, 1, 1]]


HALF_PI = 1.5707963267
ACCURACY = 2

running = True

pygame.init()
clock = pygame.time.Clock()
display = pygame.display.set_mode((800, 600))

player_coords = {'x': 2, 'y': 2}
player_rot = 0

FOV = HALF_PI / 2
WALK_SPEED = 1
TURN_SPEED = 5
print('a')


def get_forward_vector(theta):
    return round(cos(theta), ACCURACY), round(sin(theta), ACCURACY)


def get_right_vector(theta):
    return round(cos(theta - HALF_PI), ACCURACY), round(sin(theta - HALF_PI), ACCURACY)


def try_move(vx, vy):
    dx = vx * WALK_SPEED
    dy = vy * WALK_SPEED

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
    print(rvx, rvy)
    try_move(delta * rvx * rv, delta * rvy * rv)


while running:
    delta_time = 1 / clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                try_move_forward(delta_time, 1)
            if event.key == pygame.K_s:
                try_move_forward(delta_time, -1)
            if event.key == pygame.K_a:
                try_move_right(delta_time, 1)
            if event.key == pygame.K_d:
                try_move_right(delta_time, -1)
            if event.key == pygame.K_LEFT:
                player_rot += pi/8
            print(player_coords)

        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

