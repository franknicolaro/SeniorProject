
import arcade
import random
import Platform
import Player
#import os
#import neat

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
MOVEMENT_SPEED = 5
GRAVITY = 0.21
JUMP_VELOCITY = 9.8

class MyGame(arcade.Window):

    def __init__(self, width, height):
        super().__init__(width, height, "Doodle Jump")
        self.camera_sprites = None

        arcade.set_background_color(arcade.color.ALMOND)

    def setup(self):
        
        #add a camera (to be fixed onto a set x coordinate)
        self.camera_sprites = arcade.Camera(self.width, self.height)
        
        #set the game's end boolean check to false
        self.game_end = False
        
        #create the player
        self.player = Player.Player(0)
        
        #create a base platform to be used solely for its width to add platforms
        base_platform = Platform.Platform(-10000, -10000)
        
        #Create the first platforms to jump on
        self.platforms = []
        self.gap = SCREEN_HEIGHT / 6
        for i in range(6):
            self.platforms.append(Platform.Platform(random.randint(0, (SCREEN_WIDTH - base_platform.platform_sprite.width - 100)), (SCREEN_HEIGHT - (i * self.gap))))
            
        #set the player's starting position to just above the first platform
        self.player.player_sprite.center_x = self.platforms[len(self.platforms) - 1].platform_sprite.center_x
        self.player.player_sprite.center_y = self.platforms[len(self.platforms) - 1].platform_sprite.center_y + 110
        
        #Set up the physics engine with GRAVITY as the constant
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player.player_sprite, gravity_constant=GRAVITY
        )
        pass
         
    def on_draw(self):
        """ Render the screen. """
        if(self.game_end == False):
            #render the player and platforms
            self.camera_sprites.use()
            arcade.start_render()
            self.player.draw()
            self.redraw_platforms()
            arcade.draw_text('Score: ' + str(self.player.score), self.player.player_sprite.center_x - (self.player.player_sprite.width / 2), self.player.player_sprite.center_y + 50,
                            arcade.color.BLACK_LEATHER_JACKET, 10, 90, 'left')
        else:
            #reset the render and display Game over text
            arcade.finish_render()
            arcade.start_render()
            for platform in self.platforms:
                self.platforms.pop
            arcade.draw_text('Game Over! Final Score: '+ str(self.player.score), self.camera_sprites.position.x, self.camera_sprites.position.y + 300,
                            arcade.color.BLACK_LEATHER_JACKET, 30, 180, 'left')
        
    #draws all platforms in their location
    def redraw_platforms(self):
        for platform in self.platforms:
            platform.draw()
      
    #method for movement (left and right)
    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.LEFT:
            self.player.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player.player_sprite.change_x = MOVEMENT_SPEED
    
    #method to stop the player's movement when the key pressed is released
    def on_key_release(self, key: int, modifiers: int):
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player.player_sprite.change_x = 0
            
    def center_camera_to_player(self):
        screen_center_x = 0
        screen_center_y = self.player.player_sprite.center_y - (self.camera_sprites.viewport_height / 2)

        # Move Camera to center
        player_centered = screen_center_x, screen_center_y
        self.camera_sprites.move_to(player_centered)
        
    def end_game(self):
        self.game_end = True
        
    def update(self, delta_time):
        
        if(self.game_end == False):
            
            #Wrap around concept for the player
            if(self.player.player_sprite.center_x + (self.player.player_sprite.width / 2) < 0):
                self.player.player_sprite.center_x = SCREEN_WIDTH + (self.player.player_sprite.width / 2)
            if(self.player.player_sprite.center_x - (self.player.player_sprite.width / 2) > SCREEN_WIDTH):
                self.player.player_sprite.center_x = -(self.player.player_sprite.width / 2)
            
            #insert platforms as player jumps upwards
            if(self.player.player_sprite.center_y + (self.player.player_sprite.height / 2) > self.platforms[0].platform_sprite.center_y + (self.platforms[0].platform_sprite.height / 2) - 200):
                self.platforms.insert(0, Platform.Platform(random.randint(0, (SCREEN_WIDTH - 70)),(self.platforms[0].platform_sprite.center_y + (self.platforms[0].platform_sprite.height / 2) + self.gap)))
                self.redraw_platforms()
            
            #update the physics on the player (change in y) and center the camera to the player
            self.physics_engine.update()
            self.center_camera_to_player()
        
            #delete platforms as player jumps upwards
            if(self.platforms[len(self.platforms) - 1].platform_sprite.center_y 
               + (self.platforms[0].platform_sprite.height / 2) < self.camera_sprites.position.y):
                self.platforms.remove(self.platforms[len(self.platforms) - 1])
        
            #Check collisions on each platform and jump if the player collides with a platform from the player's lowest y coordinate
            for platform in self.platforms:    
                if(self.player.player_sprite.collides_with_sprite(platform.platform_sprite) 
                   and self.player.player_sprite.center_y - (self.player.player_sprite.height / 2) 
                   >= (platform.platform_sprite.center_y) - (platform.platform_sprite.height / 4.75)
                   and self.player.player_sprite.change_y < 0):
                    self.player.player_sprite.change_y = JUMP_VELOCITY
             
            #Update the player score
            self.player.updateScore()
        
            #Game over Condition
            if(self.player.player_sprite.center_y - (self.player.player_sprite.height / 2) 
               < self.platforms[len(self.platforms) - 1].platform_sprite.center_y - (self.platforms[len(self.platforms) - 1].platform_sprite.height / 2) - 200):
                self.end_game()
        pass      

def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.setup()
    arcade.run()
    
#def run(config_path):
    
    #Load in the configuration file
    #config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                #neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                #config_path)
    
    #Declare the Population
    #population = neat.Population(config)
    
    #Produces output for the population in each generation
    #population.add_reporter(neat.StdOutReporter(True))
    #stats = neat.StatisticsReporter()
    #population.add_reporter(stats)
    
    #run the population
    #most_fit = population.run(main(), 50)
    #pass

if __name__ == "__main__":
    #local_dir = os.path.dirname(__file__)
    #config_path = os.path.join(local_dir, "config.txt")
    #run(config_path)
    main()

