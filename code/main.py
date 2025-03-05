from settings import *

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Fake Pokemon")

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