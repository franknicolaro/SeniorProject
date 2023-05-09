import pygame
import random
import neat
import os
import math


#Constants
ALMOND = (239, 222, 205)
BLACK = (0, 0, 0)
WIDTH = 600
HEIGHT = 600
GAP_BETWEEN_PLATFORMS = 60
SPEED_SCALAR = 100000000000000
GEN = 0
background = ALMOND

class DoodleJump:
    
    def __init__(self):
        self.font = pygame.font.Font("Bubblegum.ttf", 16)

        #load player image and fps
        self.player = pygame.transform.scale(pygame.image.load("PlayerSprite.png"), (50, 60))
        self.platform_base = pygame.transform.scale(pygame.image.load("Platform.png"), (80, 20))
        self.fps = 60

        #Timer to keep fps in check
        self.timer = pygame.time.Clock()

        # game variables
        self.platforms = []
        gap = 180           #Gap variable to ensure platforms are a fair enough distance away
        x = 0               #x variable for the following for loop
        for platform in range(5):
            platform = [self.platform_base, (random.randint(0, 495)), 450 - (gap * x)]#Platform(80, 20, (random.randint(0, 495)), 450 - (gap * x), "Platform.png")
            self.platforms.append(platform)
            x += 1
        self.player_x = self.platforms[0][1]
        self.player_y = self.platforms[0][2] - 100
        self.jump = False
        self.change_y = 0
        self.change_x = 0
        self.player_speed = 3.5
        self.score = 0
        self.game_end = False
        self.lastPlatformIndex = 0
        self.previousLastIndex = 0
        self.timeWasting = 0
        self.firstCollision = False

        #Screen
        self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption("Doodle Jump")
        
        self.boing = pygame.mixer.Sound("Boing.ogg")

    def update_player(self, y):
        jump_height = 10
        gravity = 0.2 #* SPEED_SCALAR
        if(self.jump):
            self.change_y = -jump_height
            if(not self.firstCollision):
                self.firstCollision = True
            self.jump = False
        y += self.change_y #* SPEED_SCALAR
        self.change_y += gravity
        return y

    def check_collisions(self, plat_list, canHeJump):
        for i in range(len(plat_list)):
            if(self.player_y + 60 >= plat_list[i][2] and self.player_y + 60 <= plat_list[i][2] + 20): 
                if((self.player_x >= plat_list[i][1] - 50 and self.player_x <= plat_list[i][1] + 75)
                and canHeJump == False and self.change_y > 0):
                    canHeJump = True
                    pygame.mixer.Sound.play(self.boing)
                    self.previousLastIndex = self.lastPlatformIndex
                    self.lastPlatformIndex = i
                    if(self.lastPlatformIndex == self.previousLastIndex):
                        self.timeWasting += 1
                        if(self.timeWasting == 5):
                            self.g.fitness -= 500
                            self.game_end = True
                    else:
                        self.timeWasting = 0
        return canHeJump
        
    def update_platforms(self, plat_list, y, delta):
        if(y < 250 and delta < 0):
            for i in range(len(plat_list)):
                plat_list[i][2] -= delta
            self.player_y -= delta
            self.score += 1
            self.g.fitness += 1
        else:
            pass
    
        for k in range(len(plat_list)):
            if(plat_list[k][2] > 600):
                plat_list[k][1] = (random.randint(0, 495))
                plat_list[k][2] = plat_list[k - 1][2] - 180
                self.g.fitness += 5
        return plat_list

    def runGame(self, g, network, gen_no):
        running = True
        self.g = g
        self.network = network
        while (running == True):
            self.timer.tick(self.fps * SPEED_SCALAR)
            self.screen.fill(background)
            self.screen.blit(self.player, (self.player_x, self.player_y))
            score_label = self.font.render('Score: ' + str(self.score), True, BLACK, background)
            self.screen.blit(score_label, (480, 20))
            gen_label = self.font.render('Generation: ' + str(gen_no), True, BLACK, background)
            self.screen.blit(gen_label, (0, 20))
    
            for i in range(len(self.platforms)):
                self.screen.blit(self.platforms[i][0], (self.platforms[i][1], self.platforms[i][2]))
        
            """for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    running = False
                if (event.type == pygame.KEYDOWN):
                    if (event.key == pygame.K_LEFT):
                        self.change_x = -self.player_speed
                    if (event.key == pygame.K_RIGHT):
                       self.change_x = self.player_speed
                if (event.type == pygame.KEYUP):
                    if (event.key == pygame.K_LEFT):
                        self.change_x = 0
                    if (event.key == pygame.K_RIGHT):
                      self.change_x = 0"""
            if(self.lastPlatformIndex == 4):
                dist = (self.player_x - self.platforms[0][1])
                dist_wrap = min((self.player_x + (650 - self.platforms[0][1])),
                                ((650 - self.player_x) + self.platforms[0][1]))
                if(((self.player_x) + (650 - self.platforms[0][1])) >
                       ((650 - self.player_x) + (self.platforms[0][1]))):
                        dist_wrap = -(dist_wrap)
            else:
                dist = (self.player_x - self.platforms[self.lastPlatformIndex + 1][1])
                dist_wrap = min((self.player_x + (650 - self.platforms[self.lastPlatformIndex + 1][1])),
                                ((650 - self.player_x) + self.platforms[self.lastPlatformIndex + 1][1]))
                if(((self.player_x) + (650 - self.platforms[self.lastPlatformIndex + 1][1])) > 
                        ((650 - self.player_x) + (self.platforms[self.lastPlatformIndex + 1][1]))):
                        dist_wrap = -(dist_wrap)
            
            output = self.network.activate((self.player_x, self.player_y, dist, dist_wrap))
            
            if((max(output[0], output[1], output[2]) == output[0]) and self.firstCollision):
                self.change_x = -self.player_speed #* SPEED_SCALAR
            elif((max(output[0], output[1], output[2]) == output[1]) and self.firstCollision):
                self.change_x = self.player_speed #* SPEED_SCALAR
            else:
                self.change_x = 0
    
            self.jump = self.check_collisions(self.platforms, self.jump)
            self.player_x += self.change_x
            if(self.player_x > 600):
                self.player_x = -50
            elif(self.player_x < -50):
                self.player_x = 600
        
            if self.player_y < 520:
                self.player_y = self.update_player(self.player_y)
            else:
               self.game_end = True
               self.change_y = 0
               self.change_x = 0
        
            self.platforms = self.update_platforms(self.platforms, self.player_y, self.change_y) #* SPEED_SCALAR)
    
            if(self.change_x > 0):
                self.player = pygame.transform.scale(pygame.image.load("PlayerSprite.png"), (50, 60))
            elif(self.change_x < 0):
                self.player = pygame.transform.flip(pygame.transform.scale(pygame.image.load("PlayerSprite.png"), (50, 60)), 1, 0)
          
            pygame.display.flip()
            if(self.game_end or self.g.fitness > 50000):
               running = False
        
        pygame.quit()
        
def main(g, network, gen_no):
    pygame.init()
    doodle_jump = DoodleJump()
    doodle_jump.runGame(g, network, gen_no)

def play_gen(genomes, config):
    global GEN
    GEN += 1
    for _, g in genomes:
        network = neat.nn.FeedForwardNetwork.create(g, config)
        g.fitness = 0
        main(g, network, GEN)
        print("Fitness of Genome", g.fitness)
        
def run_config(config_path):
    
    #Load in the configuration file
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    
    #Declare the Population
    population = neat.Population(config)
    
    #Produces output for the population in each generation
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    
    #run the population
    most_fit = population.run(play_gen, 100)
    
    print("most fit is: ", most_fit)
    pass

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    run_config(config_path)
    
