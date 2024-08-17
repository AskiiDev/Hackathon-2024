from mapgen import *
import pygame
import math

TEMP_WALL = [0, 2, 3, 4]

MAP_WIDTH = 0
MAP_HEIGHT = 0

HUD_OFFSET = 150
WIDTH = 800
HEIGHT = 600

HALF_PI = 1.57

RENDER_DISTANCE = 10
ACCURACY = 2
RAY_STEP_SIZE = 0.1

TEXTURE_WIDTH = 256
TEXTURE_HEIGHT = 256

running = True

pygame.init()
clock = pygame.time.Clock()
display = pygame.display.set_mode((WIDTH, HEIGHT))

player_coords = {'x': 2, 'y': 2}
player_rot = HALF_PI
player_rotation = {'x': 0, 'y': -1}

goal_coords = {}

FOV = HALF_PI / 2
WALK_SPEED = 2
TURN_SPEED = 0.003

MOVE_MAP = {pygame.K_w: 'w',
            pygame.K_s: 's',
            pygame.K_a: 'a',
            pygame.K_d: 'd',
            pygame.K_SPACE: 'space'}


arrow_images = {
    'n': pygame.transform.scale(pygame.image.load("imgs/arrow/arrow_n.png").convert_alpha(), (WIDTH, HEIGHT)),
    'ne': pygame.transform.scale(pygame.image.load("imgs/arrow/arrow_ne.png").convert_alpha(), (WIDTH, HEIGHT)),
    'e': pygame.transform.scale(pygame.image.load("imgs/arrow/arrow_e.png").convert_alpha(), (WIDTH, HEIGHT)),
    'se': pygame.transform.scale(pygame.image.load("imgs/arrow/arrow_se.png").convert_alpha(), (WIDTH, HEIGHT)),
    's': pygame.transform.scale(pygame.image.load("imgs/arrow/arrow_s.png").convert_alpha(), (WIDTH, HEIGHT)),
    'sw': pygame.transform.scale(pygame.image.load("imgs/arrow/arrow_sw.png").convert_alpha(), (WIDTH, HEIGHT)),
    'w': pygame.transform.scale(pygame.image.load("imgs/arrow/arrow_w.png").convert_alpha(), (WIDTH, HEIGHT)),
    'nw': pygame.transform.scale(pygame.image.load("imgs/arrow/arrow_nw.png").convert_alpha(), (WIDTH, HEIGHT)),
}


# -----------------------------------------------------------------------------------------------

def get_forward_vector(theta):
    return round(math.cos(theta), ACCURACY), round(math.sin(theta), ACCURACY)


def get_right_vector(theta):
    return round(math.cos(theta - HALF_PI), ACCURACY), round(math.sin(theta - HALF_PI), ACCURACY)


def try_move(vx, vy):
    dx = vx * WALK_SPEED
    dy = vy * WALK_SPEED

    player_coords['x'] += dx
    if MAP[int(player_coords['x'])][int(player_coords['y'])] in TEMP_WALL or \
       check_player_sprite_collision(player_coords['x'], player_coords['y']):
        if MAP[int(player_coords['x'])][int(player_coords['y'])] == 4:
            next_level()
            return
        player_coords['x'] -= dx

    player_coords['y'] += dy
    if MAP[int(player_coords['x'])][int(player_coords['y'])] in TEMP_WALL or \
       check_player_sprite_collision(player_coords['x'], player_coords['y']):
        if MAP[int(player_coords['x'])][int(player_coords['y'])] == 4:
            next_level()
            return
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
    player_rot += turn_delta

    old_player_rotation = player_rotation.copy()
    player_rotation['x'] = (
            old_player_rotation['x'] * math.cos(turn_delta) - old_player_rotation['y'] * math.sin(turn_delta))
    player_rotation['y'] = (
            old_player_rotation['x'] * math.sin(turn_delta) + old_player_rotation['y'] * math.cos(turn_delta))

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
    if 'space' in move:
        hitscan_fire(3)


# -----------------------------------------------------------------------------------------------


def load_image(image, darken, colorKey=None):
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
    return ret


def distance_fog(distance, scaled_texture):
    dark_surface = pygame.Surface(scaled_texture.get_size())
    dark_surface.fill((255 * distance, 255 * distance, 255 * distance))
    scaled_texture.blit(dark_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

    return scaled_texture


def ray_cast_better():
    global background
    global textures
    global sprites

    w = WIDTH
    h = HEIGHT - 150

    #if background is None:
    #background = pygame.transform.scale(pygame.image.load("imgs/bg.png").convert(), (w, h))

    #display.blit(background, (0, 0))

    z_buffer = []

    for x in range(w):
        camera_x = float(2 * x / float(w) - 1)
        ray_pos_x = player_coords['x']
        ray_pos_y = player_coords['y']
        ray_dir_x = player_rotation['x'] + camera_x * camera_plane['x']
        # print(ray_dir_x)
        ray_dir_y = player_rotation['y'] + camera_x * camera_plane['y']

        map_x = int(ray_pos_x)
        map_y = int(ray_pos_y)

        if ray_dir_x == 0:
            ray_dir_x = 0.00001
        d_dist_x = math.sqrt(1 + (ray_dir_y ** 2) / (ray_dir_x ** 2))
        if ray_dir_y == 0:
            ray_dir_y = 0.00001
        d_dist_y = math.sqrt(1 + (ray_dir_x ** 2) / (ray_dir_y ** 2))

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

            if (MAP[int(map_x)][int(map_y)] in TEMP_WALL) or math.sqrt(
                    (map_x - ray_pos_x) ** 2 + (map_y - ray_pos_y) ** 2) > 12:
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

        tex_num = MAP[map_x][map_y]

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

        if(side == 1):
            tex_num += 100

        if line_height > 10000:
            line_height = 10000
            draw_start = -5000 + h / 2
            draw_end = 5000 + h / 2

        A = max(1 - ((math.sqrt((map_x - ray_pos_x) ** 2 + (map_y - ray_pos_y) ** 2)) / 11), 0)
        # A = 1
        
        scaled_texture = distance_fog(A, pygame.transform.scale(textures[tex_num][tex_x], (1, line_height)))

        display.blit(scaled_texture, (x, draw_start))

        z_buffer.append(perp_wall_dist)

        # def sprite_compare(sprite1, sprite2):
        #     # Calculate the square of distances directly to avoid unnecessary sqrt computation
        #     sprite1_dist_sq = (sprite1.coords[0] - player_coords['x']) ** 2 + (sprite1.coords[1] - player_coords['y']) ** 2
        #     sprite2_dist_sq = (sprite2.coords[0] - player_coords['x']) ** 2 + (sprite2.coords[1] - player_coords['y']) ** 2

        #     # Direct comparison of squared distances2
        #     if sprite1_dist_sq > sprite2_dist_sq:
        #         return 1
        #     elif sprite1_dist_sq == sprite2_dist_sq:
        #         return 0
        #     else:
        #         return -1

        # To sort the list of sprites:

    def sprite_distance(sprite):
        # Calculate the distance from the player to the sprite
        return (sprite.coords[0] - player_coords['x']) ** 2 + (sprite.coords[1] - player_coords['y']) ** 2

    #Sort sprites by distance (farthest first)
    sprites.sort(key=sprite_distance, reverse=True)

    for sprite in sprites:
        #print(sprite)
        sprite_x = sprite.coords[0] + 0.5 - player_coords['x']
        sprite_y = sprite.coords[1] + 0.5 - player_coords['y']

        inv_det = 1.0 / (camera_plane['x'] * player_rotation['y'] - player_rotation['x'] * camera_plane['y'])

        transform_x = inv_det * (player_rotation['y'] * sprite_x - player_rotation['x'] * sprite_y)
        transform_y = inv_det * (-camera_plane['y'] * sprite_x + camera_plane['x'] * sprite_y)

        sprite_surface_x = int((w / 2) * (1 + transform_x / transform_y))

        sprite_height = abs(int(h / transform_y))
        draw_start_y = -sprite_height / 2 + h / 2
        draw_end_y = sprite_height / 2 + h / 2

        sprite_width = abs(int(h / transform_y))
        # print(sprite_surface_x)
        draw_start_x = int(- sprite_width / 2 + sprite_surface_x)
        draw_end_x = int(sprite_width / 2 + sprite_surface_x)

        #print(f"{draw_start_x}, {draw_end_x}")

        if sprite_height < 2000:
            for stripe in range(draw_start_x, draw_end_x):
                tex_x = int(
                    int(256 * (stripe - (- sprite_width / 2 + sprite_surface_x)) * sprite.res[0] / sprite_width) / 256)
                # print(f"hi {draw_start_x}")
                # print(f"{stripe}, {len(z_buffer)}")
                # print(tex_x)
                if stripe >= len(z_buffer) or stripe < 0:
                    continue
                if 0 < transform_y < z_buffer[stripe] and stripe < w:
                    A = min(sprite_height / 400, 1)

                    scaled_texture = distance_fog(A, pygame.transform.scale(sprite.texture[tex_x], (1, sprite_height)))
                    display.blit(scaled_texture,
                                 (stripe, draw_start_y))


def render_hud(delta):
    global player_coords
    global player_rot
    global goal_coords

    quantization_step = 1

    y_pos = int(3 * abs(math.sin(delta / 10)))

    # Function to calculate angle to goal
    def get_angle_to_goal(player_coords, goal_coords):
        dx = goal_coords[0] - (player_coords['x'])
        dy = goal_coords[1] - (player_coords['y'])
        return math.atan2(dy, dx)

    # Function to select arrow texture based on angle

    def get_arrow_texture(player_rot, angle_to_goal):
        angle_diff = (angle_to_goal - player_rot) % (2 * math.pi)

        # Determine the direction based on the angle difference
        if 0 <= angle_diff < math.pi / 8 or angle_diff > 15 * math.pi / 8:
            return arrow_images['e']
        elif math.pi / 8 <= angle_diff < 3 * math.pi / 8:
            return arrow_images['ne']
        elif 3 * math.pi / 8 <= angle_diff < 5 * math.pi / 8:
            return arrow_images['n']
        elif 5 * math.pi / 8 <= angle_diff < 7 * math.pi / 8:
            return arrow_images['nw']
        elif 7 * math.pi / 8 <= angle_diff < 9 * math.pi / 8:
            return arrow_images['w']
        elif 9 * math.pi / 8 <= angle_diff < 11 * math.pi / 8:
            return arrow_images['sw']
        elif 11 * math.pi / 8 <= angle_diff < 13 * math.pi / 8:
            return arrow_images['s']
        elif 13 * math.pi / 8 <= angle_diff < 15 * math.pi / 8:
            return arrow_images['se']
        else:
            return arrow_images['e']

    # Usage
    angle_to_goal = get_angle_to_goal(player_coords, goal_coords)
    arrow_texture = get_arrow_texture(-angle_to_goal, -player_rot)
    #print(angle_to_goal)
    arrow = pygame.transform.scale(arrow_texture, (WIDTH, HEIGHT))

    hud = pygame.transform.scale(pygame.image.load("imgs/HUD.png").convert_alpha(), (WIDTH, HEIGHT))

    y_pos = (y_pos // quantization_step) * quantization_step
    display.blit(hud, (0, 0))
    display.blit(arrow, (0, y_pos))


def render_weapon(delta):
    quantization_step = 6
    hand = pygame.transform.scale(pygame.image.load("imgs/weapons/fist.png").convert_alpha(), (WIDTH, HEIGHT))

    x_pos = int(15 * math.cos(delta / 10))
    y_pos = int(10 * abs(math.sin(delta / 10)))

    # Quantize the positions
    x_pos = (x_pos // quantization_step) * quantization_step
    y_pos = (y_pos // quantization_step) * quantization_step

    display.blit(hand, (x_pos, 20 + y_pos))

def hitscan_fire(range):
    # Initialize the ray starting at the player's position
    ray_pos_x = player_coords['x']
    ray_pos_y = player_coords['y']
    
    ray_dir_x = player_rotation['x']
    ray_dir_y = player_rotation['y']
    
    map_x = int(ray_pos_x)
    map_y = int(ray_pos_y)

    if ray_dir_x != 0:
        delta_dist_x = math.sqrt(1 + (ray_dir_y ** 2) / (ray_dir_x ** 2))
    else:
        delta_dist_x = float('inf')  # Infinite distance if ray_dir_x is 0

    if ray_dir_y != 0:
        delta_dist_y = math.sqrt(1 + (ray_dir_x ** 2) / (ray_dir_y ** 2))
    else:
        delta_dist_y = float('inf')  # Infinite distance if ray_dir_y is 0
    
    # Direction to go in x and y (+1 or -1)
    if ray_dir_x < 0:
        step_x = -1
        side_dist_x = (ray_pos_x - map_x) * delta_dist_x
    else:
        step_x = 1
        side_dist_x = (map_x + 1.0 - ray_pos_x) * delta_dist_x
    
    if ray_dir_y < 0:
        step_y = -1
        side_dist_y = (ray_pos_y - map_y) * delta_dist_y
    else:
        step_y = 1
        side_dist_y = (map_y + 1.0 - ray_pos_y) * delta_dist_y
    
    hit = False
    side = 0
    
    # Perform DDA (Digital Differential Analyzer) to step through the grid
    while not hit:
        if side_dist_x < side_dist_y:
            side_dist_x += delta_dist_x
            map_x += step_x
            side = 0
        else:
            side_dist_y += delta_dist_y
            map_y += step_y
            side = 1
        

        # Check if the ray has hit an enemy or wall
        if MAP[map_x][map_y] in TEMP_WALL:
            hit = True
            print("Hit a wall!")
        
        for sprite in sprites:
            sprite_x = int(sprite.coords[0]) 
            sprite_y = int(sprite.coords[1])
            
            if map_x == sprite_x and map_y == sprite_y:
                hit = True
                print(f"Hit {sprite}!")
                return(sprite)
        
        # print(side_dist_x)
        if (side_dist_x ** 2 + side_dist_y ** 2 > range ** 2):
            print("Missed!")
            return
    
    if not hit:
        print("Missed!")

def check_player_sprite_collision(player_x, player_y):
    for sprite in sprites:

        if not sprite.solid:
            continue  
        sprite_x, sprite_y = sprite.coords
        sprite_width, sprite_height = sprite.width, sprite.width

        # Check for overlap between player and sprite bounding boxes
        if (player_x < sprite_x + (0.5 + sprite_width) and
            player_x > sprite_x + (0.5 - sprite_width) and
            player_y < sprite_y + (0.5 + sprite_height) and
            player_y > sprite_y + (0.5 - sprite_height)):
            # handle_collision(sprite)  # Call a function to handle what happens on collision
            return True

    return False

def check_sprite_collision(sprite1, sprite2):
    # Check for overlap between player and sprite bounding boxes
    if (sprite1.coords[0] < sprite2.coords[0] + sprite2.width and
        sprite1.coords[0] + sprite1.width > sprite2.coords[0] and
        sprite1.coords[1] < sprite2.coords[1] + sprite2.width and
        sprite1.coords[1] + sprite1.width > sprite2.coords[1]):
        print(f"Collision detected!")
        sprite1.handle_collision(sprite2)
        sprite2.handle_collision(sprite1)
        return True

    return False

class Sprite:
    def __init__(self, coords, texture, res, width, health=1, solid=True, s_type='default'):
        self.coords = coords
        self.texture = texture
        self.res = res
        self.width = width
        self.health = health
        self.solid = solid
    
    def handle_collision(self, sprite):
        pass


def next_level():
    pass


def init():
    global running
    global player_coords
    global player_rotation
    global camera_plane
    global MAP
    global MAP_WIDTH
    global MAP_HEIGHT
    global background
    global textures
    global goal_coords
    global sprites

    frames = 0

    background = None
    textures = {0: load_image(pygame.image.load("imgs/wall.png").convert(), False), 
                1: load_image(pygame.image.load("imgs/wall.png").convert(), False), 
                2: load_image(pygame.image.load("imgs/wall.png").convert(), False), 
                3: load_image(pygame.image.load("imgs/closed_door.png").convert(), False),
                4: load_image(pygame.image.load("imgs/opened_door.png").convert(), False), 
                100: load_image(pygame.image.load("imgs/wall.png").convert(), True), 
                101: load_image(pygame.image.load("imgs/wall.png").convert(), True), 
                102: load_image(pygame.image.load("imgs/wall.png").convert(), True), 
                103: load_image(pygame.image.load("imgs/closed_door.png").convert(), True),
                104: load_image(pygame.image.load("imgs/opened_door.png").convert(), True)}
    
    # sprite_key = {4: Sprite((0,0), ())}

    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)

    gen_map()
    MAP = gen_map_grid(get_stationary())
    MAP_WIDTH = len(MAP)
    MAP_HEIGHT = len(MAP[0])
    start_pos = get_start_pos()
    player_coords = {'x': start_pos[0] + 0.5, 'y': start_pos[1] + 0.5}
    goal_coords = get_real_end_pos()
    player_rotation = {'x': -1, 'y': 0}
    camera_plane = {'x': 0, 'y': 0.66}

    sprites = []
    # end_trigger = Sprite(goal_coords, load_image(pygame.image.load("imgs/barrel.png").convert(), False, colorKey=(0, 0, 0)), (64, 64), 0.6, s_type='goal', solid=False)
    # sprites.append(end_trigger)

    gobbo = Sprite((start_pos[0] - 1, start_pos[1] + 0),
                   load_image(pygame.image.load("imgs/barrel.png").convert(), False, colorKey=(0, 0, 0)), (64, 64), 0.4)
    gobbo2 = Sprite((start_pos[0] - 1.6, start_pos[1] + 0),
                   load_image(pygame.image.load("imgs/barrel.png").convert(), False, colorKey=(0, 0, 0)), (64, 64), 0.5)
    sprites.append(gobbo)
    print(gen_map_grid(get_stationary()))

    # sprites.append(gobbo2)

    # check_sprite_collision(gobbo, gobbo2)

    last_pos = start_pos

    while running:
        frames += 1
        display.fill((0, 0, 0))
        delta_time = 1 / clock.tick(60)

        input_handler(delta_time)
        ray_cast_better()
        render_weapon(frames)
        render_hud(frames)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit()
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        # print(clock.get_fps())


init()
