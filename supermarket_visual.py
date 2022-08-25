## Visualization
import pygame, sys
from pygame.locals import *
import time
import random
import pandas as pd
import numpy as np
import itertools
 
P = pd.read_csv('data/trans_matrix.csv', index_col=0)

pygame.init()
vec = pygame.math.Vector2 
 
HEIGHT = 780
WIDTH = 1052
FRIC = -0.12
FPS = 60

customers = []

counter = 0
 
bg = pygame.image.load("data/market.png")

FramePerSec = pygame.time.Clock()
 
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Supermarket Simulation Markov Model")

x_locations = {'fruit': 843, 'spices': 589, 'dairy': 436, 'drinks': 202, 'entry': 843, 'checkout': 436}

class Customer(pygame.sprite.Sprite):
    def __init__(self, number = 0):
        super().__init__() 
        self.surf = pygame.Surface((20, 20))

        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        self.speed = 7

        self.surf.fill((r,g,b))
        self.rect = self.surf.get_rect()
   
        start_y = random.randint(630,670)
        self.pos = vec((843, start_y))
        self.vel = vec(0,0)
        self.acc = vec(0,0)

        self.current_location = "entry"
        self.moving = False
        self.going_to_hallway = False
        self.going_sideways_to_section = False
        self.going_down_to_section = False
        self.initialized_movement = True
        self.new_location='entry'
        self.number = number

    def move(self):
        self.acc = vec(0,0)
        self.rect.midbottom = self.pos

    def move_up(self):
        self.acc.y = -self.speed
        self.acc.x += self.vel.x * FRIC
        self.vel = self.acc
        self.pos += self.vel + 0.5 * self.acc 

    def move_down(self):
        self.acc.y = self.speed
        self.acc.x += self.vel.x * FRIC
        self.vel = self.acc
        self.pos += self.vel + 0.5 * self.acc

    def move_sideways(self, direction):
        if direction == 'right':
            self.acc.x = self.speed
        else:
            self.acc.x = -self.speed
        self.acc.x += self.vel.x * FRIC
        self.vel = self.acc
        self.pos += self.vel + 0.5 * self.acc 


    def move_to_location(self, next_location):
        if self.current_location == next_location:
            self.moving = False
            self.acc = vec(0,0)
            self.vel = vec(0,0)
            self.pos += self.vel
            self.initialized_movement = True
        else: 
            if self.initialized_movement == True:
                self.moving = True
                self.going_to_hallway = True
                self.going_down_to_section = False
                self.going_sideways_to_section = False
                self.initialized_movement = False
            
            if self.moving and self.going_to_hallway and not self.going_sideways_to_section and not self.going_down_to_section:
                self.move_up()
                if 140 <= self.pos.y <= 150:
                    self.going_to_hallway = False
                    self.going_sideways_to_section = True

            if self.moving and not self.going_to_hallway and self.going_sideways_to_section and not self.going_down_to_section:
                if x_locations.get(next_location) > x_locations.get(self.current_location):
                    self.move_sideways('right')
                else:
                    self.move_sideways('left')
                if x_locations.get(next_location)-20 <= self.pos.x <= x_locations.get(next_location)+20:
                    self.going_sideways_to_section = False
                    self.going_down_to_section = True

            if self.moving and not self.going_to_hallway and not self.going_sideways_to_section and self.going_down_to_section:
                self.move_down()
                if self.new_location == 'checkout':
                    if 640 <= self.pos.y <= 660:
                        self.going_to_hallway = False
                        self.moving = False
                        self.going_down_to_section = False
                        self.going_sideways_to_section = False
                        self.current_location = next_location
                else:
                    lowest_random = random.randint(290,540)
                    if lowest_random <= self.pos.y:
                        self.going_to_hallway = False
                        self.moving = False
                        self.going_down_to_section = False
                        self.going_sideways_to_section = False
                        self.current_location = next_location

            if self.current_location == next_location:
                self.moving = False
                self.acc = vec(0,0)
                self.vel = vec(0,0)
                self.pos += self.vel
                self.initialized_movement = True
                self.new_location = self.current_location
    
class game_object(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.make_new_when_left = True
    
    def press_key_to_make(self):
        pressed_keys = pygame.key.get_pressed()       
        if pressed_keys[K_SPACE]:
            customers.append(Customer(counter))
            last_customer = customers[-1]
            all_sprites.add(last_customer)
        if pressed_keys[K_c]:
            if self.make_new_when_left == True:
                self.make_new_when_left = False
            else:
                self.make_new_when_left = True
            time.sleep(0.09)
        

PT1 = game_object()

score_font = pygame.font.Font(None, 35)
score_font_options = pygame.font.Font(None, 20)

all_sprites = pygame.sprite.Group()

amount_of_initial_cust = int(sys.argv[1])

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    counter += 1

    if counter % 150 == 0:
        for customer in customers:
            customer.new_location = np.random.choice(list(P.index), p=P.loc[customer.current_location])

    for customer in customers:
        customer.move_to_location(customer.new_location)

    if counter == 10:
        for i in range(amount_of_initial_cust):
            customers.append(Customer(counter))
            last_customer = customers[-1]
            all_sprites.add(last_customer)

    for customer in customers:
        customer.move()
        if customer.current_location == 'checkout':
            if PT1.make_new_when_left == True:
                customers.append(Customer(counter))
                last_customer = customers[-1]
                all_sprites.add(last_customer)
            customers.remove(customer)
            all_sprites.remove(customer)

    PT1.press_key_to_make()

    displaysurface.blit(bg, (0, 0))

    score_surf = score_font.render(str("Minute: " + str(int(counter/150))), 1, (0, 0, 0))
    score_pos = [10, 7]
    displaysurface.blit(score_surf, score_pos)

    amount_surf = score_font.render(str("Customers: " + str(len(customers))), 1, (0, 0, 0))
    amount_pos = [240, 7]
    displaysurface.blit(amount_surf, amount_pos)

    if PT1.make_new_when_left == True:
        option_text = 'on'
    else:
        option_text = 'off'

    option_surf = score_font_options.render(str("Add new customers for every checked out customer (press c): " + option_text), 1, (0, 0, 0))
    option_pos = [620, 12]
    displaysurface.blit(option_surf, option_pos)

    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)

    pygame.display.update()
    FramePerSec.tick(FPS) 
    