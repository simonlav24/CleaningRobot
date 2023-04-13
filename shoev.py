import pygame
from vector import *
from random import randint
from functools import partial
from math import pi, degrees

pygame.init()

win_dimensions = Vector(1280, 720)
win = pygame.display.set_mode(win_dimensions)

clock = pygame.time.Clock()
fps = 60

BOT_MAX_SPEED = 2
BOT_ROTATION_SPEED = pi / 32
BOT_RADIUS = 15

CLOCK_SMALL = 10
CLOCK_BIG = 20
CLOCK_PI8 = 4
CLOCK_IMMIDIATE = 1

DEBUG = False

bot_sprite = pygame.image.load('bot_sprite.png')

def load_room(path):
    with open(path, 'r') as file:
        reg = eval(file.readline())
        for wall in reg:
            Wall(wall)

def save_room(path):
    with open(path, 'w+') as file:
        file.write(str(Wall._reg))

def line_intersection(line1, line2):
	x1, y1, x2, y2 = line1[0][0], line1[0][1], line1[1][0], line1[1][1]
	x3, y3, x4, y4 = line2[0][0], line2[0][1], line2[1][0], line2[1][1]
	
	den = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
	if den == 0:
		return False
	t = ((x1 - x3)*(y3 - y4) - (y1 - y3)*(x3 - x4)) / den
	u = -((x1 - x2)*(y1 - y3) - (y1 - y2)*(x1 - x3)) / den
	if u >= 0 and u <= 1 and t >= 0 and t <= 1:
		return True
	return False

### setup

class Bot:
    def __init__(self):
        self.pos = win_dimensions / 2
        self.angle = 0
        self.speed = BOT_MAX_SPEED
        
        self.sensors = [0, -1, 1]
        self.sensors_color = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        self.sensor_lines = []

        self.state_map = {
            'idle': {
                'timeout': partial(self.handle_movement, 'forward_free_0', CLOCK_SMALL, self.move_skip),
            },
            'forward_free_0': {
                'timeout': partial(self.handle_movement, 'forward_free_0', CLOCK_SMALL, self.move_forward),
                'bump_0': partial(self.handle_movement, 'backward_0', CLOCK_SMALL, self.move_skip),
                'bump_1': partial(self.handle_movement, 'backward_1', CLOCK_SMALL, self.move_skip),
                'bump_2': partial(self.handle_movement, 'backward_2', CLOCK_SMALL, self.move_skip),
            },
            'forward_check_0': {
                'timeout': partial(self.handle_movement, 'left_0', CLOCK_PI8, self.move_forward),
                'bump_0': partial(self.handle_movement, 'backward_0', CLOCK_SMALL, self.move_skip),
                'bump_1': partial(self.handle_movement, 'backward_1', CLOCK_SMALL, self.move_skip),
                'bump_2': partial(self.handle_movement, 'backward_2', CLOCK_SMALL, self.move_skip),
            },
            'forward_check_1': {
                'timeout': partial(self.handle_movement, 'right_1', CLOCK_PI8, self.move_forward),
                'bump_0': partial(self.handle_movement, 'backward_0', CLOCK_SMALL, self.move_skip),
                'bump_1': partial(self.handle_movement, 'backward_1', CLOCK_SMALL, self.move_skip),
                'bump_2': partial(self.handle_movement, 'backward_2', CLOCK_SMALL, self.move_skip),
            },
            'forward_check_2': {
                'timeout': partial(self.handle_movement, 'left_2', CLOCK_PI8, self.move_forward),
                'bump_0': partial(self.handle_movement, 'backward_0', CLOCK_SMALL, self.move_skip),
                'bump_1': partial(self.handle_movement, 'backward_1', CLOCK_SMALL, self.move_skip),
                'bump_2': partial(self.handle_movement, 'backward_2', CLOCK_SMALL, self.move_skip),
            },
            'backward_0': {
                'timeout': partial(self.handle_movement, 'left_0', CLOCK_PI8, self.move_backward),
            },
            'backward_1': {
                'timeout': partial(self.handle_movement, 'left_1', CLOCK_PI8, self.move_backward),
            },
            'backward_2': {
                'timeout': partial(self.handle_movement, 'right_2', CLOCK_PI8, self.move_backward),
            },
            'left_0': {
                'timeout': partial(self.handle_movement, 'forward_corner_check_0', CLOCK_BIG, self.move_left),
            },
            'left_1': {
                'timeout': partial(self.handle_movement, 'forward_corner_check_1', CLOCK_BIG, self.move_left),
            },
            'left_2': {
                'timeout': partial(self.handle_movement, 'forward_corner_check_2', CLOCK_BIG, self.move_left),
            },
            'right_0': {
                'timeout': partial(self.handle_movement, 'forward_corner_check_0', CLOCK_BIG, self.move_right),
            },
            'right_1': {
                'timeout': partial(self.handle_movement, 'forward_corner_check_1', CLOCK_BIG, self.move_right),
            },
            'right_2': {
                'timeout': partial(self.handle_movement, 'forward_corner_check_2', CLOCK_BIG, self.move_right),
            },
            'forward_corner_check_0': {
                'timeout': partial(self.handle_movement, 'backward_0', CLOCK_BIG, self.move_forward),
                'bump_0': partial(self.handle_movement, 'forward_check_0', CLOCK_IMMIDIATE, self.move_skip),
                'bump_1': partial(self.handle_movement, 'forward_check_1', CLOCK_IMMIDIATE, self.move_skip),
                'bump_2': partial(self.handle_movement, 'forward_check_2', CLOCK_IMMIDIATE, self.move_skip),
            },
            'forward_corner_check_1': {
                'timeout': partial(self.handle_movement, 'backward_1', CLOCK_BIG, self.move_forward),
                'bump_0': partial(self.handle_movement, 'forward_check_0', CLOCK_IMMIDIATE, self.move_skip),
                'bump_1': partial(self.handle_movement, 'forward_check_1', CLOCK_IMMIDIATE, self.move_skip),
                'bump_2': partial(self.handle_movement, 'forward_check_2', CLOCK_IMMIDIATE, self.move_skip),
            },
            'forward_corner_check_2': {
                'timeout': partial(self.handle_movement, 'backward_2', CLOCK_BIG, self.move_forward),
                'bump_0': partial(self.handle_movement, 'forward_check_0', CLOCK_IMMIDIATE, self.move_skip),
                'bump_1': partial(self.handle_movement, 'forward_check_1', CLOCK_IMMIDIATE, self.move_skip),
                'bump_2': partial(self.handle_movement, 'forward_check_2', CLOCK_IMMIDIATE, self.move_skip),
            },
        }
        
        self.mapped = pygame.Surface(win.get_size(), pygame.SRCALPHA)

        self.state = 'idle'
        self.next_state = ''
        self.next_clock = 0
        self.clock = 0
        self.edge = 'timeout'
        
        self.t = 0
        
    def handle_movement(self, next_state, next_clock, movement):
        self.next_state = next_state
        self.next_clock = next_clock
        self.clock -= 1
        if self.clock <= 0:
            self.edge = 'timeout'
            self.state = next_state
            self.clock = next_clock
        movement()
                
    def step(self):

        # self.algorithm()

        for dust in Dust._reg:
            if dist(self.pos, dust.pos) < BOT_RADIUS:
                Dust._reg.remove(dust)
    
        self.vel = vectorFromAngle(self.angle, self.speed)
        ppos = self.pos + self.vel
        
        self.sensor_lines = []
        for sensor in self.sensors:
            new_sensor_pos = ppos + vectorFromAngle(self.angle + self.sensors[sensor], BOT_RADIUS)
            self.sensor_lines.append((vectorCopy(ppos), new_sensor_pos))
            
        stop = False
        for sensor_index, sensor_line in enumerate(self.sensor_lines):
            for wall in Wall._reg:
                if line_intersection(wall.line, sensor_line):
                    ppos = self.pos
                    self.intersection_response(sensor_index)
                    self.last_bump_sensor_index = sensor_index
                    stop = True
                    break
            if stop:
                break
                    
        self.pos = ppos
        self.speed = 0
        
        self.t += 0.3
        
    def draw(self):
    
        normal = vectorFromAngle(self.angle, BOT_RADIUS).normal() * 3/4
        p1 = self.pos + vectorFromAngle(self.angle, BOT_RADIUS * 3/4) + normal
        p2 = self.pos + vectorFromAngle(self.angle, BOT_RADIUS * 3/4) - normal
        t = self.t
        pygame.draw.line(win, (0,0,0), p1 + vectorFromAngle(self.t, 7), p1 - vectorFromAngle(self.t, 7), 2)
        pygame.draw.line(win, (0,0,0), p2 + vectorFromAngle(-self.t, 7), p2 - vectorFromAngle(-self.t, 7), 2)
    
        sprite = pygame.transform.rotate(bot_sprite, degrees(-self.angle))
        win.blit(sprite, self.pos - tup2vec(sprite.get_size()) / 2)
        
        if DEBUG:
            pygame.draw.circle(win, (255,0,0), self.pos, BOT_RADIUS, 1)
            pygame.draw.line(win, (255,255,255), self.pos, self.pos + vectorFromAngle(self.angle, BOT_RADIUS))
            
            pygame.draw.line(win, self.sensors_color[0], self.sensor_lines[0][0], self.sensor_lines[0][1])
            pygame.draw.line(win, self.sensors_color[1], self.sensor_lines[1][0], self.sensor_lines[1][1])
            pygame.draw.line(win, self.sensors_color[2], self.sensor_lines[2][0], self.sensor_lines[2][1])
            
        pygame.draw.circle(self.mapped, (103,111,147), self.pos, BOT_RADIUS)

    def move_forward(self):
        self.speed = BOT_MAX_SPEED

    def move_backward(self):
        self.speed = -BOT_MAX_SPEED

    def move_left(self):
        self.angle -= BOT_ROTATION_SPEED

    def move_right(self):
        self.angle += BOT_ROTATION_SPEED

    def move_skip(self):
        self.clock = 1

    def intersection_response(self, sensor_index):
        if 'left' in self.state or 'right' in self.state:
            return
        print('[INTERSECTION]', sensor_index)
        self.edge = f'bump_{str(sensor_index)}'
        # self.state = f'backward_{str(sensor_index)}'
        self.clock = CLOCK_SMALL 

    def algorithm(self):
        
        try:
            func = self.state_map[self.state][self.edge]
            print(self.state, self.edge, self.clock, func.args)
            func()
        except Exception as e:
            print(type(e))
            print(e)
            print(self.state, self.edge, self.clock)
            exit(1)   


class Docking:
    _instance = None
    def __init__(self, pos):
        self.pos = vecFromTuple(pos)
        Docking._instance = self
        
    def draw(self):
        pygame.draw.circle(win, (0,255,0), self.pos, BOT_RADIUS)

class Wall:
    _reg = []
    def __init__(self, line):
        Wall._reg.append(self)
        self.line = line
    def __str__(self):
        return str(self.line)
    def __repr__(self):
        return str(self)
    def draw(self):
        pygame.draw.line(win, (255,255,255), self.line[0], self.line[1], 2)

class Dust:
    _reg = []
    def __init__(self, pos):
        Dust._reg.append(self)
        self.pos = pos
    def draw(self):
        pygame.draw.circle(win, (125, 125, 125), self.pos, 2)

def draw_background():
    win.fill((8,20,62))
    win.blit(bot.mapped, (0,0))
    for i in range(0, win_dimensions[0], 50):
        pygame.draw.line(win, (60,69,112), (i, 0), (i, win_dimensions[1]))
    for i in range(0, win_dimensions[1], 50):
        pygame.draw.line(win, (60,69,112), (0, i), (win_dimensions[0], i))

### main loop

Docking((0,0))
load_room('room.txt')
bot = Bot()

for _ in range(80):
    x = randint(0, win_dimensions[0])
    y = randint(0, win_dimensions[1])
    Dust(Vector(x, y))

press_pos = None
release_pos = None
mouse_hold = False
build_mode = False
ctrl_hold = False

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_hold = True
            press_pos = pygame.mouse.get_pos()
            if ctrl_hold:
                build_mode = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouse_hold = False
            release_pos = pygame.mouse.get_pos()
            if build_mode:
                Wall((press_pos, release_pos))
            build_mode = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                save_room('room.txt')
            if event.key == pygame.K_l:
                load_room('room.txt')
            if event.key == pygame.K_d:
                Docking(pygame.mouse.get_pos())
                bot.pos = vecFromTuple(pygame.mouse.get_pos())
                bot.state = 'dock'
            if event.key == pygame.K_p:
                DEBUG = not DEBUG
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        run = False
    if keys[pygame.K_RIGHT]:
        bot.move_right()
    if keys[pygame.K_LEFT]:
        bot.move_left()
    if keys[pygame.K_UP]:
        bot.move_forward()
    if keys[pygame.K_DOWN]:
        bot.move_backward()
    
    ctrl_hold = False
    if keys[pygame.K_LCTRL]:
        ctrl_hold = True
    
    # step
    bot.step()

    # draw
    draw_background()
    # win.fill((0,0,0))
    # win.blit(bot.mapped, (0,0))
    for wall in Wall._reg:
        wall.draw()
    for dust in Dust._reg:
        dust.draw()

    Docking._instance.draw()
    bot.draw()
    
    if build_mode and press_pos:
        pygame.draw.line(win, (255,255,255), press_pos, pygame.mouse.get_pos())
    
    clock.tick(fps)
    pygame.display.update()