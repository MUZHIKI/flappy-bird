import pygame
from settings import *
from random import choice, randint

# Класс для заднего фона
class BG(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)
        bg_image = pygame.image.load('graphics/environment/background (1).png').convert()

        # Масштабирование изображения фона до нужного размера
        full_height = bg_image.get_height() * scale_factor
        full_width = bg_image.get_width() * scale_factor
        full_sized_image = pygame.transform.scale(bg_image, (full_width, full_height))

        # Создание поверхности для изображения фона и дублирование для эффекта прокрутки
        self.image = pygame.Surface((full_width * 2, full_height))
        self.image.blit(full_sized_image, (0, 0))
        self.image.blit(full_sized_image, (full_width, 0))

        # Установка прямоугольника и позиции
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.pos = pygame.math.Vector2(self.rect.topleft)

    def update(self, dt):
        # Перемещение фона влево
        self.pos.x -= 300 * dt
        if self.rect.centerx <= 0:
            self.pos.x = 0  # Сброс позиции при полном смещении
        self.rect.x = round(self.pos.x)

# Класс для земли
class Ground(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)
        self.sprite_type = 'ground'

        # Загрузка и масштабирование изображения земли
        ground_surf = pygame.image.load('graphics/environment/ground (1).png').convert_alpha()
        self.image = pygame.transform.scale(ground_surf, pygame.math.Vector2(ground_surf.get_size()) * scale_factor)

        # Установка позиции земли
        self.rect = self.image.get_rect(bottomleft=(0, WINDOW_HEIGHT))
        self.pos = pygame.math.Vector2(self.rect.topleft)

        # Создание маски для коллизий
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        # Перемещение земли влево
        self.pos.x -= 360 * dt
        if self.rect.centerx <= 0:
            self.pos.x = 0  # Сброс позиции при полном смещении
        self.rect.x = round(self.pos.x)

# Класс для самолета
class Plane(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)

        # Загрузка кадров анимации самолета
        self.import_frames(scale_factor)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

        # Установка прямоугольника и позиции
        self.rect = self.image.get_rect(midleft=(WINDOW_WIDTH / 20, WINDOW_HEIGHT / 2))
        self.pos = pygame.math.Vector2(self.rect.topleft)

        # Параметры движения
        self.gravity = 600
        self.direction = 0

        # Создание маски для коллизий
        self.mask = pygame.mask.from_surface(self.image)

        # Загрузка звука прыжка
        self.jump_sound = pygame.mixer.Sound('sounds/jump.wav')
        self.jump_sound.set_volume(0.3)

    def import_frames(self, scale_factor):
        # Импорт кадров анимации самолета
        self.frames = []
        for i in range(3):
            surf = pygame.image.load(f'graphics/plane/red{i}.png').convert_alpha()
            scaled_surface = pygame.transform.scale(surf, pygame.math.Vector2(surf.get_size()) * scale_factor)
            self.frames.append(scaled_surface)

    def apply_gravity(self, dt):
        # Применение гравитации к самолету
        self.direction += self.gravity * dt
        self.pos.y += self.direction * dt
        self.rect.y = round(self.pos.y)

    def jump(self):
        # Прыжок самолета при нажатии кнопки
        self.jump_sound.play()
        self.direction = -400

    def animate(self, dt):
        # Анимация самолета
        self.frame_index += 10 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def rotate(self):
        # Вращение самолета в зависимости от направления движения
        rotated_plane = pygame.transform.rotozoom(self.image, -self.direction * 0.06, 1)
        self.image = rotated_plane
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        # Обновление состояния самолета
        self.apply_gravity(dt)
        self.animate(dt)
        self.rotate()

# Класс для препятствий
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)
        self.sprite_type = 'obstacle'

        # Выбор ориентации препятствия (вверх или вниз)
        orientation = choice(('up', 'down'))
        surf = pygame.image.load(f'graphics/obstacles/{choice((0, 1))}.png').convert_alpha()
        self.image = pygame.transform.scale(surf, pygame.math.Vector2(surf.get_size()) * scale_factor)

        # Установка позиции препятствия за пределами экрана
        x = WINDOW_WIDTH + randint(40, 100)

        if orientation == 'up':
            # Препятствие снизу
            y = WINDOW_HEIGHT + randint(10, 50)
            self.rect = self.image.get_rect(midbottom=(x, y))
        else:
            # Препятствие сверху
            y = randint(-50, -10)
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect = self.image.get_rect(midtop=(x, y))

        self.pos = pygame.math.Vector2(self.rect.topleft)

        # Создание маски для коллизий
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        # Перемещение препятствия влево
        self.pos.x -= 400 * dt
        self.rect.x = round(self.pos.x)
        if self.rect.right <= -100:
            self.kill()  # Удаление препятствия, когда оно выходит за пределы экрана
