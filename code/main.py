import pygame
import sys
import time
import math
from settings import *
from sprites import BG, Ground, Plane, Obstacle

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Flappy Bird')
GREEN = (0, 192, 0)
BLACK = (0, 0, 0)

def koch_snowflake(start_pos, end_pos, depth, angle_offset):
    """
    Рекурсивная функция для рисования фрактала снежинки Коха.
    start_pos: начальная позиция линии
    end_pos: конечная позиция линии
    depth: глубина рекурсии
    angle_offset: смещение угла для анимации
    """
    if depth == 0:
        # Рисование линии при достижении глубины 0
        pygame.draw.line(screen, GREEN, start_pos, end_pos, 1)
    else:
        x1, y1 = start_pos
        x5, y5 = end_pos

        # Вычисление новых точек делением линии на три части
        dx = (x5 - x1) / 3
        dy = (y5 - y1) / 3
        x2, y2 = x1 + dx, y1 + dy  # Первая треть
        # Вычисление вершины "треугольника" с учетом угла смещения
        x3, y3 = (x1 + x5) / 2 + math.cos(math.radians(angle_offset)) * (y1 - y5) / 3, (y1 + y5) / 2 + math.sin(math.radians(angle_offset)) * (x5 - x1) / 3
        x4, y4 = x1 + 2 * dx, y1 + 2 * dy  # Вторая треть

        # Рекурсивный вызов для каждой части линии
        koch_snowflake((x1, y1), (x2, y2), depth - 1, angle_offset)
        koch_snowflake((x2, y2), (x3, y3), depth - 1, angle_offset)
        koch_snowflake((x3, y3), (x4, y4), depth - 1, angle_offset)
        koch_snowflake((x4, y4), (x5, y5), depth - 1, angle_offset)

class Game:
    def __init__(self):
        # Основная настройка игры
        self.display_surface = screen
        self.clock = pygame.time.Clock()
        self.active = True

        # Создание групп спрайтов
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        # Масштабирование фона для заполнения экрана
        bg_height = pygame.image.load('graphics/environment/background (1).png').get_height()
        self.scale_factor = WINDOW_HEIGHT / bg_height

        # Инициализация спрайтов
        BG(self.all_sprites, self.scale_factor)
        Ground([self.all_sprites, self.collision_sprites], self.scale_factor)
        self.plane = Plane(self.all_sprites, self.scale_factor / 1.7)

        # Таймер для генерации препятствий
        self.obstacle_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.obstacle_timer, 1400)

        # Настройка шрифта для отображения счета
        self.font = pygame.font.Font('graphics/font/BD_Cartoon_Shout.ttf', 30)
        self.score = 0
        self.start_offset = 0

        # Меню
        self.menu_surf = pygame.image.load('graphics/ui/menu.png').convert_alpha()
        self.menu_rect = self.menu_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        # Музыка
        self.music = pygame.mixer.Sound('sounds/music.wav')
        self.music.play(loops=-1)

        # Угол для анимации фрактала
        self.angle_offset = 0

    def collisions(self):
        """
        Проверка столкновений между самолетом и препятствиями.
        """
        if pygame.sprite.spritecollide(self.plane, self.collision_sprites, False, pygame.sprite.collide_mask) or self.plane.rect.top <= 0:
            for sprite in self.collision_sprites.sprites():
                if sprite.sprite_type == 'obstacle':
                    sprite.kill()  # Удаление всех препятствий при столкновении
            self.active = False
            self.plane.kill()  # Удаление самолета

    def display_score(self):
        """
        Отображение текущего счета игрока.
        """
        if self.active:
            # Обновление счета в активном состоянии
            self.score = (pygame.time.get_ticks() - self.start_offset) // 1000
            y = WINDOW_HEIGHT / 10
        else:
            # Отображение счета в центре экрана, если игра неактивна
            y = WINDOW_HEIGHT / 2 + (self.menu_rect.height / 1.5)

        score_surf = self.font.render(str(self.score), True, 'black')
        score_rect = score_surf.get_rect(midtop=(WINDOW_WIDTH / 2, y))
        self.display_surface.blit(score_surf, score_rect)

    def draw_koch_snowflake(self):
        """
        Рисование анимированной снежинки Коха в верхней части экрана.
        """
        self.angle_offset += 1
        if self.angle_offset >= 360:
            self.angle_offset = 0

        # Начальные точки для снежинки Коха (сдвинутые вниз)
        size = 200  # Размер фрактала
        vertical_offset = 200  # Смещение вниз от верхнего края окна

        start_pos1 = (WINDOW_WIDTH // 2 - size // 2, vertical_offset)
        end_pos1 = (WINDOW_WIDTH // 2 + size // 2, vertical_offset)
        start_pos2 = end_pos1
        end_pos2 = (WINDOW_WIDTH // 2, vertical_offset - size * math.sqrt(3) // 2)
        start_pos3 = end_pos2
        end_pos3 = start_pos1

        # Рисование снежинки Коха
        koch_snowflake(start_pos1, end_pos1, 4, self.angle_offset)
        koch_snowflake(start_pos2, end_pos2, 4, self.angle_offset)
        koch_snowflake(start_pos3, end_pos3, 4, self.angle_offset)

    def run(self):
        """
        Основной цикл игры, который обрабатывает события, обновляет экран и проверяет состояние игры.
        """
        last_time = time.time()
        while True:
            # Вычисление delta time для плавной анимации
            dt = time.time() - last_time
            last_time = time.time()

            # Цикл обработки событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.active:
                        self.plane.jump()
                    else:
                        # Перезапуск игры при нажатии кнопки мыши, если игра неактивна
                        self.plane = Plane(self.all_sprites, self.scale_factor / 1.7)
                        self.active = True
                        self.start_offset = pygame.time.get_ticks()
                if event.type == self.obstacle_timer and self.active:
                    Obstacle([self.all_sprites, self.collision_sprites], self.scale_factor * 1.1)

            # Логика игры
            self.display_surface.fill('black')  # Очистка экрана
            self.all_sprites.update(dt)  # Обновление всех спрайтов
            self.all_sprites.draw(self.display_surface)  # Отрисовка всех спрайтов
            self.display_score()  # Отображение счета

            if self.active:
                self.collisions()  # Проверка столкновений
            else:
                # Отображение меню и рисование фрактала при неактивной игре
                self.display_surface.blit(self.menu_surf, self.menu_rect)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:
                    self.draw_koch_snowflake()

            pygame.display.update()  # Обновление экрана
            self.clock.tick(FRAMERATE)  # Ограничение кадров

if __name__ == '__main__':
    game = Game()
    game.run()
