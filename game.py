#!/usr/bin/env python3
# ------- make exe files: auto-py-to-exe

import pyglet
from pyglet.window import key
from pyglet import gl
from pyglet import window

import yaml
from yaml import Loader

#import random
import math

# -- import settings from file

class gamesettings:
    def __init__(self):
        self.file = open('resources/gamesettings.yml', 'r')
        self.data = yaml.load(self.file, Loader=Loader)
        #print(self.data)
gamesettings = gamesettings()

# -- window settings --
display = pyglet.canvas.get_display()
screens = display.get_screens()
window_data = gamesettings.data.get("WINDOW_SETTINGS")
if window_data.get("FULLSCREEN") == True:
    window = pyglet.window.Window(width=window_data.get("WIDTH"), height=window_data.get("HEIGHT"), resizable=window_data.get("RESIZABLE"), fullscreen=window_data.get("FULLSCREEN"), screen=screens[int(window_data.get("MONITOR"))], style=pyglet.window.Window.WINDOW_STYLE_DIALOG )
else:
    window = pyglet.window.Window(width=window_data.get("WIDTH"), height=window_data.get("HEIGHT"), resizable=window_data.get("RESIZABLE") )

# -- Classes --

class Space:

    def __init__(self, img=None, objects=[]):
        self.objects = objects
        #if img == None:
        #    img = random.choice(Space.SPACE_IMAGE)
        if img != None:
            self.image = pyglet.image.load(img)
            self.sprite = pyglet.sprite.Sprite(self.image, batch=batch, group=background)
            Space.WIDTH = self.image.width
            Space.HEIGHT = self.image.height

    def __iadd__(self, other):
        self.objects += [other]
        return self

    def tik(self, dt):
        for self.o in self.objects:
            self.o.tik(dt)

###############################################################################
#                               SPACE OBJECT
###############################################################################

class SpaceObject:
# Objects properities

    def __init__(self, img, x=0, y=0, speed=0, rotation=0, group=None):
        self.image = pyglet.image.load(img)
        self.x = x
        self.y = y
        if group == None:
            group=foreground
        self.sprite = pyglet.sprite.Sprite(img=self.image, batch=batch, group=group)
        self.rotation = rotation
        self.speed = speed
        self.radius = max([self.sprite.width, self.sprite.height]) / 2


    def __str__(self):
        return str(self.__repr__())


    def __repr__(self):
        return "SpaceObject({}, {}, {})".format(self.x, self.y)


    def __del__(self):
        self.sprite.delete()

    def hit_by_spaceship(self, space_ship):
        # -- hit by spaceship
        pass

    def hit_by_laser(self, laser):
        # -- object hit by laser
        pass

    def out_of_window(self):
        if self.x > window.width:
            self.x = self.sprite.x = 0
        elif self.x < 0:
            self.x = self.sprite.x = window.width
        elif self.y > window.height:
            self.y = self.sprite.y = 0
        elif self.y < 0:
            self.y = self.sprite.y = window.height

    def tik(self, dt):
        self.out_of_window()
        # -- Objects movement calculations --
        self.x += self.speed * math.cos(self.rotation)
        self.y += self.speed * math.sin(self.rotation)

        # -- parametry sprite --
        self.sprite.rotation = 90 - math.degrees(self.rotation)
        self.sprite.x = self.x
        self.sprite.y = self.y

###############################################################################
#                               SPACE SHIP
###############################################################################

class SpaceShip(SpaceObject):
## -- space ship --
    ship = gamesettings.data.get('ship')
    # -- Movement values
    ROTATION_SPEED  = ship.get('ROTATION_SPEED') # radians/sec
    MAX_SPEED       = ship.get("MAX_SPEED")
    ACCELERATION    = ship.get('ACCELERATION')
    BREAKS          = ship.get('BREAKS')
    # -- Movement values
    controls = gamesettings.data.get('ship').get("controls")

    controls_forward = int(controls.get("forward"))
    controls_backward = int(controls.get("backward"))
    controls_left = int(controls.get("left"))
    controls_right = int(controls.get("right"))
    controls_shoot = int(controls.get("shoot"))
    # -- Space ship images
    img             = 'resources/spaceships/playerShip1_blue.png'


    def __init__(self, img, x=window.width//2, y=window.height//2, management=dict()):
        super().__init__(img, x, y, rotation=math.pi/2)
        if len(management) == 0:
            self.management = {'left': self.controls_left, 'right': self.controls_right, 'forward': self.controls_forward, 'backward': self.controls_backward, 'shoot': self.controls_shoot}
        else:
            self.management = management
        self.sprite.image.anchor_x = self.sprite.image.width//2
        self.sprite.image.anchor_y = self.sprite.image.height//2
        self.lasers = []
        self.shoot_delay = 0
        super().__init__(img, x, y, rotation=math.pi/2)

    def centering_image(self):
        self.sprite.image.anchor_x = self.sprite.image.width//2
        self.sprite.image.anchor_y = self.sprite.image.height//2
        if self.x - self.image.anchor_x < 0:
            self.x = self.image.anchor_x
        elif self.x + self.image.anchor_x > window.width:
            self.x = window.width - self.image.anchor_x
        if self.y - self.image.anchor_y < 0:
            self.y = self.image.anchor_y
        elif self.y + self.image.anchor_y > window.height:
            self.y = window.height - self.image.anchor_y

    def out_of_window(self):
        if self.x > window.width:
            self.x = self.sprite.x = 0
        elif self.x < 0:
            self.x = self.sprite.x = window.width
        elif self.y > window.height:
            self.y = self.sprite.y = 0
        elif self.y < 0:
            self.y = self.sprite.y = window.height

    def __repr__(self):
        return "SpaceShip({}, {}, {})".format(self.x, self.y, self.lasers, self.sprite)

    def check_collision(self):
        for space_object in Space.objects:
            if overlaps(self, space_object):
                space_object.hit_by_spaceship(self)

    def tik(self, dt):
        self.out_of_window()
        if self.shoot_delay > 0:
            self.shoot_delay -= 1

        self.sprite.image.width = window.height//self.ship.get("SIZE")
        self.sprite.image.height = window.height//self.ship.get("SIZE")
        self.centering_image()

        if self.management['left'] in pushed_keys:
            """ rotace vlevo """
            self.rotation -= dt * self.ROTATION_SPEED
        if self.management['right'] in pushed_keys:
            """ rotace vpravo """
            self.rotation += dt * self.ROTATION_SPEED

        if self.management['forward'] in pushed_keys:
            if self.speed < self.MAX_SPEED - 1:
                self.speed += dt * SpaceShip.ACCELERATION
            else:
                self.speed = self.MAX_SPEED
        if self.management['backward'] in pushed_keys:
            if self.speed > 1:
                self.speed -= dt * self.BREAKS
            else:
                self.speed = 0

        if self.management['shoot'] in pushed_keys:
            self.shoot()

        super().tik(dt)
        #self.check_collision()

        for laser in self.lasers:
            laser.tik(dt)
            self.sprite.image.width = 1
            laser.check_collision()


    def shoot(self):
        """ výstřel """
        if self.shoot_delay == 0:
            self.shoot_delay = Laser.LASER_DELAY
            self.lasers += [ Laser(self) ]

    def delete(self):
        [ laser.delete() for laser in self.lasers ]
        super().delete()

###############################################################################
#                                  LASER
###############################################################################


class Laser(SpaceObject):

    LASER = gamesettings.data.get("LASER")
    LASER_IMAGE = 'resources/lasers/laserBlue01.png'
    img = 'resources/lasers/laserBlue01.png'
    LASER_SPEED = LASER.get("LASER_SPEED")
    LASER_DELAY = LASER.get("LASER_DELAY")
    LASER_SIZE = LASER.get("SIZE")

    def __init__(self, SpaceShip, img=None):
        if img == None:
            img = self.LASER_IMAGE
        super().__init__(self.img, x=SpaceShip.x, y=SpaceShip.y, speed=SpaceShip.speed + Laser.LASER_SPEED,
                         rotation=SpaceShip.rotation, group=lasers_group)
        self.sprite.image.width = window.height//SpaceShip.ship.get("SIZE")//self.LASER.get("SIZE2")
        self.sprite.image.height = window.height//SpaceShip.ship.get("SIZE")
        self.sprite.image.anchor_x = self.sprite.image.width//2
        self.sprite.image.anchor_y = self.sprite.image.height//4
        self.spaceship = SpaceShip

    def __repr__(self):
        return "Laser({}, {})".format(self.x, self.y)

    def delete(self):
        self.spaceship.lasers.remove(self)
        del self

    def out_of_window(self):
        if self.x < 0 or self.x > window.width or self.y < 0 or self.y > window.height:
            self.delete()

    def check_collision(self):
        for space_object in Space.objects:
            if overlaps(self, space_object):
                space_object.hit_by_laser(self)

    def centering_image(self):
        self.sprite.image.anchor_x = self.sprite.image.width//2
        self.sprite.image.anchor_y = self.sprite.image.height
        if self.x - self.image.anchor_x < 0:
            self.x = self.image.anchor_x
        elif self.x + self.image.anchor_x > window.width:
            self.x = window.width - self.image.anchor_x
        if self.y - self.image.anchor_y < 0:
            self.y = self.image.anchor_y
        elif self.y + self.image.anchor_y > window.height:
            self.y = window.height - self.image.anchor_y

    def tik(self, dt):
        super().tik(dt)
        self.out_of_window()
        if window.height//self.LASER.get("SIZE")//self.LASER.get("SIZE2") > 0:
            self.sprite.image.width = window.height//self.LASER.get("SIZE")//self.LASER.get("SIZE2")
        else:
            self.sprite.image.width = 1
        self.sprite.image.height = window.height//self.LASER.get("SIZE")
        self.centering_image()
        self.check_collision()


###############################################################################
#                               Something else
###############################################################################

def distance(a, b, wrap_size):
    # -- vzdálenost v jednom směru osy (x nebo y)
    result = abs(a - b)
    if result > wrap_size / 2:
        result = wrap_size - result
    return result

def overlaps(a, b):
    #překrytí objektů
    distance_squared = (distance(a.x, b.x, window.width) ** 2 +
                        distance(a.y, b.y, window.height) ** 2)
    max_distance_squared = (a.radius + b.radius) ** 2
    return distance_squared < max_distance_squared


# --- some keyboard things

pushed_keys = set()

def key_push(symbol, modifikatory):
    global pushed_keys, run
    pushed_keys.add(symbol)
    if run != True:
        run = True
        rungame()



def key_release(symbol, modifikatory):
    global pushed_keys
    pushed_keys.discard(symbol)

def draw():
    window.clear()

    for x_offset in (-window.width, 0, window.width):
        for y_offset in (-window.height, 0, window.height):
            # Remember the current state
            gl.glPushMatrix()
            # Move everything drawn from now on by (x_offset, y_offset, 0)
            gl.glTranslatef(x_offset, y_offset, 0)

            # Draw
            batch.draw()

            # Restore remembered state (this cancels the glTranslatef)
            gl.glPopMatrix()



window.push_handlers(
    on_key_press = key_push,
    on_key_release = key_release,
    on_draw = draw)



batch = pyglet.graphics.Batch()
background   = pyglet.graphics.OrderedGroup(0)
lasers_group = pyglet.graphics.OrderedGroup(1)
foreground   = pyglet.graphics.OrderedGroup(2)



# -- ticks --

run = False

def rungame():
    global Space
    Space = Space()
    Space += SpaceShip(img=SpaceShip.img, x=window.width // 2, y=window.height // 2)
    pyglet.clock.schedule_interval(Space.tik, 1/gamesettings.data.get("WINDOW_SETTINGS").get("TICKSPEED"))

# -- run application --
pyglet.app.run()
