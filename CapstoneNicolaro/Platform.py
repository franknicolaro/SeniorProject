import arcade
import random
class Platform:
    def __init__(self, x, y):
        self.platform_sprite = arcade.Sprite("Platform.png", 0.3)
        self.platform_sprite.center_x = x + (self.platform_sprite.width / 2)
        self.platform_sprite.center_y = y + (self.platform_sprite.height / 2)
        
    
    def draw(self):
        self.platform_sprite.draw()
        self.platform_sprite.draw_hit_box()