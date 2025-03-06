from settings import *

class Entity(pygame.sprite.Sprite):
    def __init__(self,pos, frames, groups):
        super().__init__(groups)

        #graphics - animation
        self.frame_index , self.frames = 0, frames
        self.facing_direction = 'down'

        #sprite setup
        self.image = self.frames['down'][self.frame_index]
        self.rect = self.image.get_frect(center = pos)
        #movement
        self.direction = vector()
        self.speed = 250

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[self.get_state()][int(self.frame_index %len(self.frames[self.get_state()]))]
    
    # def update(self, dt):
    #     self.animate(dt)
    def get_state(self):
        #logic
        moving = bool(self.direction)
        if moving:
            if self.direction.x != 0:
                self.facing_direction = 'right' if self.direction.x > 0 else 'left'
            if self.direction.y != 0:
                self.facing_direction = 'down' if self.direction.y > 0 else 'up'
        return f"{self.facing_direction}{'' if moving else '_idle'}"

class Player(Entity):
    def __init__(self, pos,frames, groups):
        super().__init__(pos, frames, groups)
        # self.image = pygame.Surface((100,100)) #class Entity takes care of this part
        # self.rect = self.image.get_frect(center = pos)
        #self.direction = vector()

    def input(self):
        keys = pygame.key.get_pressed()
        input_vector = vector() #vector 0,0
        if keys[pygame.K_UP]:
            input_vector.y -= 1
            #print(input_vector.y)
        if keys[pygame.K_DOWN]:
            input_vector.y +=1
        if keys[pygame.K_LEFT]:
            input_vector.x -=1
        if keys[pygame.K_RIGHT]:
            input_vector.x +=1
        self.direction = input_vector

    def move(self, dt):
        self.rect.center += self.direction * self.speed * dt #move to direction with a certain speed ()

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)