import math

import pygame
import sys
import os
import random

GRAVITY_FORCE = 20
SIZE_X = 1200
SIZE_Y = 720
WINDOW_CAPTION = 'Murky gloom'

BRIGHTNESS_INFO = {
    10: [30, 0], 9: [60, 10], 8: [90, 20],
    7: [120, 30], 6: [150, 40], 5: [180, 50],
    4: [210, 60], 3: [240, 70], 2: [270, 80],
    1: [270, 90]
}
# Всего 7 уровней освещения, 7 - максимальный
# Словарь - каждому ключу соответствует нижняя
# граница расстояния, при котором будет этот уровень освещенности
# и второе число - сколько нано отнять от r,g,b начального цвета

PLATFORM_COLOR = (65,58,45)
# Цвет платформы при максимальном освещении

obstacles = pygame.sprite.Group()
entities = pygame.sprite.Group()
shots = pygame.sprite.Group()

darkness_radius = 180

darkness_area = pygame.Surface((SIZE_X, SIZE_Y), pygame.SRCALPHA)
darkness_area.fill((0, 0, 0))
pygame.draw.circle(darkness_area, (0, 0, 0, 0), (SIZE_X // 2, SIZE_Y // 2), darkness_radius)
platforms = []
player = None  # Чтобы пичярм не жаловался


def convert_level(level, path='misc/levels'):
    # Функция открывает текстовый файл, в котором содержатся необходимые игровые элементы ->
    # после чего создает список этих элементов(платформы, монстры и т.д).
    with open(f"""{path}/{level}.txt""", encoding='utf-8') as f:
        data = f.readlines()

    level = [i.rstrip() for i in data]
    platforms = []

    x = y = 0
    for row in level:
        for element in row:
            if element == "-":
                platform = Platform(30, 30, x, y, color=PLATFORM_COLOR)
                # obstacles.add(platform)
                platforms.append(platform)
            # elif element == "*":
            #     spike = Spike(30, 30, x, y) TODO spikes
            #     obstacles.add(spike)
            #     all_sprites.add(spike)
            #     platforms.append(spike)
            x += 30
        y += 30
        x = 0

    return platforms


def load_image(name, color_key=None):
    # Функция для загрузки текстур, name - название файла с папкой
    # например, 'textures/icon.png
    fullname = os.path.join('misc', name)
    if not os.path.isfile(fullname):
        raise FileNotFoundError
        sys.exit()
    image = pygame.image.load(fullname)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image.convert_alpha()
    return image


class Entity(pygame.sprite.Sprite):
    def __init__(self, size_x, size_y, x, y, texture=None, is_collide=True, health=None):
        # texture - название файла, как в load_image
        super().__init__(entities)
        self.size = self.size_x, self.size_y = size_x, size_y
        self.position = self.x, self.y = x, y
        self.health = health
        self.is_collide = is_collide
        self.is_immortal = False
        self.is_onground = True
        self.vel_x = 0  # velocity
        self.vel_y = 0

        self.image = load_image(texture)
        self.image = self.image
        self.rect = self.image.get_rect()
        self.rect = pygame.Rect(self.x, self.y, self.size_x, self.size_y)

        if health is None:
            self.is_immortal = True


class Player(Entity):
    def __init__(self, size_x, size_y, x, y, texture=None, is_collide=True, health=None):
        super().__init__(size_x, size_y, x, y, texture=texture, is_collide=True,
                         health=100)
        self.moving_velocity = 5
        self.jump_force = 20
        self.vel_y = GRAVITY_FORCE
        # Способ сделать красивые падения

        self.in_air = False

    def update(self, left, right, up):
        delta_x = 0  # Общее изменение
        delta_y = 0  # за всю работу функции
        if left:
            delta_x = -self.moving_velocity
        if right:
            delta_x = self.moving_velocity
        if up:
            if not self.in_air:
                self.vel_y = -self.jump_force
                self.in_air = True

        self.vel_y += 1
        if self.vel_y > GRAVITY_FORCE:
            self.vel_y = GRAVITY_FORCE
        delta_y += self.vel_y

        tmp_rect = self.rect.copy()
        # Rect для проверки на столкновение
        # Сделано для того, чтобы определить столкновение до того, как
        # настоящий игрок столкнется с препятствием

        for platform in platforms:

            tmp_rect.y = self.rect.y
            tmp_rect.x = self.rect.x + delta_x

            if platform.rect.colliderect(tmp_rect):
                delta_x = 0

            tmp_rect.x = self.rect.x
            tmp_rect.y = self.rect.y + delta_y

            if platform.rect.colliderect(tmp_rect):
                # Проверка на столкновение по y
                if self.vel_y < 0:
                    # Если летит вверх
                    delta_y = platform.rect.bottom - self.rect.top
                    self.vel_y = 0
                else:
                    # Если летит вниз
                    delta_y = platform.rect.top - self.rect.bottom
                    self.vel_y = 0
                    self.is_onground = True
            else:
                self.in_air = True

        if self.is_onground:
            self.in_air = False
        self.is_onground = False

        self.rect.x += delta_x
        self.rect.y += delta_y

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)  # - чтобы было удобно дебажить

    def get_coord(self):
        return self.rect.x, self.rect.y

    def kill(self):
        pass


class Platform:
    def __init__(self, size_x, size_y, x, y, color=(255, 255, 255)):
        self.size_x, self.size_y = size_x, size_y
        self.x, self.y = x, y
        self.color = color
        self.generate_pebbles(3)
        self.rect = pygame.Rect(self.x, self.y, self.size_x, self.size_y)

    def generate_pebbles(self, k):
        """Генерирует k камешков, так красиво"""
        pass  # TODO

    def draw(self, screen):
        # for light in lightsources: надо сделать, когда будут факелы
        #    pass
        player_x = player.rect.centerx
        player_y = player.rect.centery
        # Чтобы расстояние было не от левого верхнего

        distance_from_player = ((self.rect.centerx - player_x) ** 2 + (
                self.rect.centery - player_y) ** 2) ** 0.5
        # Просто нахождение расстояния между двумя точками
        distance_from_player = math.ceil(distance_from_player)  # чтобы int чтобы красиво
        is_changed = False
        tmp_color = None
        for i in BRIGHTNESS_INFO.keys():
            if distance_from_player <= BRIGHTNESS_INFO[i][0]:
                delta = BRIGHTNESS_INFO[i][1]
                tmp_color = [self.color[0] - delta, self.color[1] - delta, self.color[2] - delta]
                tmp_color = [i if i >= 0 else 0 for i in tmp_color]
                is_changed = True
                break

        if not is_changed:
            tmp_color = (0, 0, 0)

        pygame.draw.rect(screen, tmp_color, self.rect)


class Spike(Platform):
    def __init__(self, size_x, size_y, x, y, color=(0, 255, 0)):
        Platform.__init__(self, size_x, size_y, x, y, color)
        # Если мы пересекаемся с этим блоком то мы умераем (Земля пухом)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, color, facing):
        pygame.sprite.Sprite.__init__(self)
        self.x, self.y = x, y
        self.radius = radius
        self.color = color
        self.facing = facing
        self.speed = 10 * facing

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)


def main():
    global platforms, player
    pygame.init()
    pygame.display.set_caption(WINDOW_CAPTION)

    size = SIZE_X, SIZE_Y
    screen = pygame.display.set_mode(size)

    clock = pygame.time.Clock()
    player = Player(50, 50, 100, 100, texture='entities/arrow.png')  # TODO Поменять файл

    platforms = convert_level('level_1')

    bullets = []
    bullet_direction = 'Right'

    sprites = pygame.sprite.Group()

    left = False
    right = False
    up = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_LEFT, pygame.K_a]:
                left = True
                bullet_direction = 'Left'
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_RIGHT, pygame.K_d]:
                right = True
                bullet_direction = 'Right'
            if event.type == pygame.KEYUP and event.key in [pygame.K_RIGHT, pygame.K_d]:
                right = False
            if event.type == pygame.KEYUP and event.key in [pygame.K_LEFT, pygame.K_a]:
                left = False
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_UP, pygame.K_w,
                                                              pygame.K_SPACE]:
                up = True
            if event.type == pygame.KEYUP and event.key in [pygame.K_UP, pygame.K_w,
                                                            pygame.K_SPACE]:
                up = False

            if event.type == pygame.MOUSEBUTTONUP:
                facing = 1 if bullet_direction == 'Right' else -1
                bullets.append(
                    Bullet(player.get_coord()[0], player.get_coord()[1], 5, (100, 255, 0), facing))

        screen.fill((0, 0, 0))
        player.update(left, right, up)  # надо искать пересечения с списком platforms
        player.draw(screen)

        for bullet in bullets:
            if SIZE_X > bullet.x > 0:
                bullet.x += bullet.speed
            bullet.draw(screen)

        for platform in platforms:
            platform.draw(screen)

        pygame.display.flip()
        clock.tick(50)
    pygame.quit()


if __name__ == '__main__':
    main()
