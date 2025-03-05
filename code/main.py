from settings import *
from pytmx.util_pygame import load_pygame #install pytmx : pip install pytmx
import os
import pytmx

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Fake Pokemon")
        self.import_asset()
        self.setup(self.tmx_maps['world'], 'house')

    def import_asset(self):
        #access the map of the world for the game
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of main.py
        TMX_PATH = os.path.join(BASE_DIR, "../data/maps/world.tmx")  # Construct absolute path
        #join() parameter will create a path like ../data/maps/world.tmx
        self.tmx_maps = {	
            'world': pytmx.util_pygame.load_pygame(TMX_PATH)  # Use absolute path
            # 'world': load_pygame('MyGames/pokemon/data/maps/world.tmx')
            }
        # print(self.tmx_maps)

    def setup(self, tmx_map, player_start_pos):
        for x, y, surf in tmx_map.get_layer_by_name("Terrain").tiles():
            print(x,y,surf)

    def run(self):
        while True:
            #event loop
            for event in pygame.event.get():
                #check the event type if quit, close the game
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            #game logic
            #as long as the loop is running, the display will get update
            pygame.display.update()     

if __name__ == '__main__':
    #check if the file is main, if yes, create game and run it
    game = Game()
    game.run()