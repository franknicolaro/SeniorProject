import arcade
class Player:
    def __init__(self, score):
        self.player_sprite = arcade.Sprite("PlayerSprite.png", 0.05)
        self.score = score
        self.maxY = self.player_sprite.center_y - (self.player_sprite.height / 2)
    
    def draw(self):
        self.player_sprite.draw()
        self.player_sprite.draw_hit_box()
        
    def updateScore(self):
        if(self.player_sprite.center_y - (self.player_sprite.height / 2) > self.maxY):
            self.maxY = self.player_sprite.center_y - (self.player_sprite.height / 2)
            self.score = self.score + 1