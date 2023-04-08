import pygame
from vector import *
from random import randint
pygame.init()

win_dimensions = Vector(1280, 720)
win = pygame.display.set_mode(win_dimensions)

clock = pygame.time.Clock()
fps = 60

BOT_MAX_SPEED = 2
BOT_ROTATION_SPEED = 0.08
BOT_RADIUS = 15

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
        self.sensor_lines = []
        
        self.mapped = pygame.Surface(win.get_size())
        
    def step(self):
        for dust in Dust._reg:
            if dist(self.pos, dust.pos) < BOT_RADIUS:
                Dust._reg.remove(dust)
    
        self.vel = vectorFromAngle(self.angle, self.speed)
        ppos = self.pos + self.vel
        
        self.sensor_lines = []
        for sensor in self.sensors:
            new_sensor_pos = ppos + vectorFromAngle(self.angle + sensor, BOT_RADIUS)
            self.sensor_lines.append((vectorCopy(ppos), new_sensor_pos))
            
        stop = False
        for sensor_line in self.sensor_lines:
            for wall in Wall._reg:
                if line_intersection(wall.line, sensor_line):
                    ppos = self.pos
                    stop = True
                    break
            if stop:
                break
                    
        self.pos = ppos
        self.speed = 0
        
    def draw(self):
        pygame.draw.circle(win, (255,0,0), self.pos, BOT_RADIUS, 1)
        pygame.draw.line(win, (255,255,255), self.pos, self.pos + vectorFromAngle(self.angle, BOT_RADIUS))
        
        for sensor_line in self.sensor_lines:
            pygame.draw.line(win, (0,0,255), sensor_line[0], sensor_line[1])
        
        pygame.draw.circle(self.mapped, (120,0,0), self.pos, BOT_RADIUS)
        
class Docking:
    _instance = None
    def __init__(self, pos):
        print(pos)
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
        pygame.draw.line(win, (255,255,255), self.line[0], self.line[1])

class Dust:
    _reg = []
    def __init__(self, pos):
        Dust._reg.append(self)
        self.pos = pos
    def draw(self):
        pygame.draw.circle(win, (125, 125, 125), self.pos, 2)

### main loop

Docking((-100,100))
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
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        run = False
    if keys[pygame.K_RIGHT]:
        bot.angle += BOT_ROTATION_SPEED
    if keys[pygame.K_LEFT]:
        bot.angle -= BOT_ROTATION_SPEED
    if keys[pygame.K_UP]:
        bot.speed = BOT_MAX_SPEED
    if keys[pygame.K_DOWN]:
        bot.speed = -BOT_MAX_SPEED
    
    ctrl_hold = False
    if keys[pygame.K_LCTRL]:
        ctrl_hold = True
    
    # step
    bot.step()

    # draw
    win.fill((0,0,0))
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