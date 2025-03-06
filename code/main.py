from settings import *
from pytmx.util_pygame import load_pygame #install pytmx : pip install pytmx
import os
from os.path import join
import pytmx

from sprites import Sprite, AnimatedSprite
from entities import Player
from groups import AllSprites

from support import *

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Fake Pokemon")
        self.clock = pygame.time.Clock()

        #groups
        #self.all_sprites = pygame.sprite.Group()
        self.all_sprites = AllSprites()

        self.import_asset()
        self.setup(self.tmx_maps['world'], 'house')

    def import_asset(self):
        #access the map of the world for the game
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of main.py
        TMX_PATH_WORLD = os.path.join(BASE_DIR, "../data/maps/world.tmx")  # Construct absolute path
        TMX_PATH_HOSPITAL = os.path.join(BASE_DIR, "../data/maps/hospital.tmx")
        #join() parameter will create a path like ../data/maps/world.tmx
        self.tmx_maps = {	
            'world': pytmx.util_pygame.load_pygame(TMX_PATH_WORLD),  # Use absolute path
            # 'world': load_pygame('MyGames/pokemon/data/maps/world.tmx'), #Not working with this one or join()
            'hospital': pytmx.util_pygame.load_pygame(TMX_PATH_HOSPITAL)	
        }

        WATER_PATH = os.path.join(BASE_DIR, '../graphics/tilesets/water')
        COAST_PATH = os.path.join(BASE_DIR, '../graphics/tilesets/coast')
        CHARACTER_PATH = os.path.join(BASE_DIR, '../graphics/characters')
        self.overworld_frame = {
            'water': import_folder(WATER_PATH),
            'coast': coast_importer(COAST_PATH),
            'characters': all_character_importer(CHARACTER_PATH)
        }
        print(self.overworld_frame['coast'])

    def setup(self, tmx_map, player_start_pos):
        #background to frontground
        #terrain and terrain top
        for layer in ["Terrain", "Terrain Top"]:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                #x *tile_size = actual size of each tile, because each tile is placed colum, row with the size of 64 in settings
                #print(x * TILE_SIZE,y * TILE_SIZE ,surf)
                Sprite((x * TILE_SIZE,y * TILE_SIZE ),surf, self.all_sprites)

        # #terrain top
        # for x, y, surf in tmx_map.get_layer_by_name("Terrain Top").tiles():
        #     Sprite((x * TILE_SIZE,y * TILE_SIZE ),surf, self.all_sprites)

        #Entities
        for obj in tmx_map.get_layer_by_name("Entities"):
            if obj.name == "Player" and obj.properties['pos'] == player_start_pos:
                #print(obj.x, obj.y)
                #after getting the position of the player, we could start create a player
                self.player = Player(
                    pos = (obj.x, obj.y), 
                    frames = self.overworld_frame["characters"]['player'], 
                    groups = self.all_sprites)

        #Objects
        for obj in tmx_map.get_layer_by_name("Objects"):
            Sprite((obj.x, obj.y), obj.image, self.all_sprites)

        #Water
        for obj in tmx_map.get_layer_by_name("Water"):
            #print(obj.x, obj.y)
            for x in range(int(obj.x), int(obj.x + obj.width), TILE_SIZE):
                for y in range(int(obj.y), int(obj.y + obj.height), TILE_SIZE):
                    AnimatedSprite((x,y), self.overworld_frame['water'], self.all_sprites)

        #Coast
        for obj in tmx_map.get_layer_by_name("Coast"):
            terrain = obj.properties["terrain"]
            side = obj.properties['side']
            AnimatedSprite((obj.x, obj.y), self.overworld_frame['coast'][terrain][side], self.all_sprites)

        #Characters

            


    def run(self):
        while True:
            #event loop
            dt = self.clock.tick() / 1000 #convert to millisecond
            for event in pygame.event.get():
                #check the event type if quit, close the game
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            #game logic
            #as long as the loop is running, the display will get update
            #run sprites before update
            self.all_sprites.update(dt)
            self.display_surface.fill("black") #fill up the part of the map that is outsisde
            self.all_sprites.draw(self.player.rect.center)
            # print(self.clock.get_fps())
            # print(dt)
            pygame.display.update()     

if __name__ == '__main__':
    #check if the file is main, if yes, create game and run it
    game = Game()
    game.run()


#1:23:00