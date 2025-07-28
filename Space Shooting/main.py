from operator import index

import pygame
from os.path import join
from random import randint, uniform

from pandas.io.formats.info import frame_max_cols_sub


class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.speed = 300

        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 200
        self.mask = pygame.mask.from_surface(self.image)

    def laser_time(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, all_sprite, laser_sprites)
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=(randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))


class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, *groups):
        super().__init__(*groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom=pos)

    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()


class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, *groups):
        super().__init__(*groups)
        self.original = surf
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(400, 500)
        self.rotation_speed = randint(40,80)
        self.rotation = 0

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original,self.rotation,1)
        self.rect = self.image.get_frect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self,frames,pos,groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = frames[0]
        self.rect = self.image.get_frect(center = pos)
        explosion_sound.play()

    def update(self,dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()


def collisions():
    global running
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True,pygame.sprite.collide_mask)
    if collision_sprites:
        running = False

    for laser in laser_sprites:
        collision_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collision_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frame, laser.rect.midtop,all_sprite)
            explosion_sound.play()

def display_score():
    current_time = pygame.time.get_ticks() // 100
    text_surface = font.render(str(current_time), True, (240, 240, 240))
    text_rect = text_surface.get_frect(midbottom = (WINDOW_WIDTH/2,WINDOW_HEIGHT - 50))
    pygame.draw.rect(display, (240,240,240), text_rect.inflate(20,10).move(0,-8), 5,10)
    display.blit(text_surface,text_rect)



pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Shooting")

clock = pygame.time.Clock()
running = True

star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
explosion_frame = [pygame.image.load(join('images','explosion',f'{i}.png')).convert_alpha()  for i in range(21)]
laser_sound = pygame.mixer.Sound(join('audio','laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio','damage.ogg'))
explosion_sound.set_volume(0.5)
game_music =  pygame.mixer.Sound(join('audio','game_music.wav'))
game_music.set_volume(0.2)
game_music.play(loops=-1)

all_sprite = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

for i in range(20):
    Star(all_sprite, star_surf)

player = Player(all_sprite)

meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

while running:
    dt = clock.tick() / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            Meteor(meteor_surf, (x, y), all_sprite, meteor_sprites)

    all_sprite.update(dt)
    player.laser_time()

    collisions()

    display.fill('#3a2e3f')
    all_sprite.draw(display)
    display_score()


    pygame.display.update()

pygame.quit()