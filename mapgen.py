import random
import math


WIDTH = 30
HEIGHT = 30

ROOMS = 30

ROOM_MIN = 5
ROOM_MAX = 15

MAX_TRIES = 100

generatedRooms = []

def distanceBetweenRooms(room1, room2):
    mid_a_x, mid_a_y = a["coords"]['x'] + a["size"]["x"] // 2, a["coords"]['y'] + a["size"]["y"] // 2
    mid_b_x, mid_b_y = b["coords"]['x'] + b["size"]["x"] // 2, b["coords"]['y'] + b["size"]["y"] // 2

    return math.hypot(mid_a_x - mid_b_x, mid_a_y - mid_b_y)

def roomsIntersect(room1, room2):
    x1, y1, w1, h1 = room1["coords"]["x"], room1["coords"]["y"], room1["size"]["x"], room1["size"]["y"]
    x2, y2, w2, h2 = room2["coords"]["x"], room2["coords"]["y"], room2["size"]["x"], room2["size"]["y"]

    return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)

def try_gen_room():
    global generatedRooms

    tries = 0 
    
    while tries < MAX_TRIES: 
        tries += 1
        newRoomSize = {'x': random.randint(ROOM_MIN, ROOM_MAX), 
                       'y': random.randint(ROOM_MIN, ROOM_MAX)} 
        newRoomPosition = {'x': random.randint(0, WIDTH - newRoomSize['x']), 
                           'y': random.randint(0, HEIGHT - newRoomSize['y'])} 
        
        newRoom = {"coords": newRoomPosition, "size": newRoomSize} 

        if len(generatedRooms) == 0:
            generatedRooms.append(newRoom)
            return True

        for room in generatedRooms:
            if not roomsIntersect(room, newRoom):
                generatedRooms.append(newRoom)
                return True
            
    return False

def gen_map():
    global generatedRooms
    global stationary

    generatedRooms = []
    stationary = [] 

    for room in range(ROOMS):
        try_gen_room()

    while len(generatedRooms) != 0:
        


    print(generatedRooms)


gen_map()