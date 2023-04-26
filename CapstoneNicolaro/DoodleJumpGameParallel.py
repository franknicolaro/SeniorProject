import pygame
import random
import neat
import os
import math


#Constants
ALMOND = (239, 222, 205)        #Background Color
BLACK = (0, 0, 0)               #Extra Color Option
WIDTH = 600                     #Width of Window
HEIGHT = 600                    #Height of Window
SPEED_SCALAR = 10000000000      #Scalar for entity movement
GEN = 0                         #Global to keep track of generation number
background = ALMOND             #Set the background to Almond

#Player class to keep track of player variables
class Player(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y, file_name):
        super().__init__()
        #Load and scale the image
        self.temp = pygame.image.load_extended(file_name)
        self.image = pygame.transform.scale(self.temp, (width, height))
        
        #create rectangle and set x and y coordinates
        self.rect = self.image.get_rect()
        self.rect.bottom = y + height
        self.rect.x = x
        self.rect.y = y
        self.player_rect = pygame.Rect(x, self.rect.bottom, width, 1)
        
        #Variables used for each player to determine their game state
        self.jump = False               #determines if the player should jump
        self.change_x = 0               
        self.change_y = 0
        self.lastPlatformIndex = 0      #Last platform that the player jumped on
        self.previousLastIndex = -1     #Variable to compare to lastPlatformIndex
        self.timeWasting = 0            #Variable to ensure the player is jumping on different platforms
        self.firstCollision = False     #Boolean check for the first collision when determining the output needed.

#Platform class which initializes the platforms
class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y, file_name):
        super().__init__()
        #Load and scale the platform image
        self.temp = pygame.image.load_extended(file_name)
        self.image = pygame.transform.scale(self.temp, (width, height))
        
        #create the rectangle and set x and y coordinates
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
#The class to play the game of Doodle Jump, to be run by the AI
class DoodleJump():
    
    def __init__(self, genomes, config, gen):
        
        #Set each of the self.variables to the parameters passed through
        self.gen = gen
        self.genomes = genomes
        self.config = config
        
        #Initialize the font used
        self.font = pygame.font.Font("Bubblegum.ttf", 16)
        
        #Initialize the Window
        self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption("Doodle Jump")

        #Initialize player group and platform group for drawing.
        self.group = pygame.sprite.Group()
        self.platform_group = pygame.sprite.Group()
        
        #Initialize fps and timer to keep fps in check
        self.fps = 60
        self.timer = pygame.time.Clock()

        #Initalize the platforms and add the array to the platform group
        self.platforms = []
        self.platform_group.add(self.platforms)
        gap = 180           #Gap variable to ensure platforms are a fair enough distance away
        x = 0               #x variable for the following for loop
        for platform in range(5):
            platform = Platform(80, 20, (random.randint(0, 495)), 450 - (gap * x), "Platform.png")
            self.platform_group.add(platform)
            self.platforms.append(platform)
            x += 1
            
        #Initialize all players, networks, and genomes of the generation
        self.players = []
        self.networks = []
        self.ge = []
        for _, g in self.genomes:
            #Create the network and append to self.networks
            network = neat.nn.FeedForwardNetwork.create(g, self.config)
            self.networks.append(network)
            
            #Append a new player to the self.players list
            self.players.append(Player(50, 60, self.platforms[0].rect.x, 370, "PlayerSprite.png"))
            
            #Define the fitness for the genome and append to self.ge
            g.fitness = 0
            self.ge.append(g)
            self.group.add(self.players[len(self.players) - 1])
            
        #Other Variables for keeping the game together
        self.player_speed = 3.1                         #Horizontal player speed
        self.score = 0                                  #Score variable for score label
        self.game_end = False                           #Variable to keep track of if the game has ended
        self.boing = pygame.mixer.Sound("Boing.ogg")    #Initalize sound for player jumps

    #Helper method to update all players and if they should jump
    def update_players(self):
        #Initialize jump height and gravity
        jump_height = 10 
        gravity = 0.2 #* SPEED_SCALAR
        for x, player in enumerate(self.players):
            #If branch to determine if the player should be removed from everything
            if(player.rect.y < 550):
                #If the player can jump, then make the player jump and check for the first collision
                if(player.jump):
                    player.change_y = -jump_height
                    if(not player.firstCollision):
                        player.firstCollision = True
                    player.jump = False
                #change the player's y-coordinate and add the gravity constant to the player's change in y
                player.player_rect.y += player.change_y #* SPEED_SCALAR
                player.rect.y += player.change_y #* SPEED_SCALAR
                player.change_y += gravity
            else:
                #Remove the player from all lists and Groups and subtract fitness from that player
                self.ge[x].fitness -= 100
                self.group.remove(self.players[x])
                self.players.pop(x)
                self.networks.pop(x)
                self.ge.pop(x)
                
    #Helper method to check for the collision if the player should jump
    def check_collisions_all_players(self):
        for x, player in enumerate(self.players):
            for i in range(len(self.platforms)):
                #Hard coded collision (Pygame collision works the same)
                if(player.rect.y + 60 >= self.platforms[i].rect.y and player.rect.y + 60 <= self.platforms[i].rect.y + 20):
                    if(player.rect.x >= self.platforms[i].rect.x - 50 and player.rect.x <= self.platforms[i].rect.x + 75
                        and player.jump == False and player.change_y > 0):
                        
                            #Set the jump variable to true and play the jump Sound
                            player.jump = True
                            pygame.mixer.Sound.play(self.boing)
                            
                            #Change the player's last and previous last indices and compare the two
                            player.previousLastIndex = player.lastPlatformIndex
                            player.lastPlatformIndex = i
                            if(player.lastPlatformIndex == player.previousLastIndex):
                                #Add to time wasting if indices are the same 
                                player.timeWasting += 1
                                #check for if the player's time wasting is too much and subtract a larger
                                #amount of fitness and remove the player from all groups
                                if(player.timeWasting == 5):
                                    self.ge[x].fitness -= 500
                                    self.group.remove(self.players[x])
                                    self.players.pop(x)
                                    self.networks.pop(x)
                                    self.ge.pop(x)
                            else:
                                #Set the time wasting variable if the indices are not the same
                                player.timeWasting = 0
        return None
        
    #Update all platforms if a player has moved high enough on the window
    def update_platforms(self, plat_list, y, delta):
        if(y < 250 and delta < 0):
            for i in range(len(plat_list)):
                #decrement the y variable by a constant delta
                plat_list[i].rect.y -= delta
            #Add to the score by the pixel
            self.score += 1
            for x, player in enumerate(self.players):
                #Add 1 to each player's fitness and keep their y variable in check
                #(Note: if this is not done, the players will jump sporadically as
                # compared to a controlled jump)
                self.ge[x].fitness += 1
                player.player_rect.y -= delta
                player.rect.y -= delta
        else:
            pass
    
        for k in range(len(plat_list)):
            #If the platform goes beyong the bottom of the screen, move the platform back
            #to a specified distance from the highest platform (at index k-1)
            #and re-randomize the platform's x variable
            if(plat_list[k].rect.y > 600):
                plat_list[k].rect.x = random.randint(0, 495)
                plat_list[k].rect.y = plat_list[k-1].rect.y - 180
                #for each platform that is teleported back to the top of the screen, increment fitness by 5
                for x, player in enumerate(self.players):
                    self.ge[x].fitness += 5
        return plat_list
    
    #Helper method to help find the highest y index
    def find_highest_y(self):
        min = 10000
        for x, player in enumerate(self.players):
            if(player.rect.y < min):
                min = player.rect.y
        return min
    
    #Helper method to help find the index of which the highest y was found
    def find_highest_y_index(self, y):
        result = -1
        for x, player in enumerate(self.players):
            if(player.rect.y == y):
                result = x
        return result

    #TODO: fix varibale names
    #Main game loop to utilize all helper methods and to calculate all needed variables for all players
    def runGame(self):
        #initalize a running boolean to keep track of in the game loop
        running = True
        while (running == True):
            #Set the tick for the timer
            self.timer.tick(self.fps * SPEED_SCALAR)
            
            #initalize the screen and blit a score and generation label to the window
            self.screen.fill(background)
            score_label = self.font.render('Score: ' + str(self.score), True, BLACK, background)
            self.screen.blit(score_label, (480, 20))
            gen_label = self.font.render('Gen: ' + str(self.gen), True, BLACK, background)
            self.screen.blit(gen_label, (0, 20))
    
            #Function for each player to activate their network and provide output to them. 
            for x, player in enumerate(self.players):
                
                #Check for the last platform and to calculate distance from themselves to next platform
                #Variable names:
                #
                #dist: the distance from the player to the platform normally
                #dist_wrap: the MINIMUM distance from the player to the platform with the wrap around feature
                #
                #Other Notes:
                # The sign of the variable determines the direction in which the player moves.
                # The signs are as follows:
                #
                # Positive: the player should move to the left.
                # Negative: the player should move to the right.
                if(player.lastPlatformIndex == 4):
                    dist = (player.rect.x - self.platforms[0].rect.x)
                    #TODO: Signs of dist_wrap
                    dist_wrap = min(((player.rect.x) + (650 - self.platforms[0].rect.x)),
                                    ((650 - player.rect.x) + (self.platforms[0].rect.x)))
                    if(((player.rect.x) + (650 - self.platforms[0].rect.x)) > 
                       ((650 - player.rect.x) + (self.platforms[0].rect.x))):
                        dist_wrap = -(dist_wrap)
                else:
                    dist = (player.rect.x - self.platforms[player.lastPlatformIndex + 1].rect.x)
                    dist_wrap = min(((player.rect.x) + (650 - self.platforms[player.lastPlatformIndex + 1].rect.x)),
                                    ((650 - player.rect.x) + (self.platforms[player.lastPlatformIndex + 1].rect.x)))
                    if(((player.rect.x) + (650 - self.platforms[player.lastPlatformIndex + 1].rect.x)) > 
                        ((650 - player.rect.x) + (self.platforms[player.lastPlatformIndex + 1].rect.x))):
                        dist_wrap = -(dist_wrap)
            
                #TODO: possible vector addition for distance variables (nearest platform, not next platform)
                #Activate the network using the player's coordinates and the distance variables
                output = self.networks[x].activate((player.rect.x, player.rect.y, dist, dist_wrap))
            
                #based on the output from the network activation, move the player in the direction specified
                if((max(output[0], output[1], output[2]) == output[0]) and player.firstCollision):
                    player.change_x = -self.player_speed #* SPEED_SCALAR
                elif((max(output[0], output[1], output[2]) == output[1]) and player.firstCollision):
                    player.change_x = self.player_speed #* SPEED_SCALAR
                else:
                    player.change_x = 0
                    
                #Flip the image of the player depending on the player's change_x variable
                if(player.change_x > 0):
                    player.image = pygame.transform.flip(player.image, 0, 0)
                elif(player.change_x < 0):
                    player.image = pygame.transform.flip(player.image, 1, 0)
                    
            #Call the collision check
            self.check_collisions_all_players()
            
            #Wrap around feature: If the player moves beyond the bounds of the screen
            #(Either to the left or the right) then move the player to the other side of the screen. 
            for x, player in enumerate(self.players):
                player.rect.x += player.change_x
                player.player_rect.x = player.rect.x
                if(player.rect.x > 600):
                    player.rect.x = -50
                    player.player_rect.x  = -50
                elif(player.rect.x < -50):
                    player.rect.x = 600
                    player.player_rect.x = 600
                    
            #Call the helper method to update the players
            self.update_players()
        
            #if there are still players, update the platforms if needed
            if(len(self.players) > 0):
                self.platforms = self.update_platforms(self.platforms, self.find_highest_y(), self.players[self.find_highest_y_index(self.find_highest_y())].change_y) #* SPEED_SCALAR)
            
            #Draw all groups to the window
            self.group.draw(self.screen)
            self.platform_group.draw(self.screen)
            pygame.display.flip()
            
            #If all players are gone or the score meets the necessary variable, then stop running the loop and quit Pygame
            if(len(self.players) == 0 or self.score > 50000):
               running = False
        
        pygame.quit()
        
#Main method to run each generation iteration
def main(genomes, config):
    #Initialize global generation variable and increment
    global GEN
    GEN += 1
    pygame.init()
    doodle_jump = DoodleJump(genomes, config, GEN)
    doodle_jump.runGame()

def play_gen(genomes, config):
    for _, g in genomes:
        network = neat.nn.FeedForwardNetwork.create(g, config)
        g.fitness = 0
        main(g, network)
        print("Fitness of Genome", g.fitness)

#Method to run the configuration file and start the AI learning process
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
    most_fit = population.run(main, 1000)
    
    print("most fit is: ", most_fit)
    pass

#initialize the config file needed and run NEAT.
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    run_config(config_path)
    
