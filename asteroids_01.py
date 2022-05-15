#!/usr/bin/env python3
import pyglet
from pyglet.window import key
from pyglet import gl
import math
import random
import __future__


WIDTH  = 2560
HEIGHT = 1440

ROTATION_SPEED = 4 # radiánů za sekundu
ACCELERATION   = 5

class SpaceObject:
    """ vesmírný objekt """
    def __init__(self, img='resources/rockets/playerShip1_blue.png',x=0, y=0, speed=0, rotation=0):
        self.image = pyglet.image.load(img) 
        self.image.anchor_x = self.image.width // 2
        self.image.anchor_y = self.image.height // 2
        self.sprite = pyglet.sprite.Sprite(self.image, batch=batch, group=foreground)
        self.x = x
        self.y = y
        self.rotation = rotation
        self.speed = speed

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
    def __init__(self, img='resources/rockets/playerShip1_blue.png',x=0, y=0, management=dict()):
        super().__init__(img, x, y) 
        if len(management) == 0:
            self.management = {'left':key.LEFT, 'right':key.RIGHT, 'forward':key.UP, 'backward':key.DOWN}
        else:
            self.management = management

    def tik(self, dt):
        if self.management['left'] in stisknute_klavesy:
            """ rotace vlevo """
            self.rotation -= dt * ROTATION_SPEED
        
        if self.management['right'] in stisknute_klavesy:
            """ rotace vpravo """
            self.rotation += dt * ROTATION_SPEED
        
        if self.management['forward'] in stisknute_klavesy:
            """ zvýšení rychlosti """
            self.speed += dt * ACCELERATION

        if self.management['backward'] in stisknute_klavesy:
            """ snížení rychlosti """
            self.speed -= dt * ACCELERATION if self.speed > 0 else 0 
 
        super().tik(dt)

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

    def tik(self, dt):
        for self.o in self.objects:
            self.o.tik(dt)

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

            # Restore remembered state (this cancels the glTranslatef)
            gl.glPopMatrix()

window.push_handlers(
    on_key_press=stisk_klavesy,
    on_key_release=uvolneni_klavesy,
    on_draw=vykresli)

batch = pyglet.graphics.Batch()
background = pyglet.graphics.OrderedGroup(0) # batch group
foreground = pyglet.graphics.OrderedGroup(1) # batch group

vesmir = Space() 
vesmir += SpaceShip(img='resources/rockets/playerShip1_blue.png',  x=WIDTH//2, y=HEIGHT//2)

pyglet.clock.schedule_interval(vesmir.tik, 1/30)

pyglet.app.run()
