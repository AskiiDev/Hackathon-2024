from mapgen import *
import pygame
import math
import time

TEMP_WALL = [0, 2, 3, 4]

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

running = True

pygame.init()
pygame.font.init()

FONTS = {
    'floor': pygame.font.Font("almendra/Almendra-Regular.ttf", 40),
    'floor_n': pygame.font.Font("almendra/Almendra-Regular.ttf", 40),
    'timer': pygame.font.Font("almendra/Almendra-Regular.ttf", 40),
    'health': pygame.font.Font("almendra/Almendra-Regular.ttf", 40)
}

pygame.mixer.music.load("People Are Strange.mp3")


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

punch = {0: (pygame.transform.scale(pygame.image.load("imgs/attacks/punch/fist1.png").convert_alpha(), (WIDTH, HEIGHT)), 2),
         1: (pygame.transform.scale(pygame.image.load("imgs/attacks/punch/fist2.png").convert_alpha(), (WIDTH, HEIGHT)), 2),
         2: (pygame.transform.scale(pygame.image.load("imgs/attacks/punch/fist3.png").convert_alpha(), (WIDTH, HEIGHT)), 5),
         3: (pygame.transform.scale(pygame.image.load("imgs/attacks/punch/fist4.png").convert_alpha(), (WIDTH, HEIGHT)), 13),
         4: (pygame.transform.scale(pygame.image.load("imgs/attacks/punch/fist3.png").convert_alpha(), (WIDTH, HEIGHT)), 2),
         5: (pygame.transform.scale(pygame.image.load("imgs/attacks/punch/fist2.png").convert_alpha(), (WIDTH, HEIGHT)), 2)}

ATTACKS = {
    "punch": [punch, 4]
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

ghost_images = {
    0: load_image(pygame.image.load("imgs/enemies/ghost/A3.png").convert_alpha(), False),
    1: load_image(pygame.image.load("imgs/enemies/ghost/A4.png").convert_alpha(), False),
    2: load_image(pygame.image.load("imgs/enemies/ghost/A5.png").convert_alpha(), False)
}
goblin_images = {
    0: load_image(pygame.image.load("imgs/enemies/goblin/A1.png").convert_alpha(), False),
    1: load_image(pygame.image.load("imgs/enemies/goblin/A2.png").convert_alpha(), False),
    2: load_image(pygame.image.load("imgs/enemies/goblin/A3.png").convert_alpha(), False),
    3: load_image(pygame.image.load("imgs/enemies/goblin/A4.png").convert_alpha(), False),
    4: load_image(pygame.image.load("imgs/enemies/goblin/A5.png").convert_alpha(), False),
    5: load_image(pygame.image.load("imgs/enemies/goblin/A6.png").convert_alpha(), False),
    6: load_image(pygame.image.load("imgs/enemies/goblin/A7.png").convert_alpha(), False),
    7: load_image(pygame.image.load("imgs/enemies/goblin/A8.png").convert_alpha(), False)
}

gore_pile = load_image(pygame.image.load("imgs/enemies/gorepile.png").convert_alpha(), False)

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
    global level
    global level_start_time
    global player_rot
    global player_health
    global goal_coords

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
    arrow_texture = get_arrow_texture(-angle_to_goal, -player_rot)

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

    now = time.time()
    minutes, seconds = divmod(int(now - level_start_time), 60)

    floor_title = FONTS['floor'].render("FLOOR", True, (255, 255, 255))
    timer_title = FONTS['timer'].render("TIMER", True, (255, 255, 255))
    health_title = FONTS['timer'].render("HP", True, (255, 255, 255))
    health_counter = FONTS['floor_n'].render(f"{player_health}", True, (200, 200, 200))
    floor_counter = FONTS['floor_n'].render(f"{level}", True, (200, 200, 200))
    timer_counter = FONTS['floor_n'].render(f"{minutes}:{seconds:02}", True, (200, 200, 200))

    display.blit(floor_title, (48.5, 475))
    display.blit(timer_title, (195.5, 475))
    display.blit(health_title, (523, 475))
    display.blit(health_counter, (520, 520))
    display.blit(floor_counter, (98.5, 520))
    display.blit(timer_counter, (220, 520))


def render_weapon(weapon_state, delta):
    global anim_frames
    quantization_step = 6

    x_pos = int(15 * math.cos(delta / 10))
    y_pos = int(10 * abs(math.sin(delta / 10)))

    # Quantize the positions
    x_pos = (x_pos // quantization_step) * quantization_step
    y_pos = (y_pos // quantization_step) * quantization_step

    display.blit(weapon_state, (x_pos, y_pos))


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
        fire_x = player_x + fire_dx * dist
        fire_y = player_y + fire_dy * dist

        # Check if this point hits any sprite
        for sprite in sprites:
            sprite_x, sprite_y = sprite.coords
            sprite_width, sprite_height = sprite.width, sprite.width

            # Check for collision with sprite's bounding box
            if (sprite_x + (0.5 - sprite_width) < fire_x < sprite_x + (0.5 + sprite_width) and
                sprite_y+ (0.5 - sprite_width) < fire_y < sprite_y + (0.5 + sprite_width)):
                print(f"Hit detected on sprite at {sprite.coords} after {dist} units")
                # handle_hit(sprite)  # Call a function to handle the hit
                sprite.get_hit()
                return

        # Optionally, check if the bullet hits a wall or other obstacle in the map
        if MAP[int(fire_x)][int(fire_y)] in TEMP_WALL:
            print(f"Bullet hit a wall at {int(fire_x)}, {int(fire_y)} after {dist} units")
            return

    print("No hit detected.")


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
            # sprite.hit_player()  # Call a function to handle what happens on collision
            # print("HI")
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
    global anim_frames
    global player_health

    def __init__(self, coords, texture, res, width, health=1, solid=True, s_type='default'):
        self.coords = coords
        self.texture = texture
        self.res = res
        self.width = width
        self.health = health
        self.solid = solid
        self.s_type = s_type
        self.mark_for_death = 0
        self.died = False

    def handle_collision(self, sprite):
        pass

    def get_hit(self):
        if not self.died:
            self.died = True
            self.mark_for_death = 20
        # if self.s_type == "ghost":
        #     self.texture = ghost_images["falling"]
        # if self.s_type == "goblin":
        #     self.texture = goblin_images["falling"]

    def hit_player(self):
        pass

    def simulate(self):
        if self.mark_for_death == 1:
            sprites.append(Sprite((self.coords), gore_pile, self.res, self.width, s_type = 'gore pile'))
            sprites.remove(self)

        elif self.mark_for_death > 1:
            self.mark_for_death -= 1

        else:        
            if self.s_type == "ghost":
                self.texture = ghost_images[anim_frames % 3]

                player_x, player_y = player_coords['x'], player_coords['y']
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
                ghost_x += direction_x * ghost_speed
                ghost_y += direction_y * ghost_speed


                self.coords = (ghost_x, ghost_y)

            if self.s_type == "goblin":

                player_x, player_y = player_coords['x'], player_coords['y']
                goblin_x, goblin_y = self.coords

                    # Calculate the direction vector from the ghost to the player
                direction_x = player_x - goblin_x
                direction_y = player_y - goblin_y

                    # Normalize the direction vector to get a unit vector
                distance = math.sqrt(direction_x ** 2 + direction_y ** 2)
                if distance != 0:
                    direction_x /= distance
                    direction_y /= distance

                goblin_speed = 0.03  # Adjust this value for desired speed

                if distance < 3:

                        # Update the ghost's position to move along the direction vector
                    
                    goblin_x -= direction_x * goblin_speed
                    if MAP[int(goblin_x + 0.5 - self.width)][int(goblin_y + 0.5 - self.width)] in TEMP_WALL:
                        goblin_x += direction_x * goblin_speed

                    goblin_y -= direction_y * goblin_speed
                    if MAP[int(goblin_x + 0.5 - self.width)][int(goblin_y + 0.5 - self.width)] in TEMP_WALL:
                        goblin_y += direction_y * goblin_speed
                    self.coords = (goblin_x, goblin_y)


                elif distance > 4:
             
                    goblin_x += direction_x * goblin_speed
                    if MAP[int(goblin_x)][int(goblin_y)] in TEMP_WALL:
                        goblin_x -= direction_x * goblin_speed

                    goblin_y += direction_y * goblin_speed
                    if MAP[int(goblin_x)][int(goblin_y)] in TEMP_WALL:
                        goblin_y -= direction_y * goblin_speed
                    self.coords = (goblin_x, goblin_y)



def next_level():
    global total_score
    global score
    global level
    global MAP

    total_score += score
    display.fill(pygame.Color(0,0,0))
    render_hud(0)
    print("Score:")
    print(score)
    print("Total:")
    print(total_score)
    pygame.display.flip()

    pygame.time.wait(1000)
    display.fill(pygame.Color(0,0,0))
    render_hud(0)

    print("Generating map...")
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
    global textures
    global goal_coords
    global sprites
    global score
    global player_health

    player_health = 100

    score = 0
    background = None

    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)

    MAP = gen_map_grid(get_stationary())
    print(MAP)

    MAP_WIDTH = len(MAP)
    MAP_HEIGHT = len(MAP[0])
    start_pos = get_start_pos()
    player_coords = {'x': start_pos[0] + 0.5, 'y': start_pos[1] + 0.5}
    goal_coords = get_real_end_pos()
    player_rotation = {'x': -1, 'y': 0}
    camera_plane = {'x': 0, 'y': 0.66}


    pygame.time.wait(1000)
    level_start_time = time.time()

    sprites = []


    barrel = Sprite((start_pos[0] + 1, start_pos[1] + 1), load_image(pygame.image.load("imgs/barrel.png").convert_alpha(), False), (64, 64), 0.5, solid=True)
    sprites.append(barrel)
    # ghost_test = Sprite((start_pos[0] + 1, start_pos[1] + 1), ghost_images[1], (256,256), 0.5, health=5, solid=True, s_type="ghost")
    # sprites.append(ghost_test)

    goblin_test = Sprite((start_pos[0] - 1, start_pos[1] - 1), goblin_images[0], (256,256), 0.5, health=5, solid=True, s_type="goblin")
    sprites.append(goblin_test)

    # check_sprite_collision(gobbo, gobbo2)

    last_pos = start_pos


def init():
    global running
    global total_score
    global textures
    global level
    global sprites
    global MAP
    global frames
    global anim_frames
    global player_health

    attack = None

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
    

    total_score = 0
    level = 1

    player_health = 100

    gen_map(display)
    frames = 0

    current_weapon_state = punch[0][0]
    current_anim_frame = 0
    anim_counter = 0

    load_level()
    # pygame.mixer.music.play()

    while running:
        frames += 1
        anim_frames = int(frames / 20)
        display.fill((0, 0, 0))
        delta_time = 1 / clock.tick(60)

        if attack is not None:
            if frames - anim_counter >= punch[current_anim_frame][1]:
                current_anim_frame += 1
                if current_anim_frame >= len(punch):
                    attack = None
                    current_anim_frame = 0
                    current_weapon_state = punch[0][0]
                else:
                    anim_counter = frames
                    current_weapon_state = punch[current_anim_frame][0]

        input_handler(delta_time)

        for i in sprites:
            i.simulate()

        if check_player_sprite_collision(player_coords['x'], player_coords['y']):
            player_health = max(0, player_health - 1)

        ray_cast_better()
        render_weapon(current_weapon_state, frames)
        render_hud(frames)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fire(2)
                    attack = "punch"
                if event.key == pygame.K_ESCAPE:
                    quit()
                if event.key == pygame.K_TAB:
                    next_level()
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        # print(clock.get_fps())


init()
