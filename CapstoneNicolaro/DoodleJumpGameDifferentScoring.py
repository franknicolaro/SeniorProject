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
SPEED_SCALAR = 2
background = ALMOND

class Player(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y, file_name):
        super().__init__()
        self.temp = pygame.image.load_extended(file_name)
        #self.image = pygame.transform.scale_by(self.temp, 0.05)
        self.image = pygame.transform.scale(self.temp, (width, height))
        self.rect = self.image.get_rect()
        self.rect.bottom = y + height
        self.rect.x = x
        self.player_rect = pygame.Rect(x, self.rect.bottom, width, 1)
        #self.rect = pygame.Rect(x, self.old_rect.bottom, width, 1)

class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y, file_name):
        super().__init__()
        self.temp = pygame.image.load_extended(file_name)
        #self.image = pygame.transform.scale_by(self.temp, 0.35)
        self.image = pygame.transform.scale(self.temp, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
class DoodleJump():
    
    def __init__(self):
        self.font = pygame.font.Font("Bubblegum.ttf", 16)
        
        #Screen
        self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption("Doodle Jump")

        #load player image and fps
        self.group = pygame.sprite.Group()
        self.platform_group = pygame.sprite.Group()
        
        self.platform_base = pygame.transform.scale(pygame.image.load("Platform.png"), (105, 75))
        self.fps = 60

        #Timer to keep fps in check
        self.timer = pygame.time.Clock()

        #[self.platform_base, 50, 450], [self.platform_base, 145, 310], [self.platform_base, 275, 170],
                        #[self.platform_base, 50, 30], [self.platform_base, 135, -110], [self.platform_base, 400, -250]
        # game variables
        self.player_x = 50
        self.player_y = 370
        self.platforms = []
        gap = 140
        x = 0
        for platform in range(5):
            platform = Platform(80, 20, (random.randint(0, 495)), 450 - (gap * x), "Platform.png")
            self.platform_group.add(platform)
            self.platforms.append(platform)
            x += 1
        self.player = Player(50, 60, self.platforms[0].rect.x, 370, "PlayerSprite.png")
        self.group.add(self.player)
        self.jump = False
        self.change_y = 0
        self.change_x = 0
        self.player_speed = 4
        self.score = 0
        self.game_end = False
        self.lastPlatformIndex = 0
        self.previousLastIndex = 0
        self.timeWasting = 0
        self.firstCollision = False
        self.boing = pygame.mixer.Sound("Boing.ogg")

        

    def update_player(self):
        jump_height = 10 
        gravity = 0.2 * SPEED_SCALAR
        if(self.jump):
            self.change_y = -jump_height
            if(not self.firstCollision):
                self.firstCollision = True
            self.jump = False
        self.player.player_rect.y += self.change_y * SPEED_SCALAR
        self.player.rect.y += self.change_y * SPEED_SCALAR
        self.change_y += gravity

    def check_collisions(self, canHeJump):
        for i in range(len(self.platforms)):
            if(self.player.player_rect.colliderect(self.platforms[i].rect)
                #and (self.player.rect.y >= self.platforms[i].rect.y + self.platforms[i].rect.height and self.player.rect.y <= self.platforms[i].rect.y)
                and canHeJump == False and self.change_y > 0):
                    canHeJump = True
                    pygame.mixer.Sound.play(self.boing)
                    self.previousLastIndex = self.lastPlatformIndex
                    self.lastPlatformIndex = i
                    if(self.lastPlatformIndex == self.previousLastIndex):
                        self.timeWasting += 1
                        if(self.timeWasting == 5):
                            self.g.fitness -= 1500
                            self.game_end = True
                    else:
                        self.timeWasting = 0
        return canHeJump
        
    def update_platforms(self, plat_list, y, delta):
        if(y < 250 and delta < 0):
            for i in range(len(plat_list)):
                plat_list[i].rect.y -= delta
            self.score += 1 
            self.g.fitness += 1
            self.player.player_rect.y -= delta
            self.player.rect.y -= delta
        else:
            pass
    
        for k in range(len(plat_list)):
            if(plat_list[k].rect.y > 600):
                plat_list[k].rect.x = random.randint(0, 495)
                plat_list[k].rect.y = -140
        return plat_list

    #TODO: fix varibale names
    def runGame(self, g, network):
        running = True
        self.g = g
        self.network = network
        while (running == True):
            self.timer.tick(self.fps * SPEED_SCALAR)
            self.screen.fill(background)
            score_label = self.font.render('Score: ' + str(self.score), True, BLACK, background)
            self.screen.blit(score_label, (480, 20))
    
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
                dist = abs(self.player.rect.centerx - self.platforms[0].rect.centerx)
                dist_wrap = min((self.player.rect.centerx + (680 - self.platforms[0].rect.centerx)),
                                ((680 - self.player.rect.centerx) + self.platforms[0].rect.centerx))
            else:
                dist = abs(self.player.rect.centerx - self.platforms[self.lastPlatformIndex + 1].rect.centerx)
                dist_wrap = min((self.player.rect.centerx + (680 - self.platforms[self.lastPlatformIndex + 1].rect.centerx)),
                                ((680 - self.player.rect.centerx) + self.platforms[self.lastPlatformIndex + 1].rect.centerx))
            
            output = self.network.activate((self.player.rect.x, self.player.rect.y, dist, dist_wrap))
            
            if((max(output[0], output[1], output[2]) == output[0]) and self.firstCollision):
                self.change_x = -self.player_speed * SPEED_SCALAR
            elif((max(output[0], output[1], output[2]) == output[1]) and self.firstCollision):
                self.change_x = self.player_speed * SPEED_SCALAR
            else:
                self.change_x = 0
    
            self.jump = self.check_collisions(self.jump)
            self.player.rect.x += self.change_x
            self.player.player_rect.x = self.player.rect.x
            if(self.player.rect.x > 600):
                self.player.rect.x = -80
                self.player.player_rect.x  = -80
            elif(self.player.rect.x < -80):
                self.player.rect.x = 600
                self.player.player_rect.x = 600
        
            if self.player.rect.y < 520:
                self.update_player()
            else:
               self.game_end = True
               self.change_y = 0
               self.change_x = 0
        
            self.platforms = self.update_platforms(self.platforms, self.player.rect.y, self.change_y * SPEED_SCALAR)
    
            if(self.change_x > 0):
                self.player.image = pygame.transform.flip(self.player.image, 0, 0)
            elif(self.change_x < 0):
                self.player.image = pygame.transform.flip(self.player.image, 1, 0)
            self.group.draw(self.screen)
            self.platform_group.draw(self.screen)
            pygame.draw.rect(self.screen, (255,0,0), self.player.player_rect)
            #pygame.draw.rect(self.screen, (255,0,0), self.platforms[0].rect)
            pygame.display.flip()
            if(self.game_end):
               running = False
        
        pygame.quit()
        
def main(g, network):
    pygame.init()
    doodle_jump = DoodleJump()
    doodle_jump.runGame(g, network)

def play_gen(genomes, config):
    for _, g in genomes:
        network = neat.nn.FeedForwardNetwork.create(g, config)
        g.fitness = 0
        main(g, network)
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
    #pygame.mixer.music.load()
    most_fit = population.run(play_gen, 200)
    
    print("most fit is: ", most_fit)
    pass

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    run_config(config_path)
    
