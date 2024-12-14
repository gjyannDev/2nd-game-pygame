import pygame
from pygame.locals import *
import random
import os
import math 

pygame.init()
pygame.mixer.init()

# create the window
width = 900
height = 500
screen_size = (width, height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Buzz and Dodge')

GAME_BG = pygame.transform.scale(pygame.image.load(os.path.join("images", "game_bg.png")), (width, height)).convert_alpha()
MENU_BG = pygame.transform.scale(pygame.image.load(os.path.join("images", "menu_bg.png")), (width, height)).convert_alpha()

menu_music = pygame.mixer.Sound(os.path.join("sounds", 'menu_bg_music.wav'))
game_music = pygame.mixer.Sound(os.path.join("sounds", 'game_bg_music.wav'))

# colors
gray = (100, 100, 100)
green = (76, 208, 56)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)
blue = (0, 0, 255)

# road and marker sizes
road_width = 300
marker_width = 10
marker_height = 50

# lane coordinates
left_lane = 150
center_lane = 250
right_lane = 350
lanes = [left_lane, center_lane, right_lane]

# road and edge markers
road = (100, 0, road_width, height)
left_edge_marker = (95, 0, marker_width, height)
right_edge_marker = (395, 0, marker_width, height)

# for animating movement of the lane markers
lane_marker_move_y = 0

# player's starting coordinates
player_x = left_lane  
player_y = height - 300

# frame settings
clock = pygame.time.Clock()
fps = 120

# game settings
gameover = False
speed = 2
score = 0

bg_width = GAME_BG.get_width()
bg_rect = GAME_BG.get_rect()

scroll = 0
tiles = math.ceil(width  / bg_width) + 1

level = 1

# Define movement distance (adjustable)
move_distance = 100

class Vehicle(pygame.sprite.Sprite):
    
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        # scale the image down so it's not wider than the lane
        image_scale = 80 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (new_width, new_height))
        
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        
    def update(self):
        global score, level
        # Move the vehicle to the left
        self.rect.x -= 3  # Adjust speed for how fast you want it to move
        
        # Remove vehicle when it goes off-screen
        if self.rect.x < 0:
            score += 1
            self.kill()
        
        if score > 0 and score % 10 == 0:
            level = score // 10 + 1
            speed = 2 + (level - 1) * 0.5

class PlayerVehicle(Vehicle):
    
    def __init__(self, x, y):
        image = pygame.image.load('images/player.png')
        super().__init__(image, x, y)
        
# sprite groups
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()

# create the player's car
player = PlayerVehicle(player_x, player_y)
player_group.add(player)

# load the vehicle images
image_filenames = ['bird.png', 'bird.png', 'bird.png', 'bird.png']
vehicle_images = []
for image_filename in image_filenames:
    image = pygame.image.load('images/' + image_filename)
    vehicle_images.append(image)
    
# load the crash image
crash = pygame.image.load('images/crash.png')
crash_rect = crash.get_rect()

def mainMenu():

    running = True
    
    while running:

        game_music.stop()
        menu_music.play(-1)
        menu_music.set_volume(0.2)
    
        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
        
        screen.blit(MENU_BG, (0, 0))
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            game()
            
        if keys[pygame.K_q]:
            running = False
    
        pygame.display.update()

    pygame.quit()


def game():
    # game loop
    global score, gameover, speed, scroll, bg_width, tiles
    running = True
    while running:
        
        menu_music.stop()
        
        game_music.play(-1)
        game_music.set_volume(0.2)
        
        clock.tick(fps)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                
            # move the player's car using the left/right arrow keys
            if event.type == KEYDOWN:
                if event.key == K_UP and player.rect.top > 0:  # Check if the car is not at the top of the screen
                    # Move up but ensure it doesn't go beyond the top of the screen
                    player.rect.y -= move_distance
                    if player.rect.top < 0:  # Prevent car from going above the screen
                        player.rect.top = 0
                elif event.key == K_DOWN and player.rect.bottom < height:  # Check if the car is not at the bottom of the screen
                    # Move down but ensure it doesn't go beyond the bottom of the screen
                    player.rect.y += move_distance
                    if player.rect.bottom > height:  # Prevent car from going below the screen
                        player.rect.bottom = height

                        # check if there's a side swipe collision after changing lanes
                for vehicle in vehicle_group:
                    if pygame.sprite.collide_rect(player, vehicle):
                        gameover = True
                        
                        # place the player's car next to other vehicle
                        # and determine where to position the crash image
                        if event.key == K_LEFT:
                            player.rect.left = vehicle.rect.right
                            crash_rect.center = [player.rect.left, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
                        elif event.key == K_RIGHT:
                            player.rect.right = vehicle.rect.left
                            crash_rect.center = [player.rect.right, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
                            
                            
                
        #draw scrolling background
        for i in range(-1, tiles):
            screen.blit(GAME_BG, (i * bg_width + scroll, 0))
            bg_rect.x = i * bg_width + scroll

        #scroll background
        scroll += 1.5

        #reset scroll
        if scroll >= bg_width:
            scroll = 0
        # draw text
        
        # draw the player's car
        player_group.draw(screen)
        
        # add a vehicle if there aren't enough on the screen
        if len(vehicle_group) < 2:
            add_vehicle = True
            for vehicle in vehicle_group:
                if vehicle.rect.x > width / 2:
                    add_vehicle = False
            
            if add_vehicle:
                # spawn vehicle off-screen to the right
                lane = random.choice(lanes)
                image = random.choice(vehicle_images)
                vehicle = Vehicle(image, width + 100, lane)  # Start vehicles off-screen to the right
                vehicle_group.add(vehicle)
        
        # make the vehicles move to the left
        vehicle_group.update()
        
        # draw the vehicles
        vehicle_group.draw(screen)
        
        # display the score
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render('Score: ' + str(score), True, white)
        text_rect = text.get_rect()
        text_rect.center = (400, 30)
        screen.blit(text, text_rect)
        
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        level_text = font.render('Level: ' + str(level), True, white)
        level_text_rect = level_text.get_rect()
        level_text_rect.center = (500, 30)
        screen.blit(level_text, level_text_rect)
                
        
        # check if there's a head-on collision
        if pygame.sprite.spritecollide(player, vehicle_group, True):
            gameover = True
            crash_rect.center = [player.rect.center[0], player.rect.top]
                
        # display game over
        if gameover:
            screen.blit(crash, crash_rect)
            
            pygame.draw.rect(screen, green, (0, 50, width, 100))
            
            font = pygame.font.Font(pygame.font.get_default_font(), 16)
            text = font.render("Oh no you've been eaten, Play again? ( Y / N )", True, white)
            text_rect = text.get_rect()
            text_rect.center = (width / 2, 100)
            screen.blit(text, text_rect)
                
        pygame.display.update()

        # wait for user's input to play again or exit
        while gameover:
            
            clock.tick(fps)
            
            for event in pygame.event.get():
                
                if event.type == QUIT:
                    gameover = False
                    running = False
                    
                # get the user's input (y or n)
                if event.type == KEYDOWN:
                    if event.key == K_y:
                        # reset the game
                        gameover = False
                        speed = 2
                        score = 0
                        vehicle_group.empty()
                        player.rect.center = [player_x, player_y]
                    elif event.key == K_n:
                        # exit the loops
                        gameover = False
                        running = False

mainMenu()

pygame.quit()
