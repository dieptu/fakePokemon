from settings import *
from support import import_image
import os.path
from entities import Entity

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector()
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        SHADOW_DIR = os.path.join(BASE_DIR, "../graphics/other/shadow")
        NOTICED_DIR = os.path.join(BASE_DIR, "../graphics/ui/notice")

        self.shadow_surf = import_image(SHADOW_DIR)
        self.notice_surf = import_image(NOTICED_DIR)


    def draw(self, player):
        self.offset.x = -(player.rect.centerx - WINDOW_WIDTH / 2)
        self.offset.y = -(player.rect.centery - WINDOW_HEIGHT / 2)

        bg_sprites = [sprite for sprite in self if sprite.z < WORLD_LAYERS['main']]
        main_sprites = sorted([sprite for sprite in self if sprite.z == WORLD_LAYERS['main']], key = lambda sprite: sprite.y_sort)
        fg_sprites = [sprite for sprite in self if sprite.z > WORLD_LAYERS['main']]

        for layer in (bg_sprites, main_sprites, fg_sprites):
            for sprite in layer:
                if isinstance(sprite, Entity):
                    self.display_surface.blit(self.shadow_surf, sprite.rect.topleft + self.offset + vector(40,110))
                self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
                if sprite == player and player.noticed:
                    rect = self.notice_surf.get_frect(midbottom = sprite.rect.midtop)
                    self.display_surface.blit(self.notice_surf, rect.topleft + self.offset)

class BattleSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

    # def draw(self, current_monster_sprite, side, mode, target_index, player_sprites,opponent_sprites):
    #     #get available positions
    #     sprite_group = opponent_sprites if side == 'opponent' else player_sprites
    #     sprites = {sprite.pos_index : sprite for sprite in sprite_group}
    #     monster_sprite = sprites[list(sprites.keys())[target_index]]
        
        
    #     for sprite in sorted(self, key=lambda s: getattr(s, 'z', 0)):
    #     #for sprite in sorted(self, key = lambda sprite: sprite.z):
    #         if sprite.z == BATTLE_LAYERS['outline']:
    #             if sprite.monster_sprite == current_monster_sprite or sprite.monster_sprite == monster_sprite:
    #                 self.display_surface.blit(sprite.image, sprite.rect)
    #         else:
    #             self.display_surface.blit(sprite.image, sprite.rect)

    #     if current_monster_sprite:
    #         current_monster_sprite.set_highlight(True)


    def draw(self, current_monster_sprite, side, mode, target_index, player_sprites, opponent_sprites):
    # Get the correct sprite group
        sprite_group = opponent_sprites if side == 'opponent' else player_sprites
        sorted_sprites = sorted(sprite_group.sprites(), key=lambda s: s.pos_index)

        # Safely get the target monster sprite
        monster_sprite = sorted_sprites[target_index] if sorted_sprites and 0 <= target_index < len(sorted_sprites) else None

        
        # Draw all sprites based on their z-layer
        for sprite in sorted(self, key=lambda sprite: sprite.z):
            if sprite.z == BATTLE_LAYERS['outline']:
                highlight = False

                if sprite.monster_sprite == current_monster_sprite and not (mode == 'target' and side == 'player'):
                    highlight = True
                elif sprite.monster_sprite == monster_sprite and sprite.monster_sprite.entity == side and mode == 'target':
                    highlight = True

                #print(f"Highlight check: {sprite.monster_sprite.monster}, highlight={highlight}")
                if highlight:
                    self.display_surface.blit(sprite.image, sprite.rect)

            else:
                self.display_surface.blit(sprite.image, sprite.rect)
