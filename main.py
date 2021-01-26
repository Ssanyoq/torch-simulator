import datetime
import math
import random
import time

import pygame
import sys
import os
import menu
import files_manager

GRAVITY_FORCE = 20
SIZE = SIZE_X, SIZE_Y = 1200, 720
WINDOW_CAPTION = 'Murky gloom'
FPS = 60

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

PLATFORM_COLOR = (86, 72, 57)
# Цвет платформы при максимальном освещении
AIR_COLOR = (71, 57, 11)
FINISH_COLOR = (81, 59, 128)

obstacles = pygame.sprite.Group()
entities = pygame.sprite.Group()
enemies = []
all_sprites = pygame.sprite.Group()
shots = pygame.sprite.Group()
light_sources = []
# Список с rect источников света

darkness_radius = 180

darkness_area = pygame.Surface((SIZE_X, SIZE_Y), pygame.SRCALPHA)
darkness_area.fill((0, 0, 0))
pygame.draw.circle(darkness_area, (0, 0, 0, 0), (SIZE_X // 2, SIZE_Y // 2), darkness_radius)
platforms = []
air_blocks = []
torches = []
player = None  # Чтобы пичярм не жаловался


def convert_level(level, path='misc/levels'):
    # Функция открывает текстовый файл, в котором содержатся необходимые игровые элементы ->
    # после чего создает список этих элементов(платформы, монстры и т.д).
    with open(f"""{path}/{level}.txt""", encoding='utf-8') as f:
        data = f.readlines()

    level = [i.rstrip() for i in data]
    platforms = []
    decoratives = []
    player_x, player_y = 0, 0

    x = y = 0
    i = 0
    max_string_length = int(len(max(level, key=lambda x: len(x))))
    # Чтобы края закрывать красивым чем-нибудь

    for i in range(5):
        # Сделано для красивых краев, чтобы не было белых частей
        for _ in range(max_string_length + 3):
            platform = Platform(30, 30, x, y, color=PLATFORM_COLOR)
            all_sprites.add(platform)
            platforms.append(platform)
            x += 30
        x = 0
        y += 30

    for i, row in enumerate(level):
        for j in range(3):
            platform = Platform(30, 30, x, y, color=PLATFORM_COLOR)
            all_sprites.add(platform)
            platforms.append(platform)
            x += 30
        for k, element in enumerate(row):
            if element == "-":
                platform = Platform(30, 30, x, y, color=PLATFORM_COLOR)
                # obstacles.add(platform)
                platforms.append(platform)
                obstacles.add(platform)
                all_sprites.add(platform)
            elif element == "*":
                spike = Spike(30, 30, x, y)  # TODO
                obstacles.add(spike)
                all_sprites.add(spike)
                platforms.append(spike)
            elif element.lower() == 'e' or element.lower() == 'е':
                if len(level) - 1 == i:
                    continue
                bottom_line = list(level[i + 1])
                if len(bottom_line) - 1 < k:
                    air = Air(30, 30, x, y, color=AIR_COLOR)
                    decoratives.append(air)
                    continue
                elif bottom_line[k] != '-':
                    air = Air(30, 30, x, y, color=AIR_COLOR)
                    decoratives.append(air)
                    continue
                stopped = False
                left_from_enemy = bottom_line[:k + 1][::-1]
                for j, symbol in enumerate(left_from_enemy):
                    if symbol != '-':
                        max_path_left = (j - 1) * 30
                        stopped = True
                        break
                if not stopped:
                    max_path_left = k * 30
                stopped = False
                right_from_enemy = bottom_line[k:]
                for j, symbol in enumerate(right_from_enemy):
                    if symbol != '-':
                        max_path_right = (j - 1) * 30
                        stopped = True
                        break
                if not stopped:
                    max_path_right = (len(row) - k) * 30
                enemy = Enemy(30, 30, x, y, max_path_right, max_path_left,
                              texture='textures/platform.jpeg')
                enemies.append(enemy)
                all_sprites.add(enemy)

                air = Air(30, 30, x, y, color=AIR_COLOR)
                decoratives.append(air)
            elif element.lower() == 's':
                player_x, player_y = x, y
                air = Air(30, 30, x, y, color=AIR_COLOR)
                decoratives.append(air)
            elif element.lower() == 'f':
                finish = Air(30, 30, x, y, finish=True, color=FINISH_COLOR)
                decoratives.append(finish)
            else:
                air = Air(30, 30, x, y, color=AIR_COLOR)
                decoratives.append(air)
            x += 30

        for j in range(max_string_length + 3 - (len(row) + 3)):
            platform = Platform(30, 30, x, y, color=PLATFORM_COLOR)
            all_sprites.add(platform)
            platforms.append(platform)
            x += 30
        y += 30
        x = 0

    for i in range(5):
        # Сделано для красивых краев, чтобы не было белых частей
        for _ in range(max_string_length + 3):
            platform = Platform(30, 30, x, y, color=PLATFORM_COLOR)
            all_sprites.add(platform)
            platforms.append(platform)
            x += 30
        x = 0
        y += 30

    return platforms, decoratives, player_x, player_y


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


def clear_stuff(screen):
    global obstacles, player, entities, enemies, all_sprites, shots, platforms, air_blocks, \
        light_sources, torches
    player = None
    obstacles = pygame.sprite.Group()
    entities = pygame.sprite.Group()
    enemies = []
    all_sprites = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    platforms = []
    air_blocks = []
    light_sources = []
    torches = []


def change_color(color, center_x, center_y, light_x,
                 light_y, brightness_level=0):
    """
    Изменяет цвет в зависимости
    от расстояния точки (center_x, center_y) до
    источников света
    :param color: начальный цвет
    :param center_x: x предмета
    :param center_y: y предмета
    :param light_x: x источника света
    :param light_y: y источника света
    :param brightness_level: настоящий
    уровень освещенности предмета
    :return: новый цвет и уровень освещенности
    """
    distance = ((center_x - light_x) ** 2 + (
            center_y - light_y) ** 2) ** 0.5
    # Просто нахождение расстояния между двумя точками
    distance = math.ceil(distance)  # Чтобы int чтобы красиво

    is_changed = False
    new_color = None
    for i in BRIGHTNESS_INFO.keys():
        if distance <= BRIGHTNESS_INFO[i][0]:
            if i > brightness_level:
                brightness_level = i
            delta = BRIGHTNESS_INFO[brightness_level][1]
            new_color = [color[0] - delta, color[1] - delta, color[2] - delta]
            new_color = [j if j >= 0 else 0 for j in new_color]
            is_changed = True
            break

    if not is_changed:
        if brightness_level != 0:
            delta = BRIGHTNESS_INFO[brightness_level][1]
            new_color = [color[0] - delta, color[1] - delta, color[2] - delta]
            new_color = [j if j >= 0 else 0 for j in new_color]
        else:
            new_color = [0, 0, 0]

    return new_color, brightness_level


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, is_left=False):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.image = self.frames[0]
        self.rect = self.rect.move(x, y)
        self.is_left = is_left
        if is_left:
            for i, frame in enumerate(self.frames):
                self.frames[i] = pygame.transform.flip(frame, True, False)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, x, y, frame):
        x -= 5
        if self.is_left:
            x -= 20
        frame = frame % len(self.frames)
        self.image = self.frames[frame]
        screen.blit(self.image, (x, y))


class Entity(pygame.sprite.Sprite):
    def __init__(self, size_x, size_y, x, y, texture=None, is_collide=True, health=None):
        # texture - название файла, как в load_image
        super().__init__(entities)
        self.size = self.size_x, self.size_y = size_x, size_y
        self.position = self.x, self.y = x, y
        self.health = health
        self.is_collide = is_collide
        self.is_immortal = False
        self.is_onground = False
        self.moving_velocity = 5

        if texture is None:
            self.image = pygame.Surface((size_x, size_y))
            self.image.fill(pygame.Color((0, 0, 0)))
            self.rect = pygame.Rect(x, y, size_x, size_y)
        else:
            self.image = load_image(texture)
            self.image = self.image
            self.rect = self.image.get_rect()
            self.rect = pygame.Rect(self.x, self.y, self.size_x, self.size_y)

        if health is None:
            self.is_immortal = True


class Player(Entity):
    def __init__(self, size_x, size_y, x, y, texture=None, is_collide=True, health=None, torches=0):
        super().__init__(size_x, size_y, x, y, texture=texture, is_collide=True, health=100)
        self.jump_force = 15
        self.vel_y = GRAVITY_FORCE
        self.facing = 1
        # Способ сделать красивые падения

        self.in_air = False
        self.won = False

        self.delta_x, self.delta_y = 0, 0
        self.torches = torches
        self.was_flying = False
        # Переменная, показывающая, был ли персонаж в
        # воздухе кадр назад
        self.torch_placed = False
        # Был ли поставлен торч

        self.frame = 0
        self.animation_before = None
        # Переменная, где показывается, какая анимация была в
        # прошлый вызов функции update
        self.idle_right = AnimatedSprite(load_image('entities/player/idle.png'), 4, 1, 50, 50)
        self.jump_r = AnimatedSprite(load_image("entities/player/jump.png"), 6, 1, 50, 50)
        self.run_r = AnimatedSprite(load_image("entities/player/run.png"), 6, 1, 50, 50)
        self.place_r = AnimatedSprite(load_image("entities/player/placing.png"), 6, 1, 50, 50)

        self.idle_left = AnimatedSprite(
            load_image('entities/player/idle.png'), 4, 1, 50, 50, True)
        self.jump_l = AnimatedSprite(
            load_image("entities/player/jump.png"), 6, 1, 50, 50, True)

        self.run_l = AnimatedSprite(
            load_image("entities/player/run.png"), 6, 1, 50, 50, True)
        self.place_l = AnimatedSprite(load_image('entities/player/placing.png'), 6, 1, 50, 50, True)

    def update(self, left, right, up):
        self.delta_x = 0  # Общее изменение
        self.delta_y = 0  # за всю работу функции

        self.frame = self.frame % 30

        if up:
            if not self.in_air:
                self.vel_y = -self.jump_force
                self.in_air = True
        if right:
            self.facing = 1
            self.delta_x = self.moving_velocity

        if left:
            self.facing = -1
            self.delta_x = -self.moving_velocity

        self.vel_y += 1
        if self.vel_y > GRAVITY_FORCE:
            self.vel_y = GRAVITY_FORCE
        self.delta_y += self.vel_y

        tmp_rect = self.rect.copy()
        # Rect для проверки на столкновение
        # Сделано для того, чтобы определить столкновение до того, как
        # настоящий игрок столкнется с препятствием

        for platform in platforms:

            tmp_rect.y = self.rect.y
            tmp_rect.x = self.rect.x + self.delta_x

            if platform.rect.colliderect(tmp_rect):
                self.delta_x = 0

            tmp_rect.x = self.rect.x
            tmp_rect.y = self.rect.y + self.delta_y

            if platform.rect.colliderect(tmp_rect):
                # Проверка на столкновение по y
                if platform.kill_if_touched:
                    return True
                if self.vel_y < 0:
                    # Если летит вверх
                    self.delta_y = platform.rect.bottom - self.rect.top
                    self.vel_y = 0
                else:
                    # Если летит вниз
                    self.delta_y = platform.rect.top - self.rect.bottom
                    self.vel_y = 0
                    self.is_onground = True
            else:
                self.in_air = True
        x, y = self.rect.x, self.rect.y
        # Анимации
        if self.is_onground:
            self.in_air = False
            if self.torch_placed:
                if self.animation_before != 'placing':
                    self.frame = 0
                    self.animation_before = 'placing'
                if self.facing == 1:
                    self.place_r.update(x, y, self.frame // 3)
                    # // 3 чтобы дольше длилась
                else:
                    self.place_l.update(x, y, self.frame // 3)

            elif self.was_flying:
                # Только приземлился, так что круто
                if self.animation_before != 'landing':
                    self.frame = 0
                    self.animation_before = 'landing'

                if self.facing == 1:
                    self.jump_r.update(x, y, 6 - self.frame)
                else:
                    self.jump_l.update(x, y, 6 - self.frame)

            elif self.delta_x < 0 or self.delta_x > 0:
                if self.animation_before != 'run':
                    self.frame = 0
                    self.animation_before = 'run'

                if self.delta_x > 0:
                    # Идет вправо
                    self.run_r.update(x, y, self.frame // 6)
                else:
                    # Идет влево
                    self.run_l.update(x, y, self.frame // 6)

            else:
                # АФК (ну типа)
                if self.animation_before != 'idle':
                    self.frame = 0
                    self.animation_before = 'idle'

                if self.facing == 1:
                    self.idle_right.update(x, y, self.frame // 4)
                else:
                    self.idle_left.update(x, y, self.frame // 4)

        else:
            if self.delta_y < 0:
                # Прыгает
                if self.animation_before != 'jump':
                    self.animation_before = 'jump'
                    self.frame = 0

                if self.frame >= 2:
                    # Чтобы не повторялась анимация
                    self.frame = 2
                if self.facing == 1:
                    self.jump_r.update(x, y, self.frame)
                else:
                    self.jump_l.update(x, y, self.frame)
            else:
                # Падает
                if self.animation_before != 'drop':
                    self.animation_before = 'drop'

                if self.facing == 1:
                    self.jump_r.update(x, y, 3)
                else:
                    self.jump_l.update(x, y, 3)

        self.is_onground = False

        self.rect.x += self.delta_x
        self.rect.y += self.delta_y
        self.frame += 1

        if self.frame == 3 and self.animation_before == 'landing':
            self.was_flying = False

        if self.animation_before == 'placing' and self.frame // 3 == 6:
            self.torch_placed = False

        if self.in_air:
            self.was_flying = True

        pygame.draw.rect(screen, (0, 0, 200), self.rect, 3)  # hitbox

    def get_coord(self):
        return self.rect.x, self.rect.y

    def try_placing_torch(self):
        if not self.in_air and self.torches > 0:
            if self.facing == 1:
                torch = Torch(self.rect.bottomright[0] - 3, self.rect.bottomright[1])
            else:
                torch = Torch(self.rect.bottomleft[0] + 3, self.rect.bottomleft[1])
            self.torch_placed = True
            self.torches -= 1
            print(self.torches)


class Enemy(Entity):
    def __init__(self, size_x, size_y, x, y, max_length_right, max_length_left,
                 texture=None, is_collide=True, health=None):
        super().__init__(size_x, size_y, x, y, texture=texture, is_collide=True, health=100)
        self.start_x = x
        self.facing = 1
        self.moving_velocity -= 3
        self.to_left_border = max_length_left
        self.to_right_border = max_length_right

    def update(self):
        """
        :return: True, если соприкоснулся с игроком, иначе False
        """
        if self.to_left_border <= 0 and self.facing == -1:
            self.facing = 1
        elif self.to_right_border <= 0 and self.facing == 1:
            self.facing = -1
        else:
            self.to_left_border += self.moving_velocity * self.facing
            self.to_right_border -= self.moving_velocity * self.facing
            self.rect.x += self.moving_velocity * self.facing

        for platform in platforms:
            if pygame.sprite.collide_rect(self, platform) and self != platform:
                self.facing *= -1
        if self.rect.colliderect(player.rect):
            return True
        return False

    def draw(self, screen):
        pygame.draw.rect(screen, (44, 3, 9), self.rect)


class Platform(pygame.sprite.Sprite):
    """Наследуется от sprite только для того, чтобы камера работала"""

    def __init__(self, size_x, size_y, x, y, color=(255, 255, 255), pebble_color=(50, 50, 50),
                 pebble_amount=2):
        super().__init__(obstacles)
        self.size_x, self.size_y = size_x, size_y
        self.x, self.y = x, y
        self.color = color
        self.pebble_color = pebble_color
        self.rect = pygame.Rect(self.x, self.y, self.size_x, self.size_y)
        self.static_brightness = 0
        # Переменная, где записан уровень освещенности от статичных
        # источников света (факелов)
        self.pebbles = []
        self.generate_pebbles(pebble_amount)
        self.kill_if_touched = False
        # Для spikes

    def generate_pebbles(self, k):
        """Генерирует k камешков"""
        for i in range(k):
            width = height = random.randint(5, 10)
            pos_x = random.randint(1, self.size_x - width - 1)
            pos_y = random.randint(1, self.size_y - height - 1)
            # Можно было просто 2 раза расчитать pos_x и y,
            # но тогда камешки могут быть очень большими

            pebble_rect = pygame.Rect(pos_x, pos_y, width, height)
            self.pebbles.append(pebble_rect)

    def draw(self, screen):
        tmp_color, brightness = change_color(self.color, self.rect.centerx, self.rect.centery,
                                             player.rect.centerx, player.rect.centery,
                                             self.static_brightness)
        pygame.draw.rect(screen, tmp_color, self.rect)
        if brightness != 0:
            delta = BRIGHTNESS_INFO[brightness][1]
            pebble_color = [self.pebble_color[0] - delta, self.pebble_color[1] - delta,
                            self.pebble_color[2] - delta]
            pebble_color = [i if i >= 0 else 0 for i in pebble_color]
        else:
            pebble_color = [0, 0, 0]
        for pebble in self.pebbles:
            pebble_rect = pygame.Rect(pebble.x + self.rect.x, pebble.y + self.rect.y,
                                      pebble.width, pebble.height)
            pygame.draw.rect(screen, pebble_color, pebble_rect)


class Spike(Platform):
    def __init__(self, size_x, size_y, x, y, color=(88, 15, 15)):
        Platform.__init__(self, size_x, size_y, x, y, color, pebble_amount=4,
                          pebble_color=(98, 65, 33))
        self.kill_if_touched = True
        # Если мы пересекаемся с этим блоком то мы умераем (Земля пухом)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, color, facing):
        pygame.sprite.Sprite.__init__(self)
        self.x, self.y = x, y
        self.radius = radius
        self.color = color
        self.facing = facing
        self.speed = 10 * facing
        self.damage = 25

        self.image = pygame.Surface((2 * radius, 2 * radius))
        pygame.draw.circle(self.image, pygame.Color((255, 255, 0)), (radius, radius), radius)
        self.rect = pygame.Rect(self.x, self.y, 2 * radius, 2 * radius)


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0

    def apply(self, obj):
        obj.rect.x += self.x
        obj.rect.y += self.y

    def update(self, target):
        if target.rect.centerx + target.delta_x > SIZE_X - 200 - self.x or \
                target.rect.centerx + target.delta_x < 0 - self.x + 120:
            self.x = -target.delta_x
        else:
            self.x = 0
        if target.rect.centery + target.delta_y > SIZE_Y - 120 - self.y:
            self.y = -target.delta_y if target.delta_y != 0 else -GRAVITY_FORCE

        elif target.rect.centery + target.delta_y < 120 + self.y:
            self.y = -target.delta_y
        else:
            self.y = 0


class Air(pygame.sprite.Sprite):
    """Сделано для красивого освещения"""

    def __init__(self, size_x, size_y, x, y, finish=False, color=(255, 255, 255)):
        super().__init__(all_sprites)
        self.size_x, self.size_y = size_x, size_y
        self.x, self.y = x, y
        self.static_brightness = 0
        self.color = color
        self.finish = finish
        self.rect = pygame.Rect(self.x, self.y, self.size_x, self.size_y)
        air_blocks.append(self)

    def draw(self, screen):
        if self.rect.colliderect(player.rect) and self.finish:
            player.won = True
        tmp_color, brightness = change_color(self.color, self.rect.centerx, self.rect.centery,
                                             player.rect.centerx, player.rect.centery,
                                             self.static_brightness)
        pygame.draw.rect(screen, tmp_color, self.rect)


class Torch(pygame.sprite.Sprite):
    def __init__(self, bottom_x, bottom_y, bottom_size_x=3, bottom_size_y=10,
                 bottom_color=(50, 50, 50),
                 upper_color=(255, 156, 50)):
        """
        Факел разбит на 2 части: верхнюю и нижнюю
        Верхняя часть - часть, из которой исходит свет,
        нижняя часть - просто темная подставка под
        светящуюся часть
        X и y верхней части равны bottom_size_x
        :param bottom_x: x нижнего левого угла факела
        :param bottom_y: y нижнего левого угла факела
        :param bottom_size_x: размер нижней части факела (сделано)'
        :param bottom_size_y:
        """
        super().__init__(all_sprites)
        self.bottom_color = bottom_color
        self.upper_color = upper_color

        self.rect = pygame.Rect(bottom_x, bottom_y, bottom_size_x, bottom_size_y)
        # self.rect сделан таким, чтобы было удобно вычислять bottom и upper rect

        self.bottom_rect = pygame.Rect(self.rect.x - self.rect.width,
                                       self.rect.y - self.rect.height,
                                       self.rect.width, self.rect.height)
        self.upper_rect = pygame.Rect(self.bottom_rect.x,
                                      self.bottom_rect.y - self.bottom_rect.width,
                                      self.bottom_rect.width, self.bottom_rect.width
                                      )
        self.change_static_light()
        light_sources.append(self.upper_rect)
        torches.append(self)

    def draw(self, screen):
        self.bottom_rect = pygame.Rect(self.rect.x - self.rect.width,
                                       self.rect.y - self.rect.height,
                                       self.rect.width, self.rect.height)
        self.upper_rect = pygame.Rect(self.bottom_rect.x,
                                      self.bottom_rect.y - self.bottom_rect.width,
                                      self.bottom_rect.width, self.bottom_rect.width
                                      )
        pygame.draw.rect(screen, self.bottom_color, self.bottom_rect)
        pygame.draw.rect(screen, self.upper_color, self.upper_rect)

    def change_static_light(self):
        for platform in platforms:
            color, brightness_lvl = change_color((0, 0, 0), platform.rect.centerx,
                                                 platform.rect.centery, self.upper_rect.centerx,
                                                 self.upper_rect.centery,
                                                 platform.static_brightness)
            platform.static_brightness = brightness_lvl
        for air in air_blocks:
            color, brightness_lvl = change_color((0, 0, 0), air.rect.centerx,
                                                 air.rect.centery, self.upper_rect.centerx,
                                                 self.upper_rect.centery,
                                                 air.static_brightness)
            air.static_brightness = brightness_lvl


def main(level):
    global platforms, player, screen
    pygame.init()

    pygame.display.set_caption(WINDOW_CAPTION)
    screen = pygame.display.set_mode(SIZE)

    platforms, decoratives, player_x, player_y = convert_level(level)
    coins, torches_amount, level_data = files_manager.load_player_data()
    player = Player(20, 50, player_x, player_y, torches=torches_amount)
    all_sprites.add(player)
    start_time = time.time()
    # start_time - время, которое будет считаться как
    # время прохождения уровня, в секундах, float
    # (переделывается в читабельную дату через
    # datetime.datetime.utcfromtimestamp(start_time))

    bullets = []
    facing = 1  # Направление пуль, изначально пули летят вправо

    camera = Camera()  # Создаем камеру

    # darkness_rect = pygame.Rect((0, 0), (darkness_radius * 2, darkness_radius * 2),)
    # screen.set_clip(darkness_rect) TODO включить
    # Поверх экрана происходит отрисовка прямоугольника с вырезанным по середине кругом (Темнота)

    left = False
    right = False
    up = False

    clock = pygame.time.Clock()

    paused = False
    running = True
    while running:
        if player.won:
            level_data[level] = start_time
            coins += 5
            print(f"level {level} completed at {datetime.datetime.utcfromtimestamp(start_time)}")
            files_manager.save_player_data(coins,player.torches,level_data)
            menu.ending_screen(screen)
            return None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                files_manager.save_player_data(coins,player.torches,level_data)
                running = False
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_LEFT, pygame.K_a]:
                left = True
                facing = -1  # Запоминаем направление пули
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_RIGHT, pygame.K_d]:
                right = True
                facing = 1  # Запоминаем направление пули
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

            if event.type == pygame.MOUSEBUTTONDOWN and not paused:
                if event.button == 1:
                    bullet = Bullet(player.rect.x + 25 // 2, player.rect.y + 25 // 2,
                                    5, (100, 255, 0), facing)
                    shots.add(bullet)
                    bullets.append(bullet)
                elif event.button == 3:
                    player.try_placing_torch()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = not paused

        if not paused:  # Если игра не на паузе отрисовываем главную сцену, иначе меню паузы
            screen.fill((0, 0, 0))

            for platform in platforms:
                platform.draw(screen)

            for decorative in decoratives:
                decorative.draw(screen)

            for torch in torches:
                torch.draw(screen)

            for bullet in bullets:
                if SIZE_X > bullet.x > 0 and not pygame.sprite.spritecollideany(bullet, obstacles):
                    bullet.rect.x += bullet.speed
                else:
                    bullets.pop(bullets.index(bullet))
                    shots.remove(bullet)

            shots.update(bullets)
            shots.draw(screen)

            for enemy in enemies:
                died = enemy.update()
                enemy.draw(screen)
                if died:
                    files_manager.save_player_data(coins, player.torches, level_data)
                    menu.ending_screen(screen, False)
                    return None

            died = player.update(left, right, up)
            camera.update(player)

            for sprite in all_sprites:
                camera.apply(sprite)
            # obstacles.draw(screen)

            # screen.blit(darkness_area, darkness_rect) TODO раскомментить
            screen.set_clip(None)

            pygame.display.flip()
            clock.tick(FPS)
            if died:
                files_manager.save_player_data(coins, player.torches, level_data)
                menu.ending_screen(screen, False)
                return None

        else:  # TODO починить отрисовку
            button_pos_y = 300
            up, left, right = False, False, False
            buttons = []
            # Список вида [[rect кнопки, функция, которой соответствует эта кнопка]]
            # Вернется в меню, если было нажатие на кнопку с индексом 5
            # Можно было сделать просто если индекс == чему-то, то что-то вызвать,
            # но тогда неуниверсально

            for i in range(2):
                button = pygame.draw.rect(screen, (210, 210, 210), (350, button_pos_y, 530, 60))
                button_pos_y += 100
                buttons.append([button, None])

            buttons_texts = ["    Continue", "Back to menu"]
            text_pos_y = 315
            text_delta = 100

            menu.draw_texts(screen, buttons_texts, 500, text_pos_y, text_delta)

            for i in range(len(buttons)):
                text = buttons_texts[i].lower().strip()
                # Чтобы красиво
                buttons[i] = [buttons[i][0], text]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    files_manager.save_player_data(coins, player.torches, level_data)
                    break

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for button in buttons:
                            if pygame.Rect.collidepoint(button[0], pygame.mouse.get_pos()):
                                if button[1] == 'continue':
                                    paused = False
                                elif button[1] == 'back to menu':
                                    screen.fill((0, 0, 0))
                                    files_manager.save_player_data(coins, player.torches,
                                                                   level_data)
                                    clear_stuff(screen)
                                    menu.start_screen()
                                    return None
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    paused = not paused
                pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main('level_1')  # TODO изменить
