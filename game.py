from mapgen import gen_map, gen_map_grid, get_stationart, get_start_pos
import pygame
import math 

TEMP_WALL = 2

MAP_WIDTH = 0
MAP_HEIGHT = 0

HUD_OFFSET = 150
WIDTH = 800
HEIGHT = 600

HALF_PI = 1.57

RENDER_DISTANCE = 10
ACCURACY = 2
RAY_STEP_SIZE = 0.1

TEXTURE_WIDTH = 64
TEXTURE_HEIGHT = 64

running = True

pygame.init()
clock = pygame.time.Clock()
display = pygame.display.set_mode((WIDTH, HEIGHT))

player_coords = {'x': 2, 'y': 2}
player_rot = HALF_PI
player_rotation = {'x': 0, 'y': -1}


FOV = HALF_PI / 2
WALK_SPEED = 2
TURN_SPEED = 0.003

MOVE_MAP = {pygame.K_w: 'w',
            pygame.K_s: 's',
            pygame.K_a: 'a',
            pygame.K_d: 'd'}


# -----------------------------------------------------------------------------------------------

def get_forward_vector(theta):
    return round(math.cos(theta), ACCURACY), round(math.sin(theta), ACCURACY)


def get_right_vector(theta):
    return round(math.cos(theta - HALF_PI), ACCURACY), round(math.sin(theta - HALF_PI), ACCURACY)


def try_move(vx, vy):
    dx = vx * WALK_SPEED
    dy = vy * WALK_SPEED

    player_coords['x'] += dx
    if MAP[int(player_coords['x'])][int(player_coords['y'])] == TEMP_WALL:
        player_coords['x'] -= dx

    player_coords['y'] += dy
    if MAP[int(player_coords['x'])][int(player_coords['y'])] == TEMP_WALL:
        player_coords['y'] -= dy


def try_move_forward(delta, fv):
    fvx, fvy = player_rotation['x'], player_rotation['y']
    try_move(delta * fvx * fv, delta * fvy * fv)


def try_move_right(delta, rv):
    rvx, rvy = -player_rotation['y'], player_rotation['x']
    try_move(delta * rvx * rv, delta * rvy * rv)


def turn():
    pass


def input_handler(delta_time):
    global player_rotation
    global player_rot
    global camera_plane

    pressed = pygame.key.get_pressed()
    move = [MOVE_MAP[key] for key in MOVE_MAP if pressed[key]]

    pygame.mouse.set_pos(100, 100)

    # print(player_rotation)
    turn_delta = - pygame.mouse.get_rel()[0] * TURN_SPEED

    old_player_rotation = player_rotation.copy()
    player_rotation['x'] = (old_player_rotation['x'] * math.cos(turn_delta) - old_player_rotation['y'] * math.sin(turn_delta))
    player_rotation['y'] = (old_player_rotation['x'] * math.sin(turn_delta) + old_player_rotation['y'] * math.cos(turn_delta))

    old_camera_plane = camera_plane.copy()
    camera_plane['x'] = (old_camera_plane['x'] * math.cos(turn_delta) - old_camera_plane['y'] * math.sin(turn_delta))
    camera_plane['y'] = (old_camera_plane['x'] * math.sin(turn_delta) + old_camera_plane['y'] * math.cos(turn_delta))


    if 'w' in move:
        try_move_forward(delta_time, 1)
    if 's' in move:
        try_move_forward(delta_time, -1)
    if 'd' in move:
        try_move_right(delta_time, -1)
    if 'a' in move:
        try_move_right(delta_time, 1)

# -----------------------------------------------------------------------------------------------

def load_image(image, darken, colorKey = None):
    ret = []
    if colorKey is not None:
        image.set_colorkey(colorKey)
    if darken:
        image.set_alpha(127)
    for i in range(image.get_width()):
        s = pygame.Surface((1, image.get_height())).convert()
        #s.fill((0,0,0))
        s.blit(image, (- i, 0))
        if colorKey is not None:
            s.set_colorkey(colorKey)
        ret.append(s)
    print(len(ret))
    return ret

def ray_cast_better():
    global background
    global texture

    w = WIDTH
    h = HEIGHT - 150
    
    if background is None:
        background = pygame.transform.scale(pygame.image.load("imgs/background.png").convert(), (w, h))
    
    display.blit(background, (0, 0)) 

    z_buffer = []

    for x in range(w):
        camera_x = float(2*x / float(w) - 1)
        ray_pos_x = player_coords['x']
        ray_pos_y = player_coords['y']
        ray_dir_x = player_rotation['x'] + camera_x * camera_plane['x']
        # print(ray_dir_x)
        ray_dir_y = player_rotation['y'] + camera_x * camera_plane['y']

        map_x = int(ray_pos_x)
        map_y = int(ray_pos_y) 

        side_dist_x = 0.
        side_dist_y = 0.

        if ray_dir_x== 0: 
            ray_dir_x = 0.00001
        d_dist_x = math.sqrt(1 + (ray_dir_y ** 2) / (ray_dir_x ** 2))
        # print(d_dist_x)
        if ray_dir_y== 0: 
            ray_dir_y = 0.00001
        d_dist_y = math.sqrt(1 + (ray_dir_x ** 2) / (ray_dir_y ** 2))

        perp_wall_dist = 0
        step_x = 0
        step_y = 0
        
        hit = False
        side = 0

        if ray_dir_x < 0:
            step_x = -1
            side_dist_x = (ray_pos_x - map_x) * d_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1 - ray_pos_x) * d_dist_x
    
        if ray_dir_y < 0:
            step_y = - 1
            side_dist_y = (ray_pos_y - map_y) * d_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - ray_pos_y) * d_dist_y 
        
        while not hit:
            if side_dist_x < side_dist_y:
                side_dist_x += d_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += d_dist_y
                map_y += step_y
                side = 1

            if (MAP[int(map_x)][int(map_y)] == TEMP_WALL):
                hit = 1

        if side == 0:
            perp_wall_dist = (abs((map_x - ray_pos_x + (1 - step_x) / 2) / ray_dir_x))
        else:
            perp_wall_dist = (abs((map_y - ray_pos_y + (1 - step_y) / 2) / ray_dir_y))

        if perp_wall_dist == 0: 
            perp_wall_dist = 0.00001
        
        line_height = abs(int(h / perp_wall_dist)) 
        
        draw_start = - line_height / 2 + h / 2 
        draw_end = line_height / 2 + h / 2 

        wall_x = 0
        if side == 1:
            wall_x = ray_pos_x + ((map_y - ray_pos_y + (1 - step_y) / 2) / ray_dir_y) * ray_dir_x
        else:
            wall_x = ray_pos_y + ((map_x - ray_pos_x + (1 - step_x) / 2) / ray_dir_x) * ray_dir_y
        wall_x -= math.floor((wall_x))

        tex_x = int(wall_x * float(TEXTURE_WIDTH)) 
        
        if side == 0 and ray_dir_x > 0:
            tex_x = TEXTURE_WIDTH - tex_x - 1
        if side == 1 and ray_dir_y < 0:
            tex_x = TEXTURE_WIDTH - tex_x - 1

        if line_height > 10000:
            line_height = 10000
            draw_start = -5000 + h/2
            draw_end = 5000 + h/2

        # print(tex_x)

        display.blit(pygame.transform.scale(texture[tex_x], (1, line_height)), (x, draw_start))
        z_buffer.append(perp_wall_dist)


def render_hud():
    pygame.draw.rect(display, (100, 100, 100), pygame.Rect(0, HEIGHT - 150, WIDTH, 150))


def init():
    global running
    global player_coords
    global player_rotation
    global camera_plane
    global MAP
    global MAP_WIDTH
    global MAP_HEIGHT
    global background
    global texture

    background = None
    texture = load_image(pygame.image.load("imgs/bluestone.png").convert(), False)

    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)

    gen_map()
    MAP = gen_map_grid(get_stationart())
    MAP_WIDTH = len(MAP)
    MAP_HEIGHT = len(MAP[0])
    start_pos = get_start_pos()
    player_coords = {'x': start_pos[0] + 0.5, 'y': start_pos[1] + 0.5}
    player_rotation = {'x': -1, 'y': 0}
    camera_plane = {'x': 0, 'y': 0.66}


    while running:
        display.fill((0, 0, 0))
        delta_time = 1 / clock.tick(60)

        input_handler(delta_time)
        ray_cast_better()
        render_hud()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit()
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        print(clock.get_fps())


init()