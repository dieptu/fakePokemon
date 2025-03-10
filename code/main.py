from settings import *
from game_data import *
from pytmx.util_pygame import load_pygame #install pytmx : pip install pytmx
import os
from os.path import join
import pytmx

from sprites import Sprite, AnimatedSprite, MonsterPatchSprite, BorderSprite, CollidableSprite
from entities import Player, Character
from groups import AllSprites
from dialog import DialogTree

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
        self.collision_sprites = pygame.sprite.Group()
        self.characters_sprites = pygame.sprite.Group()

        self.import_asset()
        self.setup(self.tmx_maps['world'], 'house')
        self.dialog_tree = None

    def import_asset(self):
        #access the map of the world for the game
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of main.py
        TMX_PATH_WORLD = os.path.join(BASE_DIR, "../data/maps/world.tmx")  # Construct absolute path
        TMX_PATH_HOSPITAL = os.path.join(BASE_DIR, "../data/maps/hospital.tmx")
        WATER_PATH = os.path.join(BASE_DIR, '../graphics/tilesets/water')
        COAST_PATH = os.path.join(BASE_DIR, '../graphics/tilesets/coast')
        CHARACTER_PATH = os.path.join(BASE_DIR, '../graphics/characters')
        DIALOG_PATH = os.path.join(BASE_DIR, '../graphics/fonts/PixeloidSans.ttf')

        #join() parameter will create a path like ../data/maps/world.tmx
        self.tmx_maps = {	
            'world': pytmx.util_pygame.load_pygame(TMX_PATH_WORLD),  # Use absolute path
            # 'world': load_pygame('MyGames/pokemon/data/maps/world.tmx'), #Not working with this one or join()
            'hospital': pytmx.util_pygame.load_pygame(TMX_PATH_HOSPITAL)	
        }

        self.overworld_frame = {
            'water': import_folder(WATER_PATH),
            'coast': coast_importer(COAST_PATH),
            'characters': all_character_importer(CHARACTER_PATH)
        }
        #print(self.overworld_frame['coast'])
        self.fonts = {
            "dialog": pygame.font.Font(DIALOG_PATH, 30)
        }

    def setup(self, tmx_map, player_start_pos):
        #background to frontground
        #terrain and terrain top
        for layer in ["Terrain", "Terrain Top"]:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                #x *tile_size = actual size of each tile, because each tile is placed colum, row with the size of 64 in settings
                #print(x * TILE_SIZE,y * TILE_SIZE ,surf)
                Sprite((x * TILE_SIZE,y * TILE_SIZE ),surf, self.all_sprites, WORLD_LAYERS['bg'])

        # #terrain top
        # for x, y, surf in tmx_map.get_layer_by_name("Terrain Top").tiles():
        #     Sprite((x * TILE_SIZE,y * TILE_SIZE ),surf, self.all_sprites)
        
        #Water
        for obj in tmx_map.get_layer_by_name("Water"):
            #print(obj.x, obj.y)
            for x in range(int(obj.x), int(obj.x + obj.width), TILE_SIZE):
                for y in range(int(obj.y), int(obj.y + obj.height), TILE_SIZE):
                    AnimatedSprite((x,y), self.overworld_frame['water'], self.all_sprites, WORLD_LAYERS['water'])

        #Coast
        for obj in tmx_map.get_layer_by_name("Coast"):
            terrain = obj.properties["terrain"]
            side = obj.properties['side']
            AnimatedSprite((obj.x, obj.y), self.overworld_frame['coast'][terrain][side], self.all_sprites,WORLD_LAYERS['bg'])

        #Entities
        for obj in tmx_map.get_layer_by_name("Entities"):
            if obj.name == 'Player':
                if obj.properties['pos'] == player_start_pos:
                    self.player = Player(
						pos = (obj.x, obj.y), 
						frames = self.overworld_frame['characters']['player'], 
						groups = self.all_sprites,
						facing_direction = obj.properties['direction'],
                        collision_sprites = self.collision_sprites
                        )
            else:
                Character(
					pos = (obj.x, obj.y), 
					frames = self.overworld_frame['characters'][obj.properties['graphic']], 
					groups = (self.all_sprites, self.collision_sprites, self.characters_sprites),
					facing_direction = obj.properties['direction'],
                    character_data= TRAINER_DATA[obj.properties['character_id']],
                    player = self.player,
                    create_dialog=self.create_dialog,
                    collision_sprites= self.collision_sprites,
                    radius = obj.properties['radius']
                    )

        #Grass patches
        for obj in tmx_map.get_layer_by_name("Monsters"):
            MonsterPatchSprite((obj.x, obj.y), obj.image, self.all_sprites, obj.properties['biome'])

        #Objects
        for obj in tmx_map.get_layer_by_name("Objects"):
            if (obj.name == 'top'):
                Sprite((obj.x, obj.y), obj.image, self.all_sprites, WORLD_LAYERS['top'])
            else:
                CollidableSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        #collision objects
        for obj in tmx_map.get_layer_by_name("Collisions"):
            BorderSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

    def input(self):
        if not self.dialog_tree:
            keys = pygame.key.get_just_pressed()
            if keys[pygame.K_SPACE]:
                for character in self.characters_sprites:
                    if check_connection(100, self.player, character):
                        #block player input
                        self.player.block()
                        #entities face each other
                        character.change_facing_direction(self.player.rect.center)
                        #create dialog
                        self.create_dialog(character)
                        #print("dialog")
                        character.can_rotate = False
    
    def create_dialog(self, character):
        if not self.dialog_tree:
            self.dialog_tree = DialogTree(character, self.player, self.all_sprites, self.fonts['dialog'], self.end_dialog)

    def end_dialog(self, character):
        self.dialog_tree = None
        self.player.unblock()


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
            self.input()
            #run sprites before update
            self.all_sprites.update(dt)
            self.display_surface.fill("black") #fill up the part of the map that is outsisde
            self.all_sprites.draw(self.player)
            # print(self.clock.get_fps())
            # print(dt)

            #overlays
            if self.dialog_tree: self.dialog_tree.update()

            pygame.display.update()     

if __name__ == '__main__':
    #check if the file is main, if yes, create game and run it
    game = Game()
    game.run()


