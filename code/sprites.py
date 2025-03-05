from settings import *

#position rectangle and graphic in pygame
class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos) #get_frect : get floating point from a rectangle
        