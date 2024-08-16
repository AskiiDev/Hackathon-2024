import random
import math


WIDTH = 30
HEIGHT = 30

ROOMS = 30

ROOM_MIN = 5
ROOM_MAX = 15

MAX_TRIES = 100

generated_rooms = []

def distance_between_rooms(room1, room2):
    mid_a_x, mid_a_y = room1["coords"]['x'] + room1["size"]["x"] // 2, room1["coords"]['y'] + room1["size"]["y"] // 2
    mid_b_x, mid_b_y = room2["coords"]['x'] + room2["size"]["x"] // 2, room2["coords"]['y'] + room2["size"]["y"] // 2

    return math.hypot(mid_a_x - mid_b_x, mid_a_y - mid_b_y)

def rooms_intersect(room1, room2):
    x1, y1, w1, h1 = room1["coords"]["x"], room1["coords"]["y"], room1["size"]["x"], room1["size"]["y"]
    x2, y2, w2, h2 = room2["coords"]["x"], room2["coords"]["y"], room2["size"]["x"], room2["size"]["y"]

    return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)

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

        if len(generated_rooms) == 0:
            generated_rooms.append(new_room)
            return True

        for room in generated_rooms:
            if not rooms_intersect(room, new_room):
                generated_rooms.append(new_room)
                return True
            
    return False

def gen_map():
    global generated_rooms
    global stationary

    generated_rooms = []
    stationary = [] 
    joinable = []

    for room in range(ROOMS):
        try_gen_room()

    joinable = generated_rooms.copy()

    stationary.append(generated_rooms[0])
    joinable.remove(generated_rooms[0])

    while len(joinable) != 0:
        closest_pair = min(((a, b, distance_between_rooms(a, b)) for a in stationary for b in joinable), key=lambda x: x[2], default=None) 
        
        if closest_pair:
            stat, join, dist = closest_pair

            if try_join_rooms(stat, join):
                stationary.append(join)
            else:
                generated_rooms.remove(join)

            joinable.remove(join)




    print(generated_rooms)


gen_map()