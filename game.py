from mapgen import *
import pygame
import math
import time


STATE = "MENU"

TEMP_WALL = [0, 2, 3, 4]

hands_y = 0
lower_hand = False
new_spell = "punch"

damage_frames = 0
agg = []

player_health = 100
sprites = []
barrels = []

HANDS_LOWER_LIMIT = 600
elapsed_time = 0

held_spell = "punch"
anim_frames = 0

MAP_WIDTH = 0
MAP_HEIGHT = 0

level = 1
level_start_time = 0

HUD_OFFSET = 150
WIDTH = 800
HEIGHT = 600

HALF_PI = 1.57

ACCURACY = 2
RAY_STEP_SIZE = 0.1

TEXTURE_WIDTH = 256
TEXTURE_HEIGHT = 256

souls = 0
pills = 0


running = True

pygame.init()
pygame.font.init()
pygame.mixer.init()

FONTS = {
    'floor': pygame.font.Font("almendra/Almendra-Regular.ttf", 40),
    'floor_n': pygame.font.Font("almendra/Almendra-Regular.ttf", 40),
    'timer': pygame.font.Font("almendra/Almendra-Regular.ttf", 40),
    'health': pygame.font.Font("almendra/Almendra-Regular.ttf", 40)
}


STAGE_TRACKS = ["music/strange_people.mp3", "music/wave_of_fiends.mp3", "music/goblin_guts.mp3", "music/guitar_wizard.mp3"]
# STAGE_TRACKS = ["music/wave_of_fiends.mp3", "music/goblin_guts.mp3"]

SFX = {
    'shut': pygame.mixer.Sound("sfx/door_shut.wav"),
    'open': pygame.mixer.Sound("sfx/door_open.wav"),
    'barrel': pygame.mixer.Sound("sfx/break_barrel.wav"),
    'squelch': pygame.mixer.Sound("sfx/squelch.wav")
}

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

faces = {
    'healthy': pygame.transform.scale(pygame.image.load("imgs/faces/healthy.png").convert_alpha(), (WIDTH, HEIGHT)),
    'neutral': pygame.transform.scale(pygame.image.load("imgs/faces/neutral.png").convert_alpha(), (WIDTH, HEIGHT)),
    'hurt': pygame.transform.scale(pygame.image.load("imgs/faces/hurt.png").convert_alpha(), (WIDTH, HEIGHT))
}

hud = pygame.transform.scale(pygame.image.load("imgs/HUD.png").convert_alpha(), (WIDTH, HEIGHT))

punch = {0: (pygame.transform.scale(pygame.image.load("imgs/attacks/punch/fist2.png").convert_alpha(), (WIDTH, HEIGHT)), 4),
         1: (pygame.transform.scale(pygame.image.load("imgs/attacks/punch/fist3.png").convert_alpha(), (WIDTH, HEIGHT)), 4),
         2: (pygame.transform.scale(pygame.image.load("imgs/attacks/punch/fist4.png").convert_alpha(), (WIDTH, HEIGHT)), 9),
         3: (pygame.transform.scale(pygame.image.load("imgs/attacks/punch/fist3.png").convert_alpha(), (WIDTH, HEIGHT)), 5),
         4: (pygame.transform.scale(pygame.image.load("imgs/attacks/punch/fist2.png").convert_alpha(), (WIDTH, HEIGHT)), 14)}


fireball = {0: (pygame.transform.scale(pygame.image.load("imgs/attacks/fireball/fireball1.png").convert_alpha(), (WIDTH, HEIGHT)), 4),
            1: (pygame.transform.scale(pygame.image.load("imgs/attacks/fireball/fireball2.png").convert_alpha(), (WIDTH, HEIGHT)), 8),
            2: (pygame.transform.scale(pygame.image.load("imgs/attacks/fireball/fireball3.png").convert_alpha(), (WIDTH, HEIGHT)), 4),
            3: (pygame.transform.scale(pygame.image.load("imgs/attacks/fireball/fireball4.png").convert_alpha(), (WIDTH, HEIGHT)), 10)}


lightning = {0: (pygame.transform.scale(pygame.image.load("imgs/attacks/lightning/lightning1.png").convert_alpha(), (WIDTH, HEIGHT)), 1),
             1: (pygame.transform.scale(pygame.image.load("imgs/attacks/lightning/lightning2.png").convert_alpha(), (WIDTH, HEIGHT)), 1),
             2: (pygame.transform.scale(pygame.image.load("imgs/attacks/lightning/lightning3.png").convert_alpha(), (WIDTH, HEIGHT)), 2),
             3: (pygame.transform.scale(pygame.image.load("imgs/attacks/lightning/lightning4.png").convert_alpha(), (WIDTH, HEIGHT)), 4),
             4: (pygame.transform.scale(pygame.image.load("imgs/attacks/lightning/lightning5.png").convert_alpha(), (WIDTH, HEIGHT)), 8),
             5: (pygame.transform.scale(pygame.image.load("imgs/attacks/lightning/lightning4.png").convert_alpha(), (WIDTH, HEIGHT)), 4),
             6: (pygame.transform.scale(pygame.image.load("imgs/attacks/lightning/lightning5.png").convert_alpha(), (WIDTH, HEIGHT)), 4),
             7: (pygame.transform.scale(pygame.image.load("imgs/attacks/lightning/lightning4.png").convert_alpha(), (WIDTH, HEIGHT)), 4),
             8: (pygame.transform.scale(pygame.image.load("imgs/attacks/lightning/lightning3.png").convert_alpha(), (WIDTH, HEIGHT)), 2),
             9: (pygame.transform.scale(pygame.image.load("imgs/attacks/lightning/lightning4.png").convert_alpha(), (WIDTH, HEIGHT)), 4),
             10: (pygame.transform.scale(pygame.image.load("imgs/attacks/lightning/lightning3.png").convert_alpha(), (WIDTH, HEIGHT)), 2),
             11: (pygame.transform.scale(pygame.image.load("imgs/attacks/lightning/lightning2.png").convert_alpha(), (WIDTH, HEIGHT)), 1),
             12: (pygame.transform.scale(pygame.image.load("imgs/attacks/lightning/lightning1.png").convert_alpha(), (WIDTH, HEIGHT)), 1)}

ATTACKS = {
    "punch": punch,
    "fireball": fireball,
    "lightning": lightning
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
            print("next")
            next_level()
            return
        player_coords['x'] -= dx


    player_coords['y'] += dy
    if MAP[int(player_coords['x'])][int(player_coords['y'])] in TEMP_WALL or \
       check_player_sprite_collision(player_coords['x'], player_coords['y']):
        if MAP[int(player_coords['x'])][int(player_coords['y'])] == 4:
            print("next")
            next_level()
            return
        player_coords['y'] -= dy


def try_move_forward(delta, fv):
    fvx, fvy = player_rotation['x'], player_rotation['y']
    try_move(delta * fvx * fv, delta * fvy * fv)


def try_move_right(delta, rv):
    rvx, rvy = -player_rotation['y'], player_rotation['x']
    try_move(delta * rvx * rv, delta * rvy * rv)


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


# -----------------------------------------------------------------------------------------------


def load_image(image, darken, colorKey=None):
    ret = []
    # Convert the image to include alpha transparency
    image = image.convert_alpha()

    for i in range(image.get_width()):
        s = pygame.Surface((1, image.get_height()), pygame.SRCALPHA).convert_alpha()
        s.blit(image, (-i, 0))

        # If a color key is provided, set it as transparent
        if colorKey is not None:
            s.set_colorkey(colorKey)

        # Apply darkening effect if specified
        if darken:
            # Darken only the non-transparent parts
            for y in range(s.get_height()):
                for x in range(s.get_width()):
                    pixel = s.get_at((x, y))
                    if pixel.a != 0:  # If pixel is not fully transparent
                        s.set_at((x, y), pixel)

        ret.append(s)

    return ret


textures = {
    0: load_image(pygame.image.load("imgs/wall.png").convert(), False),
    1: load_image(pygame.image.load("imgs/wall.png").convert(), False),
    2: load_image(pygame.image.load("imgs/wall.png").convert(), False),
    3: load_image(pygame.image.load("imgs/closed_door.png").convert(), False),
    4: load_image(pygame.image.load("imgs/opened_door.png").convert(), False),
    100: load_image(pygame.image.load("imgs/wall.png").convert(), True),
    101: load_image(pygame.image.load("imgs/wall.png").convert(), True),
    102: load_image(pygame.image.load("imgs/wall.png").convert(), True),
    103: load_image(pygame.image.load("imgs/closed_door.png").convert(), True),
    104: load_image(pygame.image.load("imgs/opened_door.png").convert(), True)
}

ghost_images = {
    0: load_image(pygame.image.load("imgs/enemies/ghost/A3.png").convert_alpha(), False),
    1: load_image(pygame.image.load("imgs/enemies/ghost/A4.png").convert_alpha(), False),
    2: load_image(pygame.image.load("imgs/enemies/ghost/A5.png").convert_alpha(), False),
    "die1": load_image(pygame.image.load("imgs/enemies/ghost/GHDying1.png").convert_alpha(), False),
    "die2": load_image(pygame.image.load("imgs/enemies/ghost/GHDying2.png").convert_alpha(), False)
}

goblin_images = {
    0: load_image(pygame.image.load("imgs/enemies/goblin/A1.png").convert_alpha(), False),
    1: load_image(pygame.image.load("imgs/enemies/goblin/A2.png").convert_alpha(), False),
    2: load_image(pygame.image.load("imgs/enemies/goblin/A3.png").convert_alpha(), False),
    3: load_image(pygame.image.load("imgs/enemies/goblin/A4.png").convert_alpha(), False),
    4: load_image(pygame.image.load("imgs/enemies/goblin/A5.png").convert_alpha(), False),
    5: load_image(pygame.image.load("imgs/enemies/goblin/A6.png").convert_alpha(), False),
    6: load_image(pygame.image.load("imgs/enemies/goblin/A7.png").convert_alpha(), False),
    7: load_image(pygame.image.load("imgs/enemies/goblin/A8.png").convert_alpha(), False),
    "die1": load_image(pygame.image.load("imgs/enemies/goblin/GDying1.png").convert_alpha(), False),
    "die2": load_image(pygame.image.load("imgs/enemies/goblin/GDying2.png").convert_alpha(), False)
}

ogre_images = {
    0: load_image(pygame.image.load("imgs/enemies/ogre/F1.png").convert_alpha(), False),
    1: load_image(pygame.image.load("imgs/enemies/ogre/F2.png").convert_alpha(), False),
    2: load_image(pygame.image.load("imgs/enemies/ogre/F3.png").convert_alpha(), False),
    3: load_image(pygame.image.load("imgs/enemies/ogre/F4.png").convert_alpha(), False),
    4: load_image(pygame.image.load("imgs/enemies/ogre/F5.png").convert_alpha(), False),
    5: load_image(pygame.image.load("imgs/enemies/ogre/F6.png").convert_alpha(), False),
    6: load_image(pygame.image.load("imgs/enemies/ogre/F7.png").convert_alpha(), False),
    7: load_image(pygame.image.load("imgs/enemies/ogre/F8.png").convert_alpha(), False),
    "die1": load_image(pygame.image.load("imgs/enemies/ogre/ODying1.png").convert_alpha(), False),
    "die2": load_image(pygame.image.load("imgs/enemies/ogre/ODying2.png").convert_alpha(), False)
}

ogre_anim = []

ogre_anim += [ogre_images[0]] * 4
ogre_anim += [ogre_images[1]] * 5
ogre_anim += [ogre_images[2]] * 5
ogre_anim += [ogre_images[3]] * 1
ogre_anim += [ogre_images[4]] * 1
ogre_anim += [ogre_images[5]] * 1
ogre_anim += [ogre_images[6]] * 1
ogre_anim += [ogre_images[7]] * 3
ogre_anim += [ogre_images[6]] * 10
ogre_anim += [ogre_images[5]] * 6
ogre_anim += [ogre_images[4]] * 5
ogre_anim += [ogre_images[3]] * 4
ogre_anim += [ogre_images[2]] * 3
ogre_anim += [ogre_images[1]] * 3
ogre_anim += [ogre_images[0]] * 3

gore_pile = load_image(pygame.image.load("imgs/enemies/gorepile.png").convert_alpha(), False)

fireball_proj = load_image(pygame.image.load("imgs/attacks/fireball/fireball_proj.png"), False)

barrel_img = load_image(pygame.image.load("imgs/props/barrel.png"), False)
barrel_destroyed_img = load_image(pygame.image.load("imgs/props/barrel_destroyed.png"), False)

fireball_powerup = load_image(pygame.image.load("imgs/powerups/whiskey.png"), False)
lightning_powerup = load_image(pygame.image.load("imgs/powerups/car_battery.png"), False)


def distance_fog(distance, scaled_texture):
    dark_surface = pygame.Surface(scaled_texture.get_size())
    dark_surface.fill((255 * distance, 255 * distance, 255 * distance))
    scaled_texture.blit(dark_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

    return scaled_texture


def ray_cast_better():
    global background
    
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

        if transform_y == 0:
            transform_y = 0.00000001
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
                    if sprite.s_type != "proj":
                        A = min(sprite_height / 400, 1)
                    else:
                        A = 1

                    scaled_texture = distance_fog(A, pygame.transform.scale(sprite.texture[tex_x], (1, sprite_height)))
                    display.blit(scaled_texture,
                                 (stripe, draw_start_y))


def render_hud(delta):
    global player_coords
    global level
    global level_start_time
    global player_rot
    global player_health
    global goal_coords
    global elapsed_time
    global souls
    global pills

    quantization_step = 1

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
    arrow_texture = get_arrow_texture(-angle_to_goal, -math.atan2(-player_rotation['x'], player_rotation['y']))

    arrow = pygame.transform.scale(arrow_texture, (WIDTH, HEIGHT))

    y_pos = int(3 * abs(math.sin(delta / 10)))
    y_pos = (y_pos // quantization_step) * quantization_step

    face_y_pos = int(2 * abs(math.sin(delta / 20)))
    face_y_pos = (face_y_pos // quantization_step) * quantization_step

    display.blit(hud, (0, 0))
    display.blit(arrow, (0, 20 + y_pos))

    if player_health >= 60:
        face = "healthy"
    if 60 > player_health >= 30:
        face = "neutral"
    elif player_health < 30:
        face = "hurt"

    display.blit(faces[face], (0, face_y_pos))

    elapsed_time = int(time.time() - level_start_time)
    minutes, seconds = divmod(elapsed_time, 60)

    floor_title = FONTS['floor'].render("SOULS", True, (255, 255, 255))
    timer_title = FONTS['timer'].render("TIMER", True, (255, 255, 255))
    health_title = FONTS['timer'].render("HP", True, (255, 255, 255))
    pills_title = FONTS['timer'].render("PILLS", True, (255, 255, 255))
    health_counter = FONTS['floor_n'].render(f"{player_health}", True, (200, 200, 200))
    floor_counter = FONTS['floor_n'].render(f"{souls}", True, (200, 200, 200))
    timer_counter = FONTS['floor_n'].render(f"{minutes}:{seconds:02}", True, (200, 200, 200))
    pills_counter = FONTS['floor_n'].render(f"{pills}", True, (200, 200, 200))

    display.blit(floor_title, (48.5, 475))
    display.blit(timer_title, (195.5, 475))
    display.blit(health_title, (523, 475))
    display.blit(pills_title, (649, 475))
    display.blit(health_counter, (520, 520))
    display.blit(floor_counter, (98.5, 520))
    display.blit(timer_counter, (220, 520))
    display.blit(pills_counter, (649, 520))


def render_weapon(weapon_state, delta):
    global anim_frames
    global hands_y
    quantization_step = 6

    x_pos = int(15 * math.cos(delta / 10))
    y_pos = int(10 * abs(math.sin(delta / 10)))

    # Quantize the positions
    x_pos = (x_pos // quantization_step) * quantization_step
    y_pos = (y_pos // quantization_step) * quantization_step

    display.blit(weapon_state, (x_pos, hands_y + y_pos))


def fire(max_distance):
    # Get player's position and direction
    player_x, player_y = player_coords['x'], player_coords['y']

    # Calculate the direction vector of the fire based on player_angle
    fire_dx = player_rotation['x']
    fire_dy = player_rotation['y']

    # Maximum distance the bullet can travel
    # max_distance = 20  # Adjust as needed

    for dist in range(max_distance):
        # Calculate the current point along the fire's path
        fire_x = player_x + fire_dx * dist / 2
        fire_y = player_y + fire_dy * dist / 2

        # Check if this point hits any sprite
        for sprite in sprites:
            sprite_x, sprite_y = sprite.coords
            sprite_width, sprite_height = sprite.width, sprite.width

            # Check for collision with sprite's bounding box
            if (sprite_x + (0.5 - sprite_width) < fire_x < sprite_x + (0.5 + sprite_width) and
                sprite_y+ (0.5 - sprite_width) < fire_y < sprite_y + (0.5 + sprite_width)):
                print(f"Hit detected on sprite at {sprite.coords} after {dist} units")
                sprite.handle_hit()  # Call a function to handle the hit
                return

        # Optionally, check if the bullet hits a wall or other obstacle in the map
        if MAP[int(fire_x)][int(fire_y)] in TEMP_WALL:
            print(f"Bullet hit a wall at {int(fire_x)}, {int(fire_y)} after {dist} units")
            return

    print("No hit detected.")



def get_random_location_near_player(radius1, radius):
    global agg
    global MAP
    global player_coords

    grid = MAP

    player_x, player_y = (int(player_coords['x']), int(player_coords['y']))
    valid_locations = []

    for x in range(max(0, player_x - radius), min(grid.shape[0], player_x + radius + 1)):
        for y in range(max(0, player_y - radius), min(grid.shape[1], player_y + radius + 1)):
            if grid[x, y] == 1:  # Check if it's a floor tile
                if (x, y) not in agg:  # Check if it's not occupied
                    distance = math.sqrt((x - player_x) ** 2 + (y - player_y) ** 2)
                    if radius1 <= distance <= radius:
                        valid_locations.append((x, y))

    if valid_locations:
        return random.choice(valid_locations)
    else:
        return None

def spawn_monster():
    global sprites
    location = get_random_location_near_player(10, 15)
    option = random.randint(0, 2)

    if option == 0:
        sprites.append(Sprite(location, ghost_images[0], (256, 256), 0.3, s_type="ghost", solid=False))
    if option == 1:
        sprites.append(Sprite(location, goblin_images[0], (256, 256), 0.3, s_type="goblin"))
    if option == 2:
        sprites.append(Sprite(location, ogre_images[0], (256, 256), 0.5, s_type="ogre"))
    
    # print(option)


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
            sprite.hit_player()  # Call a function to handle what happens on collision
            # print("HI")
            return True

    return False

def check_sprite_collision(sprite1, sprite2):
    # Check for overlap between player and sprite bounding boxes
    if (sprite1.coords[0] < sprite2.coords[0] + sprite2.width and
        sprite1.coords[0] + sprite1.width > sprite2.coords[0] and
        sprite1.coords[1] < sprite2.coords[1] + sprite2.width and
        sprite1.coords[1] + sprite1.width > sprite2.coords[1]):

        # print(f"Collision detected!")
        sprite1.handle_collision(sprite2)
        sprite2.handle_collision(sprite1)
        #print("test")
        return True

    return False

class Sprite:
    global sprites
    global anim_frames
    global player_health
    global lower_hand
    global new_spell
    global souls

    def __init__(self, coords, texture, res, width, health=1, invulnerable=False, solid=True, s_type='default', speed=0, dir=(0,0)):
        self.coords = coords
        self.texture = texture
        self.res = res
        self.width = width
        self.health = health
        self.solid = solid
        self.s_type = s_type
        self.mark_for_death = 0
        self.speed  = speed
        self.dir = dir
        self.invulnerable = invulnerable

        self.attacking = False
        self.prev_anim_frame = 0
        self.frame = 0

    def handle_collision(self, sprite):
        if sprite.s_type == "proj":
            self.get_hit()

            #print("test")

    def get_hit(self):
        if self.s_type == "barrel":
            if self.texture == barrel_destroyed_img:
                return
            self.texture = barrel_destroyed_img
            pygame.mixer.Sound.play(SFX['barrel'])
            self.solid = False
            self.width = 0
            pu = random.randint(0,1)
            if pu == 0:
                sprites.append(Sprite(self.coords, fireball_powerup, (256,256), 0.1, s_type="fireball_pu", invulnerable=True))
            if pu == 1:
                sprites.append(Sprite(self.coords, lightning_powerup, (256,256), 0.1, s_type="lightning_pu", invulnerable=True))
            return
        if self.invulnerable:
            return
        if not self.mark_for_death:
            self.died = True
            self.mark_for_death = 20

    def handle_hit(self):
        self.get_hit()

    def hit_player(self):
        global player_health
        global lower_hand
        global new_spell

        if self.s_type == "lightning_pu":
            new_spell = "lightning"
            lower_hand = True
            sprites.remove(self)

        if self.s_type == "fireball_pu":
            new_spell = "fireball"
            lower_hand = True
            sprites.remove(self)


    def simulate(self):
        global player_health
        global sprites
        global souls 

        if self.mark_for_death == 1:
            sprites.append(Sprite((self.coords), gore_pile, (256, 256), 0.1,  invulnerable=True, s_type = 'gore pile'))
            pygame.mixer.Sound.play(SFX['squelch'])
            self.texture = gore_pile
            sprites.remove(self)
            souls += 1

        elif self.mark_for_death > 1:
            if self.mark_for_death <= 10:
                if self.s_type == "goblin":
                    self.texture = goblin_images["die2"]
                elif self.s_type == "ghost":
                    self.texture = ghost_images["die2"]
                elif self.s_type == "ogre":
                    self.texture = ogre_images["die2"]

            elif self.mark_for_death <= 20:
                if self.s_type == "goblin":
                    self.texture = goblin_images["die1"]
                elif self.s_type == "ghost":
                    self.texture = ghost_images["die1"]
                elif self.s_type == "ogre":
                    self.texture = ogre_images["die1"]
                
            self.mark_for_death -= 1

        else:
            if self.s_type == "proj":
                self.coords = (self.coords[0] + self.dir[0] * self.speed,  self.coords[1] + self.dir[1] * self.speed)

                if MAP[int(self.coords[0] + 0.5)][int(self.coords[1] + 0.5)] in TEMP_WALL:
                    sprites.remove(self)
                
                player_x, player_y = player_coords['x'] - 0.5, player_coords['y'] - 0.5
                x, y = self.coords

                direction_x = player_x - x
                direction_y = player_y - y

                distance = math.sqrt(direction_x ** 2 + direction_y ** 2)

                if distance < 0.3:        
                    damage_player(9)
                    sprites.remove(self)

                for i in sprites:
                    if i.s_type != "proj":
                        check_sprite_collision(self, i)

            if self.s_type == "ghost":
                self.texture = ghost_images[int(anim_frames / 10) % 3]

                player_x, player_y = player_coords['x'] - 0.5, player_coords['y'] - 0.5
                ghost_x, ghost_y = self.coords

                    # Calculate the direction vector from the ghost to the player
                direction_x = player_x - ghost_x
                direction_y = player_y - ghost_y

                    # Normalize the direction vector to get a unit vector
                distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
                if distance != 0:
                    direction_x /= distance
                    direction_y /= distance

                    # Set the speed at which the ghost moves towards the player
                ghost_speed = 0.02  # Adjust this value for desired speed

                    # Update the ghost's position to move along the direction vector
                if distance >= 0.35:
                    ghost_x += direction_x * ghost_speed
                    ghost_y += direction_y * ghost_speed
                    self.coords = (ghost_x, ghost_y)

                else:
                    damage_player(1)

                
            if self.s_type == "goblin":
                if not self.attacking:
                    self.texture = goblin_images[0]
                    player_x, player_y = player_coords['x'], player_coords['y']
                    goblin_x, goblin_y = self.coords

                    # Calculate the direction vector and distance from the goblin to the player
                    direction_x = player_x - goblin_x
                    direction_y = player_y - goblin_y
                    distance = math.hypot(direction_x, direction_y)

                    if distance > 0:
                        direction_x /= distance
                        direction_y /= distance

                    goblin_speed = 0.03

                    mx = False
                    my = False

                    if distance < 3 or distance > 4:
                        move_factor = -goblin_speed if distance < 3 else goblin_speed

                        new_x = goblin_x + direction_x * move_factor

                        if not (MAP[int(new_x + 0.5 - self.width)][int(goblin_y + 0.5 - self.width)] in TEMP_WALL or
                                MAP[int(new_x + 0.5 + self.width)][int(goblin_y + 0.5 + self.width)] in TEMP_WALL):
                            goblin_x = new_x
                            mx = True
                        
                        new_y = goblin_y + direction_y * move_factor
                            
                        if not (MAP[int(goblin_x + 0.5 - self.width)][int(new_y + 0.5 - self.width)] in TEMP_WALL or
                                MAP[int(goblin_x + 0.5 + self.width)][int(new_y + 0.5 + self.width)] in TEMP_WALL):
                            goblin_y = new_y
                            mx = True

                        self.coords = (goblin_x, goblin_y)

                    if not (mx or my): # only try to fire if 3-4 units away from player, or if in corner
                        self.attacking = True # start attack anim
                        self.frame = 0
                else:
                    if anim_frames != self.prev_anim_frame:
                        self.frame += 1
                        if self.frame < 8:
                            self.texture = goblin_images[self.frame]

                        if self.frame == 6:
                            direction_x = player_coords['x'] - 0.5 - self.coords[0]
                            direction_y = player_coords['y'] - 0.5 - self.coords[1]
                            distance = math.hypot(direction_x, direction_y)

                            if distance > 0:
                                direction_x /= distance
                                direction_y /= distance

                            projectile = (Sprite((self.coords[0] + (0.5 * direction_x), self.coords[1] + (0.5 * direction_y)), 
                                                 fireball_proj, (256,256), 0.1, solid=False, invulnerable=True, 
                                                 speed=0.1, dir=(direction_x, direction_y), s_type="proj"))
                            sprites.append(projectile)
                        
                        if self.frame >= 8:
                            self.texture = goblin_images[0]
                        
                        if self.frame == 12: # amount of 'recovery' frames for the attack
                            self.attacking = False

            if self.s_type == "ogre":
                if not self.attacking:
                    self.texture = ogre_images[0]
                    player_x, player_y = player_coords['x'] - 0.5, player_coords['y'] - 0.5
                    ogre_x, ogre_y = self.coords

                    # Calculate the direction vector and distance from the goblin to the player
                    direction_x = player_x - ogre_x
                    direction_y = player_y - ogre_y
                    distance = math.hypot(direction_x, direction_y)

                    if distance > 0:
                        direction_x /= distance
                        direction_y /= distance

                    ogre_speed = 0.03

                    mx = False
                    my = False


                    new_x = ogre_x + direction_x * ogre_speed

                    if not (MAP[int(new_x + 0.5 - self.width)][int(ogre_y + 0.5 - self.width)] in TEMP_WALL or
                            MAP[int(new_x + 0.5 + self.width)][int(ogre_y + 0.5 + self.width)] in TEMP_WALL):
                        ogre_x = new_x
                        mx = True
                    
                    new_y = ogre_y + direction_y * ogre_speed
                            
                    if not (MAP[int(ogre_x + 0.5 - self.width)][int(new_y + 0.5 - self.width)] in TEMP_WALL or
                            MAP[int(ogre_x + 0.5 + self.width)][int(new_y + 0.5 + self.width)] in TEMP_WALL):
                        ogre_y = new_y
                        mx = True

                    self.coords = (ogre_x, ogre_y)

                    if distance < 0.6:
                        self.attacking = True

                        self.has_damaged = False
                        self.frame = 0

                else:
                    if anim_frames != self.prev_anim_frame:
                        self.frame += 1
                        if self.frame <= len(ogre_anim) - 1:
                            self.texture = ogre_anim[self.frame]

                        if self.frame >= len(ogre_anim) - 1:
                            self.frame = 0
                            self.texture = ogre_images[0]
                            self.attacking = False
                            self.has_damaged = False

                        if ogre_anim[self.frame] == ogre_images[6] and not self.has_damaged:
                            self.has_damaged = True
                            direction_x = player_coords['x'] + 0.5 - self.coords[0]
                            direction_y = player_coords['y'] + 0.5 - self.coords[1]
                            distance = math.hypot(direction_x, direction_y)

                            if distance < 1:
                                damage_player(40)

        self.prev_anim_frame = anim_frames



def damage_player(amount):
    global player_health
    global damage_frames
    global score

    damage_frames += amount
    player_health = max(0, player_health - amount)
    if player_health == 0:
        display.fill((0,0,0))
        
        text_surface = FONTS['floor'].render("GAME OVER", False, (255,0,0))
        text_surface1 = FONTS['floor'].render(f"YOU SCORED {score}", False, (255,255,255))
        text_surface2 = FONTS['floor'].render("Press SPACE to return to menu.", False, (255,255,255))
        display.blit(text_surface, (20,20))
        display.blit(text_surface1, (20,60))
        display.blit(text_surface2, (20,100))


        pygame.display.flip()
        

        temp = True
        while temp:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        init()

def next_level():
    global total_score
    global elapsed_time
    global level
    global MAP
    global pills
    global souls

    total_score += 1000 - min(max(elapsed_time - 20, 0) * 40, 1000)
    
    
    display.blit(pygame.image.load("imgs/props/Merchant_Screen.png"), (0,0))

    
    text_surface = FONTS['floor'].render("Press B to buy", False, (255,255,255))
    text_surface2 = FONTS['floor'].render("Press SPACE to Leave", False, (255,255,255))
    display.blit(text_surface, (20,20))
    display.blit(text_surface2, (20,60))


    pygame.display.flip()
    

    temp = True
    while temp:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    if souls >= 10:
                        pills += 1
                        souls -= 10
                if event.key == pygame.K_SPACE:
                    temp = False
                    break

    render_hud(0)
    print("Score:")
    print(score)
    print("Total:")
    print(total_score)
    pygame.display.flip()

    # pygame.time.wait(1000)
    display.fill(pygame.Color(0,0,0))
    render_hud(0)

    gen_map(display)
    pygame.display.flip()

    level += 1
    load_level()


def load_level():
    global running
    global player_coords
    global level_start_time
    global player_rotation
    global camera_plane
    global MAP
    global MAP_WIDTH
    global MAP_HEIGHT
    global background
    
    global goal_coords
    global sprites
    global score
    global player_health

    global barrels

    player_health = 100

    score = 0
    background = None

    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)

    MAP = gen_map_grid(get_stationary())


    MAP_WIDTH = len(MAP)
    MAP_HEIGHT = len(MAP[0])
    start_pos = get_start_pos()
    player_coords = {'x': start_pos[0] + 0.5, 'y': start_pos[1] + 0.5}
    goal_coords = get_real_end_pos()
    player_rotation = {'x': -1, 'y': 0}
    camera_plane = {'x': 0, 'y': 0.66}

    
    gen_barrels()
    barrels = get_barrels()
    if (start_pos in barrels):
        barrels.remove(start_pos)
    # print(barrels)


    # pygame.time.wait(1000)
    level_start_time = time.time()

    sprites = []

    last_pos = start_pos


def init():
    global running
    global total_score
    global level
    global sprites
    global MAP
    global frames
    global anim_frames
    global player_health
    global barrels
    global hands_y
    global held_spell
    global lower_hand
    global agg
    global new_spell
    global damage_frames
    global souls
    

    display.fill((0,0,0))
    text_surface = FONTS['floor'].render("Start game: \n Press space.", False, (255,255,255))
    display.blit(text_surface, (20,20))
    menu = True
    pygame.display.flip()
    while menu:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    menu = False
                    break
        
    


    can_attack = True
    lower_hand = False
    raise_hand = False
    attack = False

    new_spell = "punch"
    held_spell = "punch"

    total_score = 0
    level = 1

    player_health = 100

    gen_map(display)
    frames = 0
    
    agg = []

    current_anim_frame = 0
    anim_counter = 0

    load_level()

    for i in range(level):
        spawn_monster()
    
    # pygame.mixer.music.play()
            
    while running:

        if frames % 300 == 0:
            for i in range(level):
                spawn_monster()

        frames += 1
        anim_frames = int(frames / 2)
        display.fill((0, 0, 0))
        delta_time = 1 / clock.tick(60)

        # print(held_spell)

        if attack:
            if frames - anim_counter >= ATTACKS[held_spell][current_anim_frame][1]:
                current_anim_frame += 1
                if current_anim_frame >= len(ATTACKS[held_spell]):
                    if held_spell != "punch":
                        attack = False
                        lower_hand = True
                        can_attack = False
                        new_spell = "punch"

                        if held_spell == "fireball":                            
                            sprites.append(Sprite((player_coords['x'] - 0.5 + (0.5 * player_rotation['x']), player_coords['y'] - 0.5 + (0.5 * player_rotation['y'])), 
                                                  fireball_proj, (256,256), 0.1, solid=False, invulnerable=True, 
                                                  speed=0.2, dir=(player_rotation['x'],player_rotation['y']), s_type="proj"))
                            # pass

                    else:
                        attack = False
                        current_anim_frame = 0
                else:
                    anim_counter = frames
                    current_weapon_state = ATTACKS[held_spell][current_anim_frame][0]
                    if held_spell == "punch" and current_anim_frame == 1:
                        fire(3)
                    if held_spell == "lightning" and current_anim_frame == 3:
                        for i in sprites:
                            if math.hypot(player_coords['x'] - i.coords[0], player_coords['y'] - i.coords[1]) < 2:
                                i.get_hit()
            
        elif can_attack:
            current_weapon_state = ATTACKS[held_spell][0][0]

        if lower_hand and hands_y < HANDS_LOWER_LIMIT and not attack:
            can_attack = False
            hands_y += 30
            if hands_y >= HANDS_LOWER_LIMIT:
                lower_hand = False
                raise_hand = True
                held_spell = new_spell
                current_weapon_state = ATTACKS[held_spell][0][0]

        if raise_hand and hands_y > 0 and not attack:
            can_attack = False
            hands_y -= 30
            if hands_y <= 0:
                hands_y = 0
                raise_hand = False
                can_attack = True
                current_anim_frame = 0

        barrel_gen_range = 10
        for i in barrels:
            if i in agg: 
                continue
            if math.hypot(player_coords['x'] - i[0], player_coords['y'] - i[1]) < barrel_gen_range:
                agg.append((i[0], i[1]))
                sprites.append(Sprite(i, barrel_img, (256, 256), 0.3, s_type="barrel"))
                # barrels.remove(i)
        

        input_handler(delta_time)

        for i in sprites:
            if i.s_type == "barrel" and math.hypot(player_coords['x'] - i.coords[0], player_coords['y'] - i.coords[1]) > 12:
                sprites.remove(i)
                agg.remove(i.coords)

            i.simulate()
        
        check_player_sprite_collision(player_coords['x'] + 0.5, player_coords['y'] + 0.5)

        # if check_player_sprite_collision(player_coords['x'], player_coords['y']):
        #     damage_player(1)

        ray_cast_better()
        render_weapon(current_weapon_state, frames)
        
        if damage_frames > 0:
            display.fill((min(10 * damage_frames, 255),0,0), special_flags=pygame.BLEND_ADD)
            damage_frames -= 1

        render_hud(frames)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if can_attack:
                        attack = True
                if event.key == pygame.K_ESCAPE:
                    quit()
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        # print(clock.get_fps())


init()
