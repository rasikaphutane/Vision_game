import cv2 as cv
import numpy as np
import autopy
import math
import os
import pygame
import pymunk as pm
from characters import Bird
from level import Level
import HandTrackingModule as htm
import time


pygame.init()
screen = pygame.display.set_mode((1200, 650))
redbird = pygame.image.load(
    "/home/rasika/DNT_vision_games/angry-birds-python/resources/images/red-bird3.png").convert_alpha()
background2 = pygame.image.load(
    "/home/rasika/DNT_vision_games/angry-birds-python/resources/images/background3.png").convert_alpha()
sling_image = pygame.image.load(
    "/home/rasika/DNT_vision_games/angry-birds-python/resources/images/sling-3.png").convert_alpha()
full_sprite = pygame.image.load(
    "/home/rasika/DNT_vision_games/angry-birds-python/resources/images/full-sprite.png").convert_alpha()
rect = pygame.Rect(181, 1050, 50, 50)
cropped = full_sprite.subsurface(rect).copy()
pig_image = pygame.transform.scale(cropped, (30, 30))
buttons = pygame.image.load(
    "/home/rasika/DNT_vision_games/angry-birds-python/resources/images/selected-buttons.png").convert_alpha()
pig_happy = pygame.image.load(
    "/home/rasika/DNT_vision_games/angry-birds-python/resources/images/pig_failed.png").convert_alpha()
stars = pygame.image.load(
    "/home/rasika/DNT_vision_games/angry-birds-python/resources/images/stars-edited.png").convert_alpha()
rect = pygame.Rect(0, 0, 200, 200)
star1 = stars.subsurface(rect).copy()
rect = pygame.Rect(204, 0, 200, 200)
star2 = stars.subsurface(rect).copy()
rect = pygame.Rect(426, 0, 200, 200)
star3 = stars.subsurface(rect).copy()
rect = pygame.Rect(164, 10, 60, 60)
pause_button = buttons.subsurface(rect).copy()
rect = pygame.Rect(24, 4, 100, 100)
replay_button = buttons.subsurface(rect).copy()
rect = pygame.Rect(142, 365, 130, 100)
next_button = buttons.subsurface(rect).copy()
clock = pygame.time.Clock()
rect = pygame.Rect(18, 212, 100, 100)
play_button = buttons.subsurface(rect).copy()
clock = pygame.time.Clock()
running = True
# the base of the physics
space = pm.Space()
space.gravity = (0.0, -700.0)
pigs = []
birds = []
balls = []
polys = []
beams = []
columns = []
poly_points = []
ball_number = 0
polys_dict = {}
mouse_distance = 0
rope_lenght = 90
angle = 0
x_mouse = 0
y_mouse = 0
count = 0
mouse_pressed = False
t1 = 0
tick_to_next_circle = 10
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
sling_x, sling_y = 135, 450
sling2_x, sling2_y = 160, 450
score = 0
game_state = 0
bird_path = []
counter = 0
restart_counter = False
bonus_score_once = True
bold_font = pygame.font.SysFont("arial", 30, bold=True)
bold_font2 = pygame.font.SysFont("arial", 40, bold=True)
bold_font3 = pygame.font.SysFont("arial", 50, bold=True)
wall = False

# Static floor
static_body = pm.Body(body_type=pm.Body.STATIC)
static_lines = [pm.Segment(static_body, (0.0, 060.0), (1200.0, 060.0), 0.0)]
static_lines1 = [pm.Segment(static_body, (1200.0, 060.0), (1200.0, 800.0), 0.0)]
for line in static_lines:
    line.elasticity = 0.95
    line.friction = 1
    line.collision_type = 3
for line in static_lines1:
    line.elasticity = 0.95
    line.friction = 1
    line.collision_type = 3
space.add(static_body)
for line in static_lines:
    space.add(line)

# Initialize hand detector
detector = htm.HandDetector()
def to_pygame(p):
    """Convert pymunk to pygame coordinates"""
    return int(p.x), int(-p.y+600)


def vector(p0, p1):
    """Return the vector of the points
    p0 = (xo,yo), p1 = (x1,y1)"""
    a = p1[0] - p0[0]
    b = p1[1] - p0[1]
    return (a, b)


def unit_vector(v):
    """Return the unit vector of the points
    v = (a,b)"""
    h = ((v[0]**2)+(v[1]**2))**0.5
    if h == 0:
        h = 0.000000000000001
    ua = v[0] / h
    ub = v[1] / h
    return (ua, ub)


def distance(xo, yo, x, y):
    """distance between points"""
    dx = x - xo
    dy = y - yo
    d = ((dx ** 2) + (dy ** 2)) ** 0.5
    return d


def load_music():
    """Load the music"""
    song1 = '/home/rasika/DNT_vision_games/angry-birds-python/resources/sounds/angry-birds.ogg'
    pygame.mixer.music.load(song1)
    pygame.mixer.music.play(-1)


def sling_action():
    """Actions while sling is pulled."""
    global angle, mouse_distance
    x, y = pygame.mouse.get_pos()
    rel_x, rel_y = x - sling_x, y - sling_y
    angle = math.atan2(rel_y, rel_x)
    angle = max(angle, -math.pi / 2)
    length = min(math.hypot(rel_x, rel_y), rope_lenght)
    bird_image = redbird
    mouse_distance = length
    screen.blit(bird_image, (138, 426))
    pygame.draw.line(screen, (0, 0, 0), (sling_x, sling_y-8),
                     (sling_x + length*math.cos(angle),
                      sling_y + length*math.sin(angle)-8), 5)

def handle_hand_gestures(img,x_mouse):
    global detector
    global screen
    global level
    global space

    # Find hands
    detector.findhands(img)
    lm_list, bbox = detector.findPosition(img)

    # If hands are detected
    if lm_list:
        # Get coordinates of index and middle fingers
        index_x, index_y = lm_list[8][1:]
        middle_x, middle_y = lm_list[12][1:]

        # Check for gestures
        fingers = detector.fingersUp()

        # Move mode: Use index finger to move cursor
        if fingers[1] == 1 and fingers[2] == 0:
            # Convert coordinates from camera frame to screen frame
            x_mouse = np.interp(index_x, (detector.frameR, detector.wCam - detector.frameR), (0, autopy.screen.width))
            y_mouse = np.interp(index_y, (detector.frameR, detector.hCam - detector.frameR), (0, autopy.screen.height))

            # Smooth cursor movement
            autopy.mouse.move(x_mouse, y_mouse)

        # Clicking mode: Use index and middle fingers to click
        elif fingers[1] == 1 and fingers[2] == 1:
            # Find distance between index and middle fingers
            length, _ = detector.findDistance(8, 12, img)

    return img,x_mouse


def draw_level_cleared():
    """Draw level cleared"""
    global game_state
    global bonus_score_once
    global score
    level_cleared = bold_font3.render("Level Cleared!", 1, WHITE)
    score_level_cleared = bold_font2.render(str(score), 1, WHITE)
    if level.number_of_birds >= 0 and len(pigs) == 0:
        if bonus_score_once:
            score += (level.number_of_birds-1) * 10000
        bonus_score_once = False
        game_state = 4
        rect = pygame.Rect(300, 0, 600, 800)
        pygame.draw.rect(screen, BLACK, rect)
        screen.blit(level_cleared, (450, 90))
        if score >= level.one_star and score <= level.two_star:
            screen.blit(star1, (310, 190))
        if score >= level.two_star and score <= level.three_star:
            screen.blit(star1, (310, 190))
            screen.blit(star2, (500, 170))
        if score >= level.three_star:
            screen.blit(star1, (310, 190))
            screen.blit(star2, (500, 170))
            screen.blit(star3, (700, 200))
        screen.blit(score_level_cleared, (550, 400))
        screen.blit(replay_button, (510, 480))
        screen.blit(next_button, (620, 480))



def draw_level_failed():
    """Draw level failed"""
    global game_state
    failed = bold_font3.render("Level Failed", 1, WHITE)
    t2=time.time()
    if level.number_of_birds <= 0 and time.time() - t2 > 5 and len(pigs) > 0:
        game_state = 3
        rect = pygame.Rect(300, 0, 600, 800)
        pygame.draw.rect(screen, BLACK, rect)
        screen.blit(failed, (450, 90))
        screen.blit(pig_happy, (380, 120))
        screen.blit(replay_button, (520, 460))


def restart():
    """Delete all objects of the level"""
    pigs_to_remove = []
    birds_to_remove = []
    columns_to_remove = []
    beams_to_remove = []
    for pig in pigs:
        pigs_to_remove.append(pig)
    for pig in pigs_to_remove:
        space.remove(pig.shape, pig.shape.body)
        pigs.remove(pig)
    for bird in birds:
        birds_to_remove.append(bird)
    for bird in birds_to_remove:
        space.remove(bird.shape, bird.shape.body)
        birds.remove(bird)
    for column in columns:
        columns_to_remove.append(column)
    for column in columns_to_remove:
        space.remove(column.shape, column.shape.body)
        columns.remove(column)
    for beam in beams:
        beams_to_remove.append(beam)
    for beam in beams_to_remove:
        space.remove(beam.shape, beam.shape.body)
        beams.remove(beam)


def post_solve_bird_pig(arbiter, space, _):
    """Collision between bird and pig"""
    surface=screen
    a, b = arbiter.shapes
    bird_body = a.body
    pig_body = b.body
    p = to_pygame(bird_body.position)
    p2 = to_pygame(pig_body.position)
    r = 30
    pygame.draw.circle(surface, BLACK, p, r, 4)
    pygame.draw.circle(surface, RED, p2, r, 4)
    pigs_to_remove = []
    for pig in pigs:
        if pig_body == pig.body:
            pig.life -= 20
            pigs_to_remove.append(pig)
            global score
            score += 10000
    for pig in pigs_to_remove:
        space.remove(pig.shape, pig.shape.body)
        pigs.remove(pig)


def post_solve_bird_wood(arbiter, space, _):
    """Collision between bird and wood"""
    poly_to_remove = []
    if arbiter.total_impulse.length > 1100:
        a, b = arbiter.shapes
        for column in columns:
            if b == column.shape:
                poly_to_remove.append(column)
        for beam in beams:
            if b == beam.shape:
                poly_to_remove.append(beam)
        for poly in poly_to_remove:
            if poly in columns:
                columns.remove(poly)
            if poly in beams:
                beams.remove(poly)
        space.remove(b, b.body)
        global score
        score += 5000


def post_solve_pig_wood(arbiter, space, _):
    """Collision between pig and wood"""
    pigs_to_remove = []
    if arbiter.total_impulse.length > 700:
        pig_shape, wood_shape = arbiter.shapes
        for pig in pigs:
            if pig_shape == pig.shape:
                pig.life -= 20
                global score
                score += 10000
                if pig.life <= 0:
                    pigs_to_remove.append(pig)
    for pig in pigs_to_remove:
        space.remove(pig.shape, pig.shape.body)
        pigs.remove(pig)


# bird and pigs
space.add_collision_handler(0, 1).post_solve=post_solve_bird_pig
# bird and wood
space.add_collision_handler(0, 2).post_solve=post_solve_bird_wood
# pig and wood
space.add_collision_handler(1, 2).post_solve=post_solve_pig_wood
load_music()
level = Level(pigs, columns, beams, space)
level.number = 0
level.load_level()

def main():
    running=True
    x_mouse=0
    #img=None
    while running:
            img = cv.VideoCapture(0)
            #img = cv.flip(img, 1)

            img, x_mouse = handle_hand_gestures(img, x_mouse)
            # Input handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                    # Toggle wall
                    if wall:
                        for line in static_lines1:
                            space.remove(line)
                        wall = False
                    else:
                        for line in static_lines1:
                            space.add(line)
                        wall = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                    space.gravity = (0.0, -10.0)
                    level.bool_space = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                    space.gravity = (0.0, -700.0)
                    level.bool_space = False
                if ( x_mouse > 100 and x_mouse < 250 \
                    and y_mouse > 370 and y_mouse < 550):
                    mouse_pressed = True
                if (event.type == pygame.MOUSEBUTTONUP and
                        event.button == 1 and mouse_pressed):
                    # Release new bird
                    mouse_pressed = False
                    if level.number_of_birds > 0:
                        level.number_of_birds -= 1
                        t1 = time.time()*1000
                        xo = 154
                        yo = 156
                        if mouse_distance > rope_lenght:
                            mouse_distance = rope_lenght
                        if x_mouse < sling_x+5:
                            bird = Bird(mouse_distance, angle, xo, yo, space)
                            birds.append(bird)
                        else:
                            bird = Bird(-mouse_distance, angle, xo, yo, space)
                            birds.append(bird)
                        if level.number_of_birds == 0:
                            t2 = time.time()
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if (x_mouse < 60 and y_mouse < 155 and y_mouse > 90):
                        game_state = 1
                    if game_state == 1:
                        if x_mouse > 500 and y_mouse > 200 and y_mouse < 300:
                            # Resume in the paused screen
                            game_state = 0
                        if x_mouse > 500 and y_mouse > 300:
                            # Restart in the paused screen
                            restart()
                            level.load_level()
                            game_state = 0
                            bird_path = []
                    if game_state == 3:
                        # Restart in the failed level screen
                        if x_mouse > 500 and x_mouse < 620 and y_mouse > 450:
                            restart()
                            level.load_level()
                            game_state = 0
                            bird_path = []
                            score = 0
                    if game_state == 4:
                        # Build next level
                        if x_mouse > 610 and y_mouse > 450:
                            restart()
                            level.number += 1
                            game_state = 0
                            level.load_level()
                            score = 0
                            bird_path = []
                            bonus_score_once = True
                        if x_mouse < 610 and x_mouse > 500 and y_mouse > 450:
                            # Restart in the level cleared screen
                            restart()
                            level.load_level()
                            game_state = 0
                            bird_path = []
                            score = 0
            x_mouse, y_mouse = pygame.mouse.get_pos()
            # Draw background
            screen.fill((130, 200, 100))
            screen.blit(background2, (0, 0))
            # Draw objects
            for bird in birds:
                pygame.draw.circle(screen, (255, 0, 0), (int(bird.body.position.x), int(600-bird.body.position.y)), 20)
            for pig in pigs:
                pygame.draw.circle(screen, (255, 255, 0), (int(pig.body.position.x), int(600-pig.body.position.y)), 25)
            pygame.draw.rect(screen, (0, 0, 0), (sling_x-8, sling_y-8, 16, 16))
            pygame.draw.line(screen, (0, 0, 0), (sling_x, sling_y),
                            (sling2_x, sling2_y), 5)
            # Display frame
            pygame.display.flip()
            # Clock tick
            clock.tick(50)
    pygame.quit()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()