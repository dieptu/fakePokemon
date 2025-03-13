from settings import *
from os.path import join
from os import walk
from pytmx.util_pygame import load_pygame
import os

# imports 
def import_image(*path, alpha = True, format = 'png'):
	full_path = join(*path) + f'.{format}'
	surf = pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()
	return surf

def import_folder(*path):
    frames = []
    for folder_path, sub_folders, image_names in os.walk(os.path.join(*path)):
        for image_name in sorted(image_names, key=lambda name: int(name.split('.')[0])):
            full_path = os.path.join(folder_path, image_name)
            surf = pygame.image.load(full_path).convert_alpha()
            frames.append(surf)
    return frames

def import_folder_dict(*path):
	frames = {}
	for folder_path, sub_folders, image_names in walk(join(*path)):
		for image_name in image_names:
			full_path = join(folder_path, image_name)
			surf = pygame.image.load(full_path).convert_alpha()
			frames[image_name.split('.')[0]] = surf
	return frames

def import_sub_folders(*path):
	frames = {}
	for _, sub_folders, __ in walk(join(*path)):
		if sub_folders:
			for sub_folder in sub_folders:
				frames[sub_folder] = import_folder(*path, sub_folder)
	return frames

def import_tmx(*path):
	tmx_dict = {}
	for folder_path, _, file_names in walk(join(*path)):
		for file in file_names:
			tmx_dict[file.split('.')[0]] = load_pygame(join('..', 'data', 'maps', file))
	return tmx_dict

def import_tilemap(cols, rows, *path):
	frames = {}
	surf = import_image(*path)
	cell_width, cell_height = surf.get_width() / cols, surf.get_height() / rows
	for col in range(cols):
		for row in range(rows):
			cutout_rect = pygame.Rect(col * cell_width, row * cell_height,cell_width,cell_height)
			cutout_surf = pygame.Surface((cell_width, cell_height))
			cutout_surf.fill('green')
			cutout_surf.set_colorkey('green')
			cutout_surf.blit(surf, (0,0), cutout_rect)
			frames[(col, row)] = cutout_surf
	return frames

def character_importer(*path):
	frame_dict = import_tilemap(4,4,*path)
	new_dict = {}
	for key, row in (('down', 0), ('left', 1), ('right', 2), ('up', 3)):
		new_dict[f'{key}_idle'] = [frame_dict[(0,row)]]
		new_dict[key] = [frame_dict[(col, row)] for col in range(4)]
	return new_dict

def all_character_importer(*path):
	char_dict = {}
	for folder_path, _, image_names in walk(join(*path)):
		for image in image_names:
			image_name = image.split('.')[0]
			char_dict[image_name] = character_importer(*path,image_name)
			#print("\n\ncharacter dictionary: ",char_dict)
	return char_dict

def monster_importer(*path):
	monster_dict = {}
	for folder_path, _, image_names in walk(join(*path)):
		for image in image_names:
			image_name = image.split('.')[0]
			frame_dict = import_tilemap(4,2,*path, image_name)
			monster_dict[image_name] = {}
			for key, row in (('idle', 0), ('attack',1)):
				monster_dict[image_name][key] = [frame_dict[(col, row)] for col in range(4)]
					
	return monster_dict

def attack_importer(*path):
	attack_dict = {}
	for folder_path, _, image_names in walk(join(*path)):
		for image in image_names:
			image_name = image.split('.')[0]
			attack_dict[image_name] = list(import_tilemap(4,1,folder_path,image_name).values())
	return attack_dict

def coast_importer(cols, rows, *path):
	frame_dict = import_tilemap(cols, rows, *path)
	new_dict = {}
	terrains = ['grass', 'grass_i', 'sand_i', 'sand', 'rock', 'rock_i', 'ice', 'ice_i']
	sides = {
		'topleft': (0,0), 'top': (1,0), 'topright': (2,0), 
		'left': (0,1), 'right': (2,1), 
		'bottomleft': (0,2), 'bottom': (1,2), 'bottomright': (2,2)
		}
	for index, terrain in enumerate(terrains): 
		new_dict[terrain] = {}
		for key, pos in sides.items():
			new_dict[terrain][key] = [frame_dict[(pos[0] + index * 3,pos[1] + row)] for row in range(0,12,3)]
	return new_dict


def tmx_importer(*path):
	tmx_dict = {}
	for folder_path, sub_folders, file_names in walk(join(*path)):
		for file in file_names:
			tmx_dict[file.split('.')[0]] = load_pygame(join(folder_path, file))
	return tmx_dict

def audio_importer(*path):
	files = {}
	for folder_path, _, file_names in walk(join(*path)):
		for file_name in file_names:
			full_path = join(folder_path, file_name)
			files[file_name.split('.')[0]] = pygame.mixer.Sound(full_path)
	return files

# # functions 
def check_connection(radius, entity, target, tolerance = 30):
	relation = vector(target.rect.center) - vector(entity.rect.center)
	if relation.length() < radius:
		if entity.facing_direction == 'left' and relation.x < 0 and abs(relation.y) < tolerance or \
		   entity.facing_direction == 'right' and relation.x > 0 and abs(relation.y) < tolerance or \
		   entity.facing_direction == 'up' and relation.y < 0 and abs(relation.x) < tolerance or \
		   entity.facing_direction == 'down' and relation.y > 0 and abs(relation.x) < tolerance:
		   return True

def draw_bar(surface, rect, value, max_value, color, bg_color, radius = 1):
	ratio = rect.size[0] / max_value
	bg_rect = rect.copy()
	progress_rect = pygame.FRect(rect.topleft, (max(0, value) * ratio, rect.size[1]))
	pygame.draw.rect(surface, bg_color, bg_rect,0,radius)
	pygame.draw.rect(surface, color, progress_rect,0,radius)

#outline of the square white
def outline_creator(frame_dict, width):
    outline_frame_dict = {}

    for monster, monster_frames in frame_dict.items():
        outline_frame_dict[monster] = {}

        for state, frames in monster_frames.items():
            outline_frame_dict[monster][state] = []

            for frame in frames:
                # Create transparent surface large enough for the outline
                new_surf = pygame.Surface(
                    (frame.get_width() + width * 2, frame.get_height() + width * 2),
                    pygame.SRCALPHA
                )
                new_surf.fill((0, 0, 0, 0))  # Fully transparent

                # Create a mask from the sprite
                mask = pygame.mask.from_surface(frame)
                outline_points = mask.outline()  # Get actual shape outline

                # Offset the points so they wrap around the monster
                outline_points = [(x + width, y + width) for x, y in outline_points]

                # Ensure the outline isn't just a bounding box by checking length
                if len(outline_points) > 1:
                    pygame.draw.polygon(new_surf, (255, 255, 255), outline_points, width)

                # Blit the original sprite onto the new surface
                new_surf.blit(frame, (width, width))

                # Store the outlined sprite
                outline_frame_dict[monster][state].append(new_surf)

    return outline_frame_dict