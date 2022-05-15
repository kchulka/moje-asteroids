#!/usr/bin/env python3
"""
verze 03

- parametr radius u SpaceObject
- funkce draw_circle()
"""
import pyglet
from pyglet.window import key
from pyglet import gl
import math
import random

WIDTH  = 1500
HEIGHT = 850

ROTATION_SPEED = 4 # radiánů za sekundu
ACCELERATION   = 5
asteroid_images = ['meteorBrown_big1.png', 'meteorBrown_med1.png', 'meteorBrown_small1.png', 'meteorBrown_tiny1.png'] 
asteroid_images += ['meteorGrey_big2.png', 'meteorGrey_med2.png', 'meteorGrey_small2.png', 'meteorGrey_tiny2.png'] 

class SpaceObject:
    """ vesmírný objekt """

    def __init__(self, img, x=0, y=0, speed=0, rotation=0):
        self.image = pyglet.image.load(img) 
        self.image.anchor_x = self.image.width // 2
        self.image.anchor_y = self.image.height // 2
        self.sprite = pyglet.sprite.Sprite(self.image, batch=batch, group=foreground)
        self.x = x
        self.y = y
        self.rotation = rotation
        self.speed = speed
        self.radius = max([self.sprite.width, self.sprite.height]) / 2

    def __str__(self):
        return str(self.__repr__())

    def __repr__(self):
        return "SpaceObject({}, {}, {})".format(self.x, self.y)              
 
    def __del__(self):
        self.sprite.delete()
 
    def delete(self):
        """ vymaže sebe sama (self) ze hry """
        vesmir.objects.remove(self)
        del self

    def tik(self, dt):
        """ změna polohy vesmírného objektu """

        # -- přepočítání souřadnic objektu --
        self.x += self.speed * math.cos(self.rotation)
        self.y += self.speed * math.sin(self.rotation)

        # -- parametry sprite --
        self.sprite.rotation = 90 - math.degrees(self.rotation)
        self.sprite.x = self.x
        self.sprite.y = self.y

class SpaceShip(SpaceObject):
    """ vesmírná loď """

    def __init__(self, img='shuttle2.png',x=0, y=0, management=dict()):
        super().__init__(img, x, y, rotation=math.pi/2) 
        if len(management) == 0:
            self.management = {'left':key.LEFT, 'right':key.RIGHT, 'forward':key.UP, 'backward':key.DOWN}
        else:
            self.management = management

    def __repr__(self):
        return "SpaceShip({}, {})".format(self.x, self.y)              

    def out_of_window(self):
        if self.x > WIDTH:
            self.x = self.sprite.x = 0
        elif self.x < 0:
            self.x = self.sprite.x = WIDTH
        elif self.y > HEIGHT:
            self.y = self.sprite.y = 0
        elif self.y < 0:
            self.y = self.sprite.y = HEIGHT

    def tik(self, dt):
        if self.management['left'] in stisknute_klavesy:
            """ rotace vlevo """
            self.rotation += dt * ROTATION_SPEED
        
        if self.management['right'] in stisknute_klavesy:
            """ rotace vpravo """
            self.rotation -= dt * ROTATION_SPEED
        
        if self.management['forward'] in stisknute_klavesy:
            """ zvýšení rychlosti """
            self.speed += dt * ACCELERATION

        if self.management['backward'] in stisknute_klavesy:
            """ snížení rychlosti """
            self.speed -= dt * ACCELERATION if self.speed > 0 else 0 
 
        super().tik(dt)
        self.out_of_window()

class Asteroid(SpaceObject):
    """ Asteroid """

    def __init__(self, x, y, direction=0, images=asteroid_images):
        img = random.choice(images)
        speed = random.randint(2,30)
        self.sprite_rotation = random.randint(0,10)
        self.rotate_speed = random.random() * 5.0 - 3.0
        super().__init__(img, x, y, speed=speed, rotation=direction)

    def __repr__(self):
        return "Asteroid({}, {})".format(self.x, self.y)              

    def tik(self, dt):
        super().tik(dt)            
        
        # rotace asteroidu
        self.sprite_rotation += self.rotate_speed * dt
        self.sprite.rotation = 90 - math.degrees(self.sprite_rotation)
 
class Space:
    """ Vesmír """

    def __init__(self, objects=[], img=None):
        self.objects = objects
        if img != None:
            self.image = pyglet.image.load(img)
            self.sprite = pyglet.sprite.Sprite(self.image, batch=batch, group=background)
    
    def __iadd__(self, other):
        self.objects += [other]
        return self

    def __str__(self):
        return str(self.__repr__())

    def __repr__(self):
        return "Space({})".format(self.objects)

    def out_of_space(self, spaceobject):
        """ není objekt mimo vesmír? """
        if spaceobject.x < 0 or spaceobject.x > WIDTH:
            return True
        elif spaceobject.y < 0 or spaceobject.y > HEIGHT:
            return True
        else:
            return False

    def tik(self, dt):
        for space_object in self.objects:
            space_object.tik(dt)                # tik všech objektů ve vesmíru      

            if self.out_of_space(space_object): # není  objekt mimo hranice okna?
                space_object.delete()
 
stisknute_klavesy = set()

# --- okno aplikace ---
window = pyglet.window.Window(width=WIDTH, height=HEIGHT)

def stisk_klavesy(symbol, modifikatory):
    global stisknute_klavesy
    stisknute_klavesy.add(symbol)

def uvolneni_klavesy(symbol, modifikatory):
    global stisknute_klavesy
    stisknute_klavesy.discard(symbol)

def vykresli():
    window.clear()

    for x_offset in (-window.width, 0, window.width):
        for y_offset in (-window.height, 0, window.height):
            # Remember the current state
            gl.glPushMatrix()
            # Move everything drawn from now on by (x_offset, y_offset, 0)
            gl.glTranslatef(x_offset, y_offset, 0)

            # Draw
            batch.draw()

            # kolečka 
            for space_object in vesmir.objects:
                draw_circle(space_object.x, space_object.y, space_object.radius)

            # Restore remembered state (this cancels the glTranslatef)
            gl.glPopMatrix()

def draw_circle(x, y, radius):
        iterations = 20
        s = math.sin(2*math.pi / iterations)
        c = math.cos(2*math.pi / iterations)

        dx, dy = radius, 0

        gl.glBegin(gl.GL_LINE_STRIP)
        for i in range(iterations+1):
            gl.glVertex2f(x + dx, y + dy)
            dx, dy = (dx*c - dy*s), (dy*c + dx*s)
        gl.glEnd()

def pridej_asteroid(dt):
    global vesmir
    K = 0.20 # cca 25 %
    OKRAJ  = 20 # od okraje počet pixelů
    TIME = 0.5

    xx, yy = random.choice([(0,1), (1,0)])
    x = random.randrange(OKRAJ, WIDTH - OKRAJ)  * xx
    y = random.randrange(OKRAJ, HEIGHT- OKRAJ) * yy
    if x == 0:
        r = random.uniform(-math.pi/2 + K , math.pi/2 - K)
    elif y == 0:
        r = random.uniform(0 + K, math.pi - K)

    vesmir += Asteroid(x, y, direction=r)
    print(vesmir)   
    pyglet.clock.schedule_once(pridej_asteroid, TIME)

window.push_handlers(
    on_key_press=stisk_klavesy,
    on_key_release=uvolneni_klavesy,
    on_draw=vykresli)

batch = pyglet.graphics.Batch()
background = pyglet.graphics.OrderedGroup(0) # batch group
foreground = pyglet.graphics.OrderedGroup(1) # batch group

vesmir = Space(img='space1.jpg') 
vesmir += SpaceShip(img='ship2.png', x=WIDTH//2, y=HEIGHT//2)

pyglet.clock.schedule_interval(vesmir.tik, 1/30)
pyglet.clock.schedule_once(pridej_asteroid, 3)

pyglet.app.run()
