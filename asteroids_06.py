#!/usr/bin/env python3
"""
verze 06

- zničení asteroidu pomocí laseru
- metoda Asteroid.hit_by_laser()
- metoda zjištění kolize laseru a asteroidu - Laser.check_collision()
"""
import pyglet
from pyglet.window import key
from pyglet import gl
import math
import random

# -- nový Asteroid --
K       = 0.20  # cca 25 % - min natočení asteroidu
OKRAJ   = 20    # počet pixelů od kraje
TIME    = 1     # sec - čas mezi tvořením asteroidů

class SpaceObject:
    """ třída SpecObject - vesmírný objekt """

    def __init__(self, img, x=0, y=0, speed=0, rotation=0, group=None):
        self.image = pyglet.image.load(img) 
        self.x = x
        self.y = y
        self.centering_image()
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
        elif self.x + self.image.anchor_x > Space.WIDTH:
            self.x = Space.WIDTH - self.image.anchor_x
        if self.y - self.image.anchor_y < 0:
            self.y = self.image.anchor_y
        elif self.y + self.image.anchor_y > Space.HEIGHT:
            self.y = Space.HEIGHT - self.image.anchor_y

    def __str__(self):
        return str(self.__repr__())

    def __repr__(self):
        return "SpaceObject({}, {}, {})".format(self.x, self.y)              
 
    def __del__(self):
        self.sprite.delete()

    def delete(self):
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

        self.out_of_window()

    def hit_by_spaceship(self, space_ship):
        """ srážka objektu s vesmírnou lodí """
        pass

    def hit_by_laser(self, laser):
        """ objekt je zasažen laserem """
        pass

    def out_of_window(self):
        """ objekt mimo okno aplikace """
        if self.x > Space.WIDTH:
            self.x = self.sprite.x = 0
        elif self.x < 0:
            self.x = self.sprite.x = Space.WIDTH
        elif self.y > Space.HEIGHT:
            self.y = self.sprite.y = 0
        elif self.y < 0:
            self.y = self.sprite.y = Space.HEIGHT

class SpaceShip(SpaceObject):
    """ třída SpaceShip - vesmírná loď """

    SPACESHIP_IMAGE = [
        'playerShip1_green.png', 'playerShip1_orange.png', 'playerShip1_red.png', 'playerShip3_blue.png'] 
    ROTATION_SPEED      = 4 # akcelerace rotace rakety - radiánů za sekundu
    ACCELERATION        = 5 # akcelerace rychlosti rakety 
    DEFAULT_MANAGEMENT  = {'left':key.LEFT, 'right':key.RIGHT, 'forward':key.UP, 'backward':key.DOWN, 'shot':key.SPACE}

    def __init__(self, img=None,x=0, y=0, management=None, images=SPACESHIP_IMAGE):
        if img == None:
            img = random.choice(images)
        if management == None:
            self.management = SpaceShip.DEFAULT_MANAGEMENT
        else:
            self.management = management

        self.lasers = []
        self.shot_delay = 0
        super().__init__(img, x, y, rotation=math.pi/2) 

    def __repr__(self):
        return "SpaceShip({}, {}, {})".format(self.x, self.y, self.lasers)              

    def check_collision(self):
        """ srazila se lod s nějakým objektem? """
        for space_object in vesmir.objects:
            if overlaps(self, space_object):
                space_object.hit_by_spaceship(self)

    def tik(self, dt):
        
        if self.shot_delay > 0:
            self.shot_delay -= 1

        if self.management['left'] in stisknute_klavesy:
            """ rotace vlevo """
            self.rotation += dt * SpaceShip.ROTATION_SPEED
        
        if self.management['right'] in stisknute_klavesy:
            """ rotace vpravo """
            self.rotation -= dt * SpaceShip.ROTATION_SPEED
        
        if self.management['forward'] in stisknute_klavesy:
            """ zvýšení rychlosti """
            self.speed += dt * SpaceShip.ACCELERATION

        else:
            """ snížení rychlosti """
            self.speed = self.speed - dt * SpaceShip.ACCELERATION if self.speed > 0 else 0 
        
        if self.management['shot'] in stisknute_klavesy:
            self.shot()

        super().tik(dt)
        self.check_collision()
 
        # -- lasery --
        for laser in self.lasers:
            laser.tik(dt)
            laser.check_collision()

    def shot(self):
        """ výstřel """
        if self.shot_delay == 0:
            self.shot_delay = Laser.LASER_DELAY
            self.lasers += [ Laser(self) ]

    def delete(self):
        [ laser.delete() for laser in self.lasers ]
        super().delete()

class Asteroid(SpaceObject):
    """ třída Asteroid - asteroid """
    
    ASTEROID_IMAGE  =  [
        'meteorBrown_big1.png', 'meteorBrown_med1.png', 'meteorBrown_small1.png', 'meteorBrown_tiny1.png'] 
    ASTEROID_IMAGE += [
        'meteorGrey_big2.png', 'meteorGrey_med2.png', 'meteorGrey_small2.png', 'meteorGrey_tiny2.png'] 

    def __init__(self, x, y, direction=0, images=ASTEROID_IMAGE):
        img = random.choice(images)
        speed = random.randint(2,30)
        self.sprite_rotation = random.randint(0,10)
        self.rotate_speed = random.random() * 5.0 - 3.0
        super().__init__(img, x, y, speed=speed, rotation=direction)

    def __repr__(self):
        return "Asteroid({}, {})".format(self.x, self.y)              

    def tik(self, dt):
        super().tik(dt)            
        
        # rotace asteroidu kolem svého středu
        self.sprite_rotation += self.rotate_speed * dt
        self.sprite.rotation = 90 - math.degrees(self.sprite_rotation)

    def hit_by_laser(self, laser):
        """ zasažen laserem """
        self.delete()

    def hit_by_spaceship(self, space_ship):
        """ srážka s vesmírnou lodí - zničení spaceship """
        space_ship.delete()
    
    def out_of_window(self):
        """ asteroid mimo okno aplikace """
        if self.x < 0 or self.x > Space.WIDTH or self.y < 0 or self.y > Space.HEIGHT:
            self.delete()
   
class Laser(SpaceObject):
    """ třída Laser - střela """
    
    LASER_IMAGE = ['laserBlue13.png', 'laserGreen03.png', 'laserRed13.png']
    LASER_SPEED = 30
    LASER_DELAY = 15

    def __init__(self, spaceship, img=None):
        if img == None:
            img = random.choice(Laser.LASER_IMAGE)
        self.spaceship = spaceship
        super().__init__(img, x=spaceship.x, y=spaceship.y, speed=spaceship.speed + Laser.LASER_SPEED, rotation=spaceship.rotation, group=lasers_group)

    def __repr__(self):
        return "Laser({}, {})".format(self.x, self.y)              

    def delete(self):
        self.spaceship.lasers.remove(self)
        del self

    def out_of_window(self):
        """ střela mimo okno """
        if self.x < 0 or self.x > Space.WIDTH or self.y < 0 or self.y > Space.HEIGHT:
            self.delete()

    def check_collision(self):
        """ kolize laseru s ostatním vesmírným objektem """
        for space_object in vesmir.objects:
            if overlaps(self, space_object):
                space_object.hit_by_laser(self)

class Space:
    """ třída Space - Vesmír """
 
    DEFAULT_SPACE = 'space1.jpg'

    def __init__(self, img=DEFAULT_SPACE, objects=[]):
        self.objects = objects
        self.image = pyglet.image.load(img)
        self.sprite = pyglet.sprite.Sprite(self.image, batch=batch, group=background)
        Space.WIDTH = self.image.width
        Space.HEIGHT = self.image.height
        
    def __iadd__(self, other):
        """ přidá vesmírný objekt do seznamu """
        self.objects += [other]
        return self

    def __str__(self):
        return str(self.__repr__())

    def __repr__(self):
        return "Space({})".format(self.objects)

    def tik(self, dt):
        """ tik vesmíru """
        for space_object in self.objects:
            space_object.tik(dt)                # tik všech objektů ve vesmíru      
 
        if key.PLUS in stisknute_klavesy:       # pokud není raketa ve vesmíru, tak přidáme
            if  len([o for o in self.objects if isinstance(o, SpaceShip)]) == 0:
                self.objects += [SpaceShip(x=Space.WIDTH//2, y=Space.HEIGHT//2)]

# -- definice funkcí --

def distance(a, b, wrap_size):
    """ vzdálenost v jednom směru osy (x nebo y) """
    result = abs(a - b)
    if result > wrap_size / 2:
        result = wrap_size - result
    return result

def overlaps(a, b):
    """ test překrytí objektů """
    distance_squared = (distance(a.x, b.x, window.width) ** 2 +
                        distance(a.y, b.y, window.height) ** 2)
    max_distance_squared = (a.radius + b.radius) ** 2
    return distance_squared < max_distance_squared

def draw_circle(x, y, radius):
    """ pomocná funkce pro kreslení kolečka """
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
    """ přidá asteroid do vesmíru """
    global vesmir
        
    xx, yy = random.choice([(0,1), (1,0)])
    x = random.randrange(OKRAJ, Space.WIDTH - OKRAJ)  * xx
    y = random.randrange(OKRAJ, Space.HEIGHT- OKRAJ) * yy
    if x == 0:
        r = random.uniform(-math.pi/2 + K , math.pi/2 - K)
    elif y == 0:
        r = random.uniform(0 + K, math.pi - K)

    vesmir += Asteroid(x, y, direction=r)
    #print(vesmir)   
    pyglet.clock.schedule_once(pridej_asteroid, TIME)


# -- funkce - ovladače pro události --

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
            #[draw_circle(space_object.x, space_object.y, space_object.radius) for space_object in vesmir.objects]

            # Restore remembered state (this cancels the glTranslatef)
            gl.glPopMatrix()

# -- hlavni program --

batch = pyglet.graphics.Batch()
background   = pyglet.graphics.OrderedGroup(0)
lasers_group = pyglet.graphics.OrderedGroup(1)
foreground   = pyglet.graphics.OrderedGroup(2)

vesmir = Space('image6.jpg') 
vesmir += SpaceShip(x=Space.WIDTH//2, y=Space.HEIGHT//2)

window = pyglet.window.Window(width=Space.WIDTH, height=Space.HEIGHT)
window.push_handlers(
    on_key_press=stisk_klavesy,
    on_key_release=uvolneni_klavesy,
    on_draw=vykresli)

stisknute_klavesy = set()

pyglet.clock.schedule_interval(vesmir.tik, 1/60)
pyglet.clock.schedule_once(pridej_asteroid, 3)

pyglet.app.run()
