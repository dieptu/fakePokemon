from settings import *
from random import uniform
from support import draw_bar

#position rectangle and graphic in pygame
class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z = WORLD_LAYERS['main']):
        super().__init__(groups)
        self.image = surf 
        self.rect = self.image.get_frect(topleft = pos)
        self.z = z
        self.y_sort = self.rect.centery
        self.hitbox = self.rect.copy()

class MonsterPatchSprite(Sprite):
    def __init__(self, pos, surf, groups, biome):
        self.biome = biome
        super().__init__(pos, surf, groups, WORLD_LAYERS['main' if biome != 'sand' else 'bg'])
        self.y_sort -= 40

class BorderSprite(Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy()

class TransitionSprite(Sprite):
	def __init__(self, pos, size, target, groups):
		surf = pygame.Surface(size)
		super().__init__(pos, surf, groups)
		self.target = target

class CollidableSprite(Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.inflate(0, -self.rect.height*0.6)

class AnimatedSprite(Sprite):
    def __init__(self, pos, frames, groups, z = WORLD_LAYERS['main']):
        self.frame_index, self.frames = 0, frames
        super().__init__(pos, frames[self.frame_index], groups, z)

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[int(self.frame_index % len(self.frames))]

    def update(self, dt):
        self.animate(dt)


class MonsterSprite(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, monster, index, pos_index, entity):
        #data
        self.index = index
        self.pos_index = pos_index
        self.entity = entity
        self.monster = monster
        self.frame_index, self.frames, self.state = 0, frames, 'idle'
        self.animation_speed = ANIMATION_SPEED * uniform(-1, 1)
        self.z = BATTLE_LAYERS['monster']
        self.highlight = False

        #sprite set up
        super().__init__(groups)
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_frect(center = pos)

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED *dt
        self.adjusted_frame_index = int(self.frame_index % len(self.frames[self.state]))
        self.image = self.frames[self.state][self.adjusted_frame_index]

    def update(self, dt):
        self.animate(dt)
        self.monster.update(dt)

    def set_highlight(self, value):
        self.highlight = value
        # if value: 
        #     self.timers['remove highlight'].activate()


class MonsterNameSprite(pygame.sprite.Sprite):
    def __init__(self, pos, monster_sprite, groups, font):
        super().__init__(groups)
        self.z = BATTLE_LAYERS['name']
        self.monster_sprite = monster_sprite

        text_surf = font.render(monster_sprite.monster.name, False, COLORS['black'])
        padding = 10

        self.image = pygame.Surface((text_surf.get_width()+2 * padding, text_surf.get_height() + 2 * padding))
        self.image.fill(COLORS['white'])
        self.image.blit(text_surf, (padding, padding))
        self.rect =self.image.get_frect(midtop = pos)

class MonsterLevelSprite(pygame.sprite.Sprite):
    def __init__(self,entity, pos, monster_sprite, groups, font):
        super().__init__(groups)
        self.monster_sprite = monster_sprite
        self.font = font
        self.z = BATTLE_LAYERS['name']

        self.image = pygame.Surface((60,26))
        self.rect = self.image.get_frect(topleft = pos) if entity == 'player' else self.image.get_frect(topright = pos)
        self.xp_rect = pygame.FRect(0, self.rect.height - 2 , self.rect.width,2)

    def update(self, _):
        self.image.fill(COLORS['white'])

        text_surf = self.font.render(f'Lvl {self.monster_sprite.monster.level}', False, COLORS['black'])
        text_rect = text_surf.get_frect(center = (self.rect.width/2, self.rect.height/2))
        self.image.blit(text_surf, text_rect)

        
        draw_bar(self.image, self.xp_rect, self.monster_sprite.monster.xp, self.monster_sprite.monster.level_up, COLORS['black'], COLORS['white'], 0)


class MonsterStatsSprite(pygame.sprite.Sprite):
    def __init__(self, pos, monster_sprite, size, groups, font):
        super().__init__(groups)
        self.monster_sprite = monster_sprite
        self.z = BATTLE_LAYERS['overlay']

        self.image = pygame.Surface(size)
        self.rect = self.image.get_frect(midbottom = pos)
        self.font = font

    def update(self, _):
        self.image.fill(COLORS['white'])

        for index, (value, max_value) in enumerate(self.monster_sprite.monster.get_info()):
            color = (COLORS['red'], COLORS['blue'], COLORS['gray'])[index]
            if index < 2: # health and energy 
                text_surf = self.font.render(f'{int(value)}/{max_value}', False, COLORS['black'])
                text_rect = text_surf.get_frect(topleft = (self.rect.width * 0.05,index * self.rect.height / 2))
                bar_rect = pygame.FRect(text_rect.bottomleft + vector(0,-2), (self.rect.width * 0.9, 4))

                self.image.blit(text_surf, text_rect)
                draw_bar(self.image, bar_rect, value, max_value, color, COLORS['black'], 2)
            else: # initiative
                init_rect = pygame.FRect((0, self.rect.height - 2), (self.rect.width, 2)) 
                draw_bar(self.image, init_rect, value, max_value, color, COLORS['white'], 0)

class MonsterOutlineSprite(pygame.sprite.Sprite):
    def __init__(self, monster_sprite, groups, frames):
        super().__init__(groups)
        self.z = BATTLE_LAYERS['outline']
        self.monster_sprite = monster_sprite
        self.frames = frames
    

        # self.image = self.frames[self.monster_sprite.state][self.monster_sprite.frame_index]

        self.image = pygame.transform.scale(self.frames[self.monster_sprite.state][self.monster_sprite.frame_index], 
                                        (int(self.monster_sprite.rect.width * 1.1), int(self.monster_sprite.rect.height * 1.1)))
    
        # Position the outline **slightly larger** than the monster to make it visible
        self.rect = self.image.get_frect(center=self.monster_sprite.rect.center)

    def update(self, _):
        """ Syncs the outline frame with the monster's animation """
        self.image = self.frames[self.monster_sprite.state][self.monster_sprite.adjusted_frame_index]
        self.rect.center = self.monster_sprite.rect.center  # Keep it aligned with the monster
        
        # Optional visibility condition
        if not self.monster_sprite.highlight:
            self.image.set_alpha(0)  # Make the outline invisible when not highlighted
        else:
            self.image.set_alpha(255)  # Make the outline visible when highlighted