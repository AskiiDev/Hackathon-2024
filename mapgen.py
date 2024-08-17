import random
import math
import numpy as np

import pygame

WIDTH = 200
HEIGHT = 150

ROOMS = 100

ROOM_MIN = 3
ROOM_MAX = 7

TRANSFORMS = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]


SHIFTS = 3

MAX_TRIES = 100

generated_rooms = []
joinable = []
stationary = []
discovered = []

def get_midpoint(room):
    return (room["coords"]['x'] + room["size"]["x"] // 2, room["coords"]['y'] + room["size"]["y"] // 2)

def distance_between_rooms(room1, room2):
    mid_a_x, mid_a_y = room1["coords"]['x'] + room1["size"]["x"] // 2, room1["coords"]['y'] + room1["size"]["y"] // 2
    mid_b_x, mid_b_y = room2["coords"]['x'] + room2["size"]["x"] // 2, room2["coords"]['y'] + room2["size"]["y"] // 2

    return math.hypot(mid_a_x - mid_b_x, mid_a_y - mid_b_y)

def rooms_intersect(a, b):
    a_x, a_y = a["coords"]['x'], a["coords"]['y']
    b_x, b_y = b["coords"]['x'], b["coords"]['y']

    a_right = a_x + a["size"]['x']
    b_right = b_x + b["size"]['x']
    a_bottom = a_y + a["size"]['y']
    b_bottom = b_y + b["size"]['y']

    return a_x >= b_right or b_x >= a_right or a_y >= b_bottom or a_bottom <= b_y

def try_gen_room():
    global generated_rooms

    tries = 0 
    
    while tries < MAX_TRIES: 
        tries += 1
        new_room_size = {'x': random.randint(ROOM_MIN, ROOM_MAX), 
                       'y': random.randint(ROOM_MIN, ROOM_MAX)} 
        new_room_position = {'x': random.randint(0, WIDTH - new_room_size['x']), 
                           'y': random.randint(0, HEIGHT - new_room_size['y'])} 
        
        new_room = {"coords": new_room_position, "size": new_room_size} 

        if all(rooms_intersect(a, new_room) and rooms_intersect(new_room, a) for a in generated_rooms):
            generated_rooms.append(new_room)
            return 0
            
    return False

def try_join_rooms(a, b):
    global stationary
    global joinable

    stuck = False
    dist = distance_between_rooms(a, b)

    times_shifted = 0

    max_x = WIDTH - b["size"]['x']
    max_y = HEIGHT - b["size"]['y']

    while not stuck:
        stuck = True
        smallest_distance = dist
        best_shift = (0, 0)

        for i in TRANSFORMS:
            new_x = b["coords"]['x'] + i[0]
            new_y = b["coords"]['y'] + i[1]

            if not (0 <= new_x <= max_x and 0 <= new_y <= max_y):
                continue

            tmp_dist = distance_between_rooms(a, {"coords": {"x": new_x, "y": new_y}, "size": b["size"]})

            if tmp_dist < smallest_distance and not any(
                    x != a and x != b and not (rooms_intersect(b, x) and rooms_intersect(x, b))
                    for x in joinable):
                smallest_distance = tmp_dist
                best_shift = i

        if best_shift != (0, 0):
            stuck = False

            b["coords"]['x'] += best_shift[0]
            b["coords"]['y'] += best_shift[1]

            dist = smallest_distance

            if not (rooms_intersect(a, b) and rooms_intersect(b, a)):
                times_shifted += 1
                if times_shifted >= SHIFTS:
                    return True

    return False

def gen_map_grid(rooms):
    grid = np.zeros((WIDTH, HEIGHT), dtype=np.uint8)

    # Place each room on the grid
    for room in rooms:
        x_start = room["coords"]['x']
        y_start = room["coords"]['y']
        x_end = x_start + room["size"]['x']
        y_end = y_start + room["size"]['y']

        # Ensure the room fits within the grid boundaries
        x_end = min(x_end, WIDTH)
        y_end = min(y_end, HEIGHT)

        grid[x_start:x_end, y_start:y_end] = 1

    # Create a boolean mask to identify cells to update
    mask = np.zeros((WIDTH, HEIGHT), dtype=bool)

    # Apply transformations and update the mask
    for transform in TRANSFORMS:
        # Apply the transformation (shift) to the grid
        shifted_grid = np.roll(grid, shift=transform, axis=(0, 1))
        
        # Determine which cells have been changed and should be updated
        mask |= (shifted_grid == 0) & (grid == 1)  # Only update cells that were originally 1

    # Update the grid using the mask
    grid[mask] = 2


    def count_adjacent_ones(grid, wall_positions):
        num_rows, num_cols = grid.shape
        adjacent_counts = np.zeros(len(wall_positions), dtype=int)
        
        # Convert wall_positions to a list of row and column indices
        wall_rows, wall_cols = wall_positions[:, 0], wall_positions[:, 1]
        
        for idx, (row, col) in enumerate(zip(wall_rows, wall_cols)):
            # Define the slice boundaries
            row_min, row_max = max(row - 1, 0), min(row + 2, num_rows)
            col_min, col_max = max(col - 1, 0), min(col + 2, num_cols)
            
            # Extract the subgrid of adjacent cells
            subgrid = grid[row_min:row_max, col_min:col_max]
            
            # Count adjacent '1's excluding the wall tile itself
            adjacent_counts[idx] = np.sum(subgrid == 1) - (grid[row, col] == 1)
        
        return adjacent_counts

    
    wall_positions = np.argwhere(grid == 2)
    adjacent_counts = count_adjacent_ones(grid, wall_positions)
    filtered_positions = wall_positions[(adjacent_counts >= 2) & (adjacent_counts <= 3)]

    start_room_mid = get_start_pos()
    distances = np.sqrt([(pos[0] - start_room_mid[0]) ** 2 + (pos[1] - start_room_mid[1]) ** 2 for pos in filtered_positions])
    
    if len(distances) == 0:
        print("No distances calculated for start room.")

    nearest_wall_idx = np.argmin(distances)
    nearest_wall_position = filtered_positions[nearest_wall_idx]
    grid[nearest_wall_position[0], nearest_wall_position[1]] = 3

    # End room midpoint logic
    end_room_mid = get_end_pos()
    distances = np.sqrt([(pos[0] - end_room_mid[0]) ** 2 + (pos[1] - end_room_mid[1]) ** 2 for pos in filtered_positions])

    if len(distances) == 0:
        print("No distances calculated for end room.")
        return grid

    nearest_wall_idx = np.argmin(distances)
    nearest_wall_position = filtered_positions[nearest_wall_idx]
    grid[nearest_wall_position[0], nearest_wall_position[1]] = 4

    return grid

def gen_map(surface):
    global stationary
    global joinable
    global discovered
    global generated_rooms

    generated_rooms = []
    stationary = []
    joinable = []
    discovered = []

    for i in range(ROOMS):
        try_gen_room()

    joinable = generated_rooms.copy()

    stationary.append(generated_rooms[0])
    joinable.remove(generated_rooms[0])

    while len(joinable) > 0:

        closest_pair = min(
            ((a, b, distance_between_rooms(a, b)) for a in stationary for b in joinable),
            key=lambda x: x[2],
            default=None
        )

        if closest_pair:
            stat, join, dist = closest_pair

            if try_join_rooms(stat, join):
                stationary.append(join)
            else:
                generated_rooms.remove(join)

            joinable.remove(join)
        
        hud = pygame.transform.scale(pygame.image.load("imgs/HUD.png").convert_alpha(), (800, 600))

        surface.blit(pygame.transform.scale(render_map(stationary), (800, 450)), (0,0))

        surface.blit(hud, (0, 0))
        pygame.display.flip()


def render_map(rooms):
    colours = np.array([[0, 0, 0], [0, 0, 255], [255, 255, 0], [0,255,0], [0,255,0]], dtype=np.uint8)  # 3x3 array for RGB values
    surface = pygame.Surface((WIDTH, HEIGHT))
    grid = np.array(gen_map_grid(rooms), dtype=np.uint8)  # Convert grid to NumPy array

    # Use grid to index into colours array and create an RGB array for the surface
    pixels = colours[grid]

    # Use surfarray to directly set the surface's pixels
    pygame.surfarray.blit_array(surface, pixels)
    

    return surface

def get_stationary():
    return stationary

def get_discovered():
    return discovered

def discover(x, y):
    pass

def get_start_pos():
    global stationary
    return get_midpoint(stationary[0])

def get_end_pos():
    global stationary
    return get_midpoint(stationary[-1])

def get_real_end_pos():
    global stationary
    return get_midpoint(stationary[-1])

# gen_map()
# print(gen_map_grid(stationary))