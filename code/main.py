from settings import *
from game_data import *
from pytmx.util_pygame import load_pygame #install pytmx : pip install pytmx
import os
from os.path import join
import pytmx

from sprites import Sprite, AnimatedSprite, MonsterPatchSprite, BorderSprite, CollidableSprite, TransitionSprite
from entities import Player, Character
from groups import AllSprites
from dialog import DialogTree

from support import *
from monster import Monster
from monster_index import MonsterIndex
from battle import Battle

class Game:
    #general
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Fake Pokemon")
        self.clock = pygame.time.Clock()

        #player monster
        self.player_monster = {
            0: Monster("Charmadillo", 30),
            1: Monster("Friolera", 29),
            2: Monster("Larvea", 3),
            3: Monster("Atrox", 24),
            4: Monster("Sparchu", 24),
            5: Monster("Gulfin", 4),
            6: Monster("Jacana", 2),
            7: Monster("Pouch", 3)
        }

        self.dummy_monster = {
            0: Monster("Atrox", 12),
            1: Monster("Sparchu", 15),
            2: Monster("Gulfin", 19),
            3: Monster("Jacana", 2),
            4: Monster("Pouch", 3)
        }

        #groups
        #self.all_sprites = pygame.sprite.Group()
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.characters_sprites = pygame.sprite.Group()
        self.transition_sprites = pygame.sprite.Group()

        # transition / tint
        self.transition_target = None
        self.tint_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.tint_mode = 'untint'
        self.tint_progress = 0
        self.tint_direction = -1
        self.tint_speed = 600

        self.import_asset()
        self.setup(self.tmx_maps['world'], 'house')
        
        #overlays
        self.dialog_tree = None
        self.monster_index = MonsterIndex(self.player_monster, self.fonts, self.monster_frames)
        self.index_open = False
        self.battle = Battle(self.player_monster, self.dummy_monster, self.monster_frames, self.bg_frames['forest'], self.fonts)


    def import_asset(self):
        #access the map of the world for the game
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of main.py
        # TMX_PATH_WORLD = os.path.join(BASE_DIR, "../data/maps/world.tmx")  # Construct absolute path
        # TMX_PATH_HOSPITAL = os.path.join(BASE_DIR, "../data/maps/hospital.tmx")
        WATER_PATH = os.path.join(BASE_DIR, '../graphics/tilesets/water')
        COAST_PATH = os.path.join(BASE_DIR, '../graphics/tilesets/coast')
        CHARACTER_PATH = os.path.join(BASE_DIR, '../graphics/characters')
        DIALOG_PATH = os.path.join(BASE_DIR, '../graphics/fonts/PixeloidSans.ttf')
        MAPS_PATH = os.path.join(BASE_DIR, '../data/maps')
        BOLD_PATH = os.path.join(BASE_DIR, '../graphics/fonts/dogicapixelbold.otf')
        ICONS_PATH = os.path.join(BASE_DIR, '../graphics/icons')
        MONSTER_PATH = os.path.join(BASE_DIR, '../graphics/monsters')
        UI_PATH = os.path.join(BASE_DIR, '../graphics/ui')
        BACKGROUND_PATH = os.path.join(BASE_DIR, '../graphics/backgrounds')

        #join() parameter will create a path like ../data/maps/world.tmx
        # self.tmx_maps = {	
        #     'world': pytmx.util_pygame.load_pygame(TMX_PATH_WORLD),  # Use absolute path
        #     # 'world': load_pygame('MyGames/pokemon/data/maps/world.tmx'), #Not working with this one or join()
        #     'hospital': pytmx.util_pygame.load_pygame(TMX_PATH_HOSPITAL),	

        # }
        # print(tmx_importer(MAPS_PATH)) 
        self.tmx_maps = tmx_importer(MAPS_PATH)

        self.overworld_frame = {
            'water': import_folder(WATER_PATH),
            'coast': coast_importer(24, 12, COAST_PATH),
            'characters': all_character_importer(CHARACTER_PATH)
        }
        #print(self.overworld_frame['coast'])
        self.fonts = {
            "dialog": pygame.font.Font(DIALOG_PATH, 30),
            "regular": pygame.font.Font(DIALOG_PATH, 18),
            "small": pygame.font.Font(DIALOG_PATH, 14),
            "bold": pygame.font.Font(BOLD_PATH, 20)
        }

        self.monster_frames = {
            'icons' : import_folder_dict(ICONS_PATH),
            'monsters': monster_importer(MONSTER_PATH), 
            'ui': import_folder_dict(UI_PATH)
        }
        self.monster_frames['outlines'] = outline_creator(self.monster_frames['monsters'], 5)
        print('MONSTER_FRAMES - OUTLINES \n\n',self.monster_frames['outlines'])
        self.bg_frames = import_folder_dict(BACKGROUND_PATH)
        

    def setup(self, tmx_map, player_start_pos):
        #background to frontground
        for group in (self.all_sprites, self.collision_sprites, self.transition_sprites, self.characters_sprites):
            group.empty()

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

        #transition objects
        for obj in tmx_map.get_layer_by_name('Transition'):
            TransitionSprite((obj.x, obj.y), (obj.width, obj.height), (obj.properties['target'], obj.properties['pos']), self.transition_sprites)

        #collision objects
        for obj in tmx_map.get_layer_by_name("Collisions"):
            BorderSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

    #dialog system
    def input(self):
        if not self.dialog_tree and not self.battle:
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
            if keys[pygame.K_RETURN]:
                self.index_open = not self.index_open
                self.player.blocked = not self.player.blocked
    
    def create_dialog(self, character):
        if not self.dialog_tree:
            self.dialog_tree = DialogTree(character, self.player, self.all_sprites, self.fonts['dialog'], self.end_dialog)

    def end_dialog(self, character):
        self.dialog_tree = None
        self.player.unblock()

    #transition system
    # def transition_check(self):
    #     sprites = [sprite for sprite in self.transition_sprites if sprite.rect.colliderect(self.player.hitbox)]
    #     if sprites:
    #         self.player.block()
    #         self.transition_target = sprites[0].target
    #         self.tint_mode = 'tint'
    #         self.tint_progress = 0

    def transition_check1(self):
        sprites = [sprite for sprite in self.transition_sprites if sprite.rect.colliderect(self.player.hitbox)]
        if sprites:
            self.player.block()
            self.transition_target = sprites[0].target
            self.tint_mode = 'tint'

    def tint_screen1(self, dt):
        if self.tint_mode == 'untint':
            self.tint_progress -= self.tint_speed * dt

        if self.tint_mode == 'tint':
            self.tint_progress += self.tint_speed * dt
            if self.tint_progress >= 255:
                self.setup(self.tmx_maps[self.transition_target[0]], self.transition_target[1])
                self.tint_mode = 'untint'
                self.transition_target = None

        self.tint_progress = max(0, min(self.tint_progress, 255))
        #self.tint_surf.set_alpha(self.tint_progress)
        #self.display_surface.blit(self.tint_surf, (0,0))
        # # Only apply the black tint after all other sprites are drawn
        # if self.tint_progress > 0 and self.tint_progress < 255:
        #     self.tint_surf.fill((0, 0, 0))  # Fill with black color
        #     self.tint_surf.set_alpha(self.tint_progress)  # Apply the transparency based on tint progress

        #     # Draw the tint over the entire screen
        #     self.display_surface.blit(self.tint_surf, (0, 0))

        # # Draw all the other game entities (background, player, coast, etc.)
        # if self.tint_progress == 255:  # After the fade-in, draw all entities
        #     self.all_sprites.draw(self.display_surface)
        if self.tint_progress > 0:
            self.tint_surf.fill((0, 0, 0))  # Fill the surface with black color
            self.tint_surf.set_alpha(self.tint_progress)  # Set the transparency based on tint_progress
            self.display_surface.blit(self.tint_surf, (0, 0))  # Draw the tint

        # Step 4: Draw all the game entities (after the fade-in)
        if self.tint_progress == 0 and self.tint_mode == 'untint':  # When fully visible again
            for sprite in self.all_sprites:
                # Check if the sprite has the surface attribute, and blit it to the display
                if hasattr(sprite, 'surf'):
                    self.display_surface.blit(sprite.surf, sprite.rect)
        
    # def tint_screen(self, dt):
    #     if self.tint_mode == 'tint':  # Fade in (to black)
    #         self.tint_progress += self.tint_speed * dt
    #         if self.tint_progress >= 255:  # When fully black, change map
    #             self.tint_progress = 255
    #             self.setup(self.tmx_maps[self.transition_target[0]], self.transition_target[1])
    #             self.tint_mode = 'untint'  # Start fade-out

    #     elif self.tint_mode == 'untint':  # Fade out (back to normal)
    #         self.tint_progress -= self.tint_speed * dt
    #         if self.tint_progress <= 0:
    #             self.tint_progress = 0
    #             self.tint_mode = None  # Stop tinting
    #             self.player.unblock() 
       
    #     if self.tint_progress > 0:  # Only blit if there is tint
    #         self.tint_surf.fill((0, 0, 0, int(self.tint_progress)))
    #         self.display_surface.blit(self.tint_surf, (0, 0))

    def run(self):
        while True:
            #event loop
            dt = self.clock.tick() / 1000 #convert to millisecond
            self.display_surface.fill("black") #fill up the part of the map that is outsisde
            
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
            self.all_sprites.draw(self.player)
            # print(self.clock.get_fps())
            # print(dt)

            #overlays
            if self.dialog_tree : self.dialog_tree.update()
            if self.index_open  : self.monster_index.update(dt)
            if self.battle      : self.battle.update(dt)
            self.transition_check1()
            self.tint_screen1(dt)

            #self.tint_screen(dt)
            pygame.display.update()     

if __name__ == '__main__':
    #check if the file is main, if yes, create game and run it
    game = Game()
    game.run()


#7:50:00