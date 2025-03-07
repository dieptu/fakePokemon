from settings import *

class Entity(pygame.sprite.Sprite):
    def __init__(self,pos, frames, groups, facing_direction):
        super().__init__(groups)
        self.z = WORLD_LAYERS['main']
        

        #graphics - animation
        self.frame_index , self.frames = 0, frames
        self.facing_direction = facing_direction

        #movement
        self.direction = vector()
        self.speed = 250
        self.blocked = False

        #sprite setup
        self.image = self.frames[self.get_state()][self.frame_index]
        self.rect = self.image.get_frect(center = pos)
        self.hitbox = self.rect.inflate(-self.rect.width/2, -60) #shrink -60 is remove 30 on top, 30 at the bottom

        self.y_sort = self.rect.centery

        

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[self.get_state()][int(self.frame_index %len(self.frames[self.get_state()]))]
    
    # def update(self, dt):
    #     self.animate(dt)
    def get_state(self):
        moving = bool(self.direction)
        if moving:
            if self.direction.x != 0:
                self.facing_direction = 'right' if self.direction.x > 0 else 'left'
            if self.direction.y != 0:
                self.facing_direction = 'down' if self.direction.y > 0 else 'up'
        return f'{self.facing_direction}{'' if moving else '_idle'}'
    
    def change_facing_direction(self, target_pos):
        relation = vector(target_pos) - vector(self.rect.center)
        if abs(relation.y) < 30:
            self.facing_direction = 'right'
    
    def block(self):
        self.blocked = True
        self.direction = vector(0,0)

    def unblock(self):
        self.blocked = False

class Character(Entity):
    def __init__(self, pos, frames, groups, facing_direction):
        super().__init__(pos, frames, groups, facing_direction)
    
    def update(self, dt):
        self.animate(dt)


class Player(Entity):
    def __init__(self, pos,frames, groups, facing_direction, collision_sprites):
        super().__init__(pos, frames, groups, facing_direction)
        # self.image = pygame.Surface((100,100)) #class Entity takes care of this part
        # self.rect = self.image.get_frect(center = pos)
        #self.direction = vector()
        self.collision_sprites = collision_sprites

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
        self.direction = input_vector.normalize() if input_vector else input_vector #normalize the speed to all directions for the player

    def move(self, dt):
        self.rect.centerx += self.direction.x * self.speed * dt #move to direction with a certain speed ()
        self.hitbox.centerx = self.rect.centerx
        self.collision('horizontal')
        self.rect.centery += self.direction.y * self.speed * dt #move to direction with a certain speed ()
        self.hitbox.centery = self.rect.centery
        self.collision('vertical')

    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                if axis == 'horizontal':
                    if self.direction.x > 0 : #move to the right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0 : #move to the left
                        self.hitbox.left = sprite.hitbox.right
                    self.rect.centerx = self.hitbox.centerx
                else:
                    if self.direction.y > 0 : #move to the up
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0 : #move to the up
                        self.hitbox.top = sprite.hitbox.bottom
                    self.rect.centery = self.hitbox.centery


    def update(self, dt):
        self.y_sort = self.rect.centery
        if not self.blocked:
            self.input()
            self.move(dt)
        self.animate(dt)