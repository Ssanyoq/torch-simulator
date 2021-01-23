import math
import random
import pygame
import sys
import os
import menu
import files_manager

GRAVITY_FORCE = 20
SIZE = SIZE_X, SIZE_Y = 1200, 720
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

PLATFORM_COLOR = (86, 72, 57)
# Цвет платформы при максимальном освещении
AIR_COLOR = (71, 57, 11)
FINISH_COLOR = (81, 59, 128)

obstacles = pygame.sprite.Group()
entities = pygame.sprite.Group()
enemies = pygame.sprite.Group()
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
    count = 0
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

    for row in level:
        for i in range(3):
            platform = Platform(30, 30, x, y, color=PLATFORM_COLOR)
            all_sprites.add(platform)
            platforms.append(platform)
            x += 30
        for element in row:
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
            elif element == 'E':
                a = [i for i in level[count + 1]]
                max_length_right = a[x // 30:].index(' ') * 30
                max_length_left = a[:x // 30][::-1].index(' ') * 30
                if not max_length_right == max_length_left == 0:
                    # Если враг не на платформе, то мы его не создаем :(
                    enemy = Enemy(30, 30, x, y, max_length_right, max_length_left,
                                  texture='textures/platform.jpeg')
                    enemies.add(enemy)
                    all_sprites.add(enemy)
            elif element == 'S':
                player_x, player_y = x, y
                air = Air(30, 30, x, y, color=AIR_COLOR)
                decoratives.append(air)
            elif element == 'F':
                finish = Air(30, 30, x, y, finish=True, color=FINISH_COLOR)
                decoratives.append(finish)
            else:
                air = Air(30, 30, x, y, color=AIR_COLOR)
                decoratives.append(air)
            x += 30

        for i in range(max_string_length + 3 - (len(row) + 3)):
            platform = Platform(30, 30, x, y, color=PLATFORM_COLOR)
            all_sprites.add(platform)
            platforms.append(platform)
            x += 30
        count += 1
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
    global obstacles, player, entities, enemies, all_sprites, shots, platforms
    player = None
    obstacles = pygame.sprite.Group()
    entities = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    platforms = []


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

        self.image = load_image(texture)
        self.image = self.image
        self.rect = self.image.get_rect()
        self.rect = pygame.Rect(self.x, self.y, self.size_x, self.size_y)

        if health is None:
            self.is_immortal = True


class Player(Entity):
    def __init__(self, size_x, size_y, x, y, texture=None, is_collide=True, health=None, torches=0):
        super().__init__(size_x, size_y, x, y, texture=texture, is_collide=True, health=100)
        self.jump_force = 20
        self.vel_y = GRAVITY_FORCE
        # Способ сделать красивые падения

        self.in_air = False
        self.won = False

        self.delta_x, self.delta_y = 0, 0
        self.torches = torches

    def update(self, left, right, up):
        self.delta_x = 0  # Общее изменение
        self.delta_y = 0  # за всю работу функции
        if left:
            self.delta_x = -self.moving_velocity
        if right:
            self.delta_x = self.moving_velocity
        if up:
            if not self.in_air:
                self.vel_y = -self.jump_force
                self.in_air = True

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
            tmp_rect.x = self.rect.x + delta_x

            if platform.rect.colliderect(tmp_rect):
                self.delta_x = 0

            tmp_rect.x = self.rect.x
            tmp_rect.y = self.rect.y + self.delta_y

            if platform.rect.colliderect(tmp_rect):
                # Проверка на столкновение по y
                if self.vel_y < 0:
                    # Если летит вверх
                    self.delta_y = platform.rect.bottom - self.rect.top
                    self.vel_y = 0
                else:
                    # Если летит вниз
                    delta_y = platform.rect.top - self.rect.bottom
                    self.vel_y = 0
                    self.is_onground = True
            else:
                self.in_air = True

        for enemy in enemies:
            if pygame.sprite.collide_rect(self, enemy):
                self.health -= 1  # TODO сделать удары рагов

        if self.is_onground:
            self.in_air = False
        self.is_onground = False

        self.rect.x += self.delta_x
        self.rect.y += self.delta_y

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
        # pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)  # - чтобы было удобно дебажить

    def get_coord(self):
        return self.rect.x, self.rect.y

    def try_placing_torch(self):
        if not self.in_air:
            torch = Torch(*self.rect.bottomleft)
            print('Working')
        else:
            print('not')

    def kill(self):
        pass


class Enemy(Entity):
    def __init__(self, size_x, size_y, x, y, max_length_right, max_length_left,
                 texture=None, is_collide=True, health=None):
        super().__init__(size_x, size_y, x, y, texture=texture, is_collide=True, health=100)
        self.max_length_right = max_length_right
        self.max_length_left = max_length_left
        self.x_vel = max_length_right

        if self.x_vel - self.size_x == 0:
            self.facing = -1
        else:
            self.facing = 1

    def update(self):
        self.rect.x += (self.moving_velocity - 3) * self.facing
        self.x_vel -= (self.moving_velocity - 3) * self.facing

        if self.x_vel - self.size_x == 0 and self.facing == 1:
            self.facing = -1
        elif self.x_vel > self.max_length_right + self.max_length_left and self.facing == -1:
            self.facing = 1

        for platform in platforms:
            if pygame.sprite.collide_rect(self, platform):
                self.facing = -1 if self.facing == 1 else 1
                self.is_on_ground = True

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Platform(pygame.sprite.Sprite):
    """Наследуется от sprite только для того, чтобы камера работала"""

    def __init__(self, size_x, size_y, x, y, color=(255, 255, 255), pebble_color=(50, 50, 50)):
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
        self.generate_pebbles(2)

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
        self.damage = 25

        self.image = pygame.Surface((2 * radius, 2 * radius))
        pygame.draw.circle(self.image, pygame.Color((255, 255, 0)), (radius, radius), radius)
        self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - SIZE_X // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - SIZE_Y // 2)
        if target.rect.centerx + target.delta_x > SIZE_X - 120 - self.x or \
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
    global platforms, player
    pygame.init()

    pygame.display.set_caption(WINDOW_CAPTION)
    screen = pygame.display.set_mode(SIZE)

    platforms, player_x, player_y = convert_level(level)  # Level передается через level_screen и start_screen

    player = Player(50, 50, player_x, player_y, texture='entities/arrow.png')  # TODO Поменять файл
    all_sprites.add(player)  # Создаем персонажа
    platforms, decoratives, player_x, player_y = convert_level(level)
    player = Player(50, 50, player_x, player_y - 20,
                    texture='entities/arrow.png')  # TODO Поменять файл
    all_sprites.add(player)

    bullets = []
    bullets_quantity = 10
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
            menu.win_window(screen)
            return None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
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
            if event.type == pygame.KEYUP and event.key == pygame.K_r:
                main("level_1")
                return None

            if event.type == pygame.MOUSEBUTTONDOWN and not paused:
                if event.button == 1:
                    bullet = Bullet(player.rect.x + 25 // 2, player.rect.y + 25 // 2,
                                    5, (100, 255, 0), facing)
                    shots.add(bullet)
                    bullets.append(bullet)
                elif event.button == 3:
                    player.try_placing_torch()
            if player.rect.x == 570:
                facing = -1
            elif player.rect.x == 580:
                facing = 1
            # Стреляем туда куда движется игрок

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and not paused\
                    and bullets_quantity > 0:
                bullet = Bullet(player.rect.x + 25 // 2, player.rect.y + 25 // 2,
                                5, (100, 255, 0), facing)
                shots.add(bullet)
                bullets.append(bullet)
                bullets_quantity -= 1

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = not paused

        if not paused:  # Если игра не на паузе отрисовываем главную сцену, иначе меню паузы
            screen.fill((255, 255, 255))

            enemies.update()
            enemies.draw(screen)

            for platform in platforms:
                platform.draw(screen)

            for decorative in decoratives:
                decorative.draw(screen)

            for torch in torches:
                torch.draw(screen)

            if player.health < 0:
                menu.end_screen(screen, False, level)

            for hit in pygame.sprite.groupcollide(enemies, shots, True, True):
                enemies.remove(hit)  # Убиваем врага если по нему попала пуля

            for bullet in bullets:
                if SIZE_X > bullet.x > 0 and not pygame.sprite.spritecollideany(bullet, obstacles)\
                        and not pygame.sprite.spritecollideany(bullet, enemies):
                    bullet.rect.x += bullet.speed
                    # Если пуля не вышла за экран и не попала по платформе или врагу она литит дальше
                else:
                    bullets.pop(bullets.index(bullet))
                    shots.remove(bullet) # Удаляем пулю

            shots.update(bullets)
            shots.draw(screen)

            player.update(left, right, up)
            camera.update(player)

            player.draw(screen)
            for sprite in all_sprites:
                camera.apply(sprite)
            # obstacles.draw(screen)

            # screen.blit(darkness_area, darkness_rect) TODO раскомментить
            screen.set_clip(None)

            color = 'White' if bullets_quantity > 0 else 'Red'
            menu.draw_text(screen, [str(bullets_quantity)], 0, 0, color, size=75, text_coord_2=0)
            menu.draw_text(screen, [str(player.health)], 0, 0, 'Green', size=75, text_coord_2=1105)

            pygame.display.flip()
            clock.tick(60)
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
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for button in buttons:
                            if pygame.Rect.collidepoint(button[0], pygame.mouse.get_pos()):
                                if button[1] == 'continue':
                                    paused = False
                                elif button[1] == 'back to menu':
                                    screen.fill((0, 0, 0))
                                    clear_stuff(screen)
                                    menu.start_screen()
                                    return None
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    paused = not paused
                pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main('level_1')
