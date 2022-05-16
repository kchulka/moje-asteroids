#!/usr/bin/env python3
# ------- make exe files: auto-py-to-exe

import pyglet
from pyglet.window import key
from pyglet import gl
from pyglet import window

import yaml
from yaml import Loader

import random
import time
import math

# -- import settings from file

class gamesettings:
    def __init__(self):
        self.file = open('resources/gamesettings.yml', 'r')
        self.data = yaml.load(self.file, Loader=Loader)
        #print(self.data)
gamesettings = gamesettings()


# -- game run

run = False

# -- window settings --
display = pyglet.canvas.get_display()
screens = display.get_screens()
window_data = gamesettings.data.get("WINDOW_SETTINGS")
if window_data.get("FULLSCREEN") == True:
    window = pyglet.window.Window(width=window_data.get("WIDTH"), height=window_data.get("HEIGHT"), resizable=window_data.get("RESIZABLE"), fullscreen=window_data.get("FULLSCREEN"), screen=screens[int(window_data.get("MONITOR"))], style=pyglet.window.Window.WINDOW_STYLE_DIALOG )
else:
    window = pyglet.window.Window(width=window_data.get("WIDTH"), height=window_data.get("HEIGHT"), resizable=window_data.get("RESIZABLE") )
# -- Resource variables --

asteroid_images = "resources/meteors/['meteorBrown_big1.png', 'meteorBrown_med1.png', 'meteorBrown_small1.png', 'meteorBrown_tiny1.png']"
asteroid_images += "resources/meteors/['meteorGrey_big2.png', 'meteorGrey_med2.png', 'meteorGrey_small2.png', 'meteorGrey_tiny2.png']"


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



class SpaceObject:
# Objects properities

    def __init__(self, img, x=0, y=0, speed=0, rotation=0, group=None):
        self.image = pyglet.image.load(img)
        self.x = x
        self.y = y
        #self.centering_image()
        if group == None:
            group=foreground
        self.sprite = pyglet.sprite.Sprite(img=self.image, batch=batch, group=group)
        self.rotation = rotation
        self.speed = speed
        self.radius = max([self.sprite.width, self.sprite.height]) / 2

    def centering_image(self):
        """ centering of image """
        self.image.anchor_x = self.image.width // 2
        self.image.anchor_y = self.image.height // 2
        if self.x - self.image.anchor_x < 0:
            self.x = self.image.anchor_x
        elif self.x + self.image.anchor_x > window.width:
            self.x = window.width - self.image.anchor_x
        if self.y - self.image.anchor_y < 0:
            self.y = self.image.anchor_y
        elif self.y + self.image.anchor_y > window.height:
            self.y = window.height - self.image.anchor_y

    def out_of_window(self):
        """ objekt mimo okno aplikace """
        if self.x > window.width:
            self.x = self.sprite.x = 0
        elif self.x < 0:
            self.x = self.sprite.x = window.width
        elif self.y > window.height:
            self.y = self.sprite.y = 0
        elif self.y < 0:
            self.y = self.sprite.y = window.height

# Space.HEIGHT bylo nahrazeno window.height


    def tik(self, dt):
        # -- Objects movement calculations --
        self.x += self.speed * math.cos(self.rotation)
        self.y += self.speed * math.sin(self.rotation)

        # -- parametry sprite --
        self.sprite.rotation = 90 - math.degrees(self.rotation)
        self.sprite.x = self.x
        self.sprite.y = self.y

        self.out_of_window()




class SpaceShip(SpaceObject):
## -- space ship --
    ship = gamesettings.data.get('ship')
    # -- Movement values
    ROTATION_SPEED  = ship.get('ROTATION_SPEED') # radians/sec
    ACCELERATION    = ship.get('ACCELERATION')
    BREAKS          = ship.get('BREAKS')
    # -- Movement values
    controls = gamesettings.data.get('ship').get("controls")

    controls_forward = int(controls.get("forward"))
    controls_backward = int(controls.get("backward"))
    controls_left = int(controls.get("left"))
    controls_right = int(controls.get("right"))
    # -- Space ship images
    img             = 'resources/spaceships/playerShip1_blue.png'


    def __init__(self, img, x=0, y=0, management=dict()):
        super().__init__(self.img, x, y)

        self.sprite.image.width = window.height//self.ship.get("SIZE")
        self.sprite.image.height = window.height//self.ship.get("SIZE")

        self.centering_image()

        if len(management) == 0:
            self.management = {'left': self.controls_left, 'right': self.controls_right, 'forward': self.controls_forward, 'backward': self.controls_backward, "shoot": key.SPACE}
        else:
            self.management = management



    def centering_image(self):
        """ centering of image """
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



    def tik(self, dt):
        self.sprite.image.width = window.height//self.ship.get("SIZE")
        self.sprite.image.height = window.height//self.ship.get("SIZE")
        if self.management['left'] in pushed_keys:
            """ rotace vlevo """
            self.rotation -= dt * SpaceShip.ROTATION_SPEED

        if self.management['right'] in pushed_keys:
            """ rotace vpravo """
            self.rotation += dt * SpaceShip.ROTATION_SPEED

        if self.management['forward'] in pushed_keys:
            self.speed += dt * SpaceShip.ACCELERATION


        if self.management['backward'] in pushed_keys:
            if self.speed > 1:
                self.speed -= dt * SpaceShip.BREAKS
            else:
                self.speed = 0

        super().tik(dt)

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
background = pyglet.graphics.OrderedGroup(0)  # batch group
foreground = pyglet.graphics.OrderedGroup(1)  # batch group



# -- ticks --

def rungame():
    global Space
    Space = Space()
    Space += SpaceShip(img=SpaceShip.img, x=window.width // 2, y=window.height // 2)
    pyglet.clock.schedule_interval(Space.tik, 1/gamesettings.data.get("WINDOW_SETTINGS").get("TICKSPEED"))

# -- run application --
pyglet.app.run()
