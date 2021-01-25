import math
import random
import pygame
import sys
import os
import menu

GRAVITY_FORCE = 20
SIZE = SIZE_X, SIZE_Y = 1200, 720
WINDOW_CAPTION = 'Murky gloom'
FPS = 120

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

obstacles = pygame.sprite.Group()
entities = pygame.sprite.Group()
enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
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
                spike = Spike(30, 30, x, y, texture='textures/spike.png')
                obstacles.add(spike)
                all_sprites.add(spike)
                platforms.append(spike)
            elif element == 'E':
                a = [i for i in level[count + 1]]
                max_length_right = a[x // 30:].index(' ') * 30
                max_length_left = a[:x // 30][::-1].index(' ') * 30
                enemy = Enemy(30, 30, x, y, max_length_right, max_length_left,
                              texture='textures/platform.jpeg')
                enemies.add(enemy)
                all_sprites.add(enemy)
            elif element == 'S':
                player_x, player_y = x, y
                air = Air(30, 30, x, y, color=AIR_COLOR)
                decoratives.append(air)
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


def change_color(color, center_x, center_y):
    # for light in lightsources: надо сделать, когда будут факелы
    #    pass
    player_x = player.rect.centerx
    player_y = player.rect.centery
    # Чтобы расстояние было не от левого верхнего

    distance_from_player = ((center_x - player_x) ** 2 + (
            center_y - player_y) ** 2) ** 0.5
    # Просто нахождение расстояния между двумя точками
    distance_from_player = math.ceil(distance_from_player)  # чтобы int чтобы красиво

    is_changed = False
    new_color = None
    for i in BRIGHTNESS_INFO.keys():
        if distance_from_player <= BRIGHTNESS_INFO[i][0]:
            delta = BRIGHTNESS_INFO[i][1]
            new_color = [color[0] - delta, color[1] - delta, color[2] - delta]
            new_color = [i if i >= 0 else 0 for i in new_color]
            is_changed = True
            break

    if not is_changed:
        new_color = (0, 0, 0)

    return new_color


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.image = self.frames[0]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, x, y, frame):
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
    def __init__(self, size_x, size_y, x, y, texture=None, is_collide=True, health=None):
        super().__init__(size_x, size_y, x, y, texture=texture, is_collide=True, health=100)
        self.jump_force = 20
        self.vel_y = GRAVITY_FORCE
        self.facing = 1
        # Способ сделать красивые падения

        self.in_air = False
        self.delta_x, self.delta_y = 0, 0

        self.frame = 0

        self.idle_right = AnimatedSprite(load_image('entities/player/idle.png'), 4, 1, 50, 50)
        self.jump_r = AnimatedSprite(load_image("entities/player/jump.png"), 6, 1, 50, 50)
        self.run_r = AnimatedSprite(load_image("entities/player/run.png"), 6, 1, 50, 50)

        self.idle_left = AnimatedSprite(
            pygame.transform.flip(load_image('entities/player/idle.png'), True, False), 4, 1,
            50, 50)
        self.jump_l = AnimatedSprite(
            pygame.transform.flip(load_image("entities/player/jump.png"), True, False), 6, 1,
            50, 50)
        self.run_l = AnimatedSprite(
            pygame.transform.flip(load_image("entities/player/run.png"), True, False), 6, 1,
            50, 50)

    def update(self, left, right, up):
        self.delta_x = 0  # Общее изменение
        self.delta_y = 0  # за всю работу функции

        self.frame = self.frame % 30

        if up:
            if not self.in_air:
                self.vel_y = -self.jump_force
                self.in_air = True
            if self.facing == 1:
                self.jump_r.update(self.rect.x, self.rect.y, self.frame // 5)
            else:
                self.jump_l.update(self.rect.x, self.rect.y, self.frame // 5)

        if right:
            self.facing = 1
            self.delta_x = self.moving_velocity
            if self.vel_y < 0:
                self.jump_r.update(self.rect.x, self.rect.y, self.frame // 5)
            elif self.vel_y == 0:
                self.run_r.update(self.rect.x, self.rect.y, self.frame // 5)

        if left:
            self.facing -= 1
            self.delta_x = -self.moving_velocity
            if self.vel_y < 0:
                self.jump_l.update(self.rect.x, self.rect.y, self.frame // 5)
            elif self.vel_y == 0:
                self.run_l.update(self.rect.x, self.rect.y, self.frame // 5)

        if not (left or right or up) and self.vel_y == 0:  # Если стоим
            if self.facing == 1:
                self.idle_right.update(self.rect.x, self.rect.y, self.frame // 5)
            else:
                self.idle_left.update(self.rect.x, self.rect.y, self.frame // 4)

        if self.vel_y > 0:  # Если падаем
            if self.facing == 1:
                self.jump_r.update(self.rect.x, self.rect.y, 4)
            else:
                self.jump_l.update(self.rect.x, self.rect.y, 4)
        self.frame += 1

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

        if self.is_onground:
            self.in_air = False
        self.is_onground = False

        self.rect.x += self.delta_x
        self.rect.y += self.delta_y
        pygame.draw.rect(screen, (0, 0, 200), self.rect, 3)

    def get_coord(self):
        return self.rect.centerx, self.rect.centery


class Enemy(Entity):
    def __init__(self, size_x, size_y, x, y, max_length_right, max_length_left,
                 texture=None, is_collide=True, health=None):
        super().__init__(size_x, size_y, x, y, texture=texture, is_collide=True, health=100)
        self.max_length_right = max_length_right
        self.max_length_left = max_length_left
        self.max_length_vel = max_length_right

        if self.max_length_vel - self.size_x == 0:
            self.facing = -1
        else:
            self.facing = 1

    def update(self):
        self.rect.x += (self.moving_velocity - 3) * self.facing
        self.max_length_vel -= (self.moving_velocity - 3) * self.facing

        if self.max_length_vel - self.size_x == 0 and self.facing == 1:
            self.facing = -1

        if self.max_length_vel > self.max_length_right + self.max_length_left and self.facing == -1:
            self.facing = 1

        for platform in platforms:
            if pygame.sprite.collide_rect(self, platform) and self != platform:
                self.facing = -1 if self.facing == 1 else 1

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
        tmp_color = change_color(self.color, self.rect.centerx, self.rect.centery)

        pygame.draw.rect(screen, tmp_color, self.rect)
        for pebble in self.pebbles:
            tmp_pebble_color = change_color(self.pebble_color, pebble.centerx, pebble.centery)
            tmp_rect = pygame.Rect(pebble.x + self.rect.x, pebble.y + self.rect.y, pebble.width,
                                   pebble.height)
            pygame.draw.rect(screen, tmp_pebble_color, tmp_rect)


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
        self.rect = pygame.Rect(self.x, self.y, 2 * radius, 2 * radius)


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0

    def apply(self, obj):
        obj.rect.x += self.x
        obj.rect.y += self.y

    def update(self, target):
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

    def __init__(self, size_x, size_y, x, y, color=(255, 255, 255)):
        super().__init__(all_sprites)
        self.size_x, self.size_y = size_x, size_y
        self.x, self.y = x, y
        self.color = color
        self.rect = pygame.Rect(self.x, self.y, self.size_x, self.size_y)

    def draw(self, screen):
        tmp_color = change_color(self.color, self.rect.centerx, self.rect.centery)
        pygame.draw.rect(screen, tmp_color, self.rect)


def main(level):
    global platforms, player, screen
    pygame.init()

    pygame.display.set_caption(WINDOW_CAPTION)
    screen = pygame.display.set_mode(SIZE)

    platforms, decoratives, player_x, player_y = convert_level(level)
    player = Player(20, 50, player_x, player_y)
    all_sprites.add(player)

    bullets = []
    facing = 1  # Направление пуль, изначально пули летят вправо

    camera = Camera()  # Создаем камеру

    # darkness_rect = pygame.Rect((0, 0), (darkness_radius * 2, darkness_radius * 2),)
    # screen.set_clip(darkness_rect)
    # Поверх экрана происходит отрисовка прямоугольника с вырезанным по середине кругом (Темнота)

    left = False
    right = False
    up = False

    clock = pygame.time.Clock()

    paused = False
    running = True
    while running:
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

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not paused:
                bullet = Bullet(player.get_coord()[0], player.get_coord()[1],
                                5, (100, 255, 0), facing)
                shots.add(bullet)
                bullets.append(bullet)

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

            for bullet in bullets:
                if SIZE_X > bullet.x > 0 and not pygame.sprite.spritecollideany(bullet, obstacles):
                    bullet.rect.x += bullet.speed
                else:
                    bullets.pop(bullets.index(bullet))
                    shots.remove(bullet)

            shots.draw(screen)

            player.update(left, right, up)
            camera.update(player)

            for sprite in all_sprites:
                camera.apply(sprite)
            # obstacles.draw(screen)

            # screen.blit(darkness_area, darkness_rect)
            screen.set_clip(None)

            pygame.display.flip()
            clock.tick(FPS)
        else:  # TODO починить отрисовку
            button_coord = 300
            buttons = []

            for i in range(2):
                button = pygame.draw.rect(screen, (210, 210, 210), (350, button_coord, 530, 60))
                button_coord += 100
                buttons.append(button)

            intro_text = ["Continue", "Quit"]
            text_coord = 255
            text_delta = 60

            menu.draw_text(screen, intro_text, text_coord, text_delta)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()  # Поправить ошибку
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for button in buttons:
                        if pygame.Rect.collidepoint(button, pygame.mouse.get_pos()):
                            if button.y == 300:
                                paused = False
                            else:
                                screen.fill((0, 0, 0))
                                paused = False
                                running = False
                                menu.start_screen()
                pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main('level_1')
