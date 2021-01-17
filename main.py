import pygame
import sys
import os
import menu

SIZE = SIZE_X, SIZE_Y = 1200, 720
WINDOW_CAPTION = 'Murky gloom'
GRAVITY_FORCE = 5

all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
entities = pygame.sprite.Group()
enemies = pygame.sprite.Group()
shots = pygame.sprite.Group()

darkness_radius = 180
darkness_area = pygame.Surface((SIZE_X, SIZE_Y), pygame.SRCALPHA)
darkness_area.fill((0, 0, 0))
pygame.draw.circle(darkness_area, (0, 0, 0, 0), (SIZE_X // 2, SIZE_Y // 2), darkness_radius)


def convert_level(level, path='misc/levels'):
    # Функция открывает текстовый файл, в котором содержатся необходимые игровые элементы ->
    # после чего создает список этих элементов(платформы, монстры и т.д).
    with open(f"""{path}/{level}.txt""", encoding='utf-8') as f:
        data = f.readlines()

    level = [i.rstrip() for i in data]
    platforms = list()
    player_x, player_y = 0, 0

    x = y = 0
    count = 0
    for row in level:
        for element in row:
            if element == "-":
                platform = Platform(30, 30, x, y, texture='textures/platform.jpeg')
                obstacles.add(platform)
                all_sprites.add(platform)
                platforms.append(platform)
            elif element == "*":
                spike = Spike(30, 30, x, y, texture='textures/spike.png')
                obstacles.add(spike)
                all_sprites.add(spike)
                platforms.append(spike)
            elif element == 'E':
                a = [i for i in level[count + 1]]
                max_length_right = a[x // 30:].index(' ') * 30
                max_length_left = a[:x // 30][::-1].index(' ') * 30
                if not max_length_right == max_length_left == 0:
                    # Если враг не на платформе, то мы его не создаем
                    enemy = Enemy(30, 30, x, y, max_length_right, max_length_left,
                                  texture='textures/platform.jpeg')
                    enemies.add(enemy)
                    all_sprites.add(enemy)
            elif element == 'S':
                player_x, player_y = x, y
            x += 30
        count += 1
        y += 30
        x = 0

    return platforms, player_x, player_y


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
        self.is_on_ground = True
        self.moving_velocity = 5

        self.image = load_image(texture)
        self.image = self.image
        self.rect = self.image.get_rect()
        self.rect = pygame.Rect(self.x, self.y, self.size_x, self.size_y)

        if health is None:
            self.is_immortal = True


class Player(Entity):
    def __init__(self, size_x, size_y, x, y, texture=None, is_collide=True, health=None):
        super().__init__(size_x, size_y, x, y, texture=texture, is_collide=True, health=100)
        self.jump_force = 15
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

        for enemy in enemies:
            if pygame.sprite.collide_rect(self, enemy):
                self.health -= 25  # TODO сделать удары

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
    def __init__(self, size_x, size_y, x, y, color=(255, 0, 0), texture=None):
        pygame.sprite.Sprite.__init__(self)
        self.size_x, self.size_y = size_x, size_y
        self.x, self.y = x, y
        self.color = color

        self.image = load_image(texture)
        self.image = self.image
        self.rect = self.image.get_rect()
        self.rect = pygame.Rect(self.x, self.y, self.size_x, self.size_y)

    def draw(self, screen):
        screen.blit(self.color, (self.rect.x, self.rect.y))


class Spike(Platform):
    def __init__(self, size_x, size_y, x, y, color=(0, 255, 0), texture=None):
        Platform.__init__(self, size_x, size_y, x, y, color, texture)
        pygame.sprite.Sprite.__init__(self)


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


def main(level):
    global platforms

    pygame.display.set_caption(WINDOW_CAPTION)
    screen = pygame.display.set_mode(SIZE)

    platforms, player_x, player_y = convert_level(level)  # Level передается через level_screen и start_screen

    player = Player(50, 50, player_x, player_y, texture='entities/arrow.png')  # TODO Поменять файл
    all_sprites.add(player)

    bullets = []
    facing = 1  # Направление пуль, изначально пули летят вправо

    camera = Camera()  # Создаем камеру

    darkness_rect = pygame.Rect((0, 0), (darkness_radius * 2, darkness_radius * 2))
    screen.set_clip(darkness_rect)
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
                if not right:
                    facing = -1
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_RIGHT, pygame.K_d]:
                right = True
                if not left:
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

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and not paused:
                bullet = Bullet(player.rect.x + 25 // 2, player.rect.y + 25 // 2,
                                5, (100, 255, 0), facing)
                shots.add(bullet)
                bullets.append(bullet)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = not paused

        if not paused:  # Если игра не на паузе отрисовываем главную сцену, иначе меню паузы
            screen.fill((255, 255, 255))

            camera.update(player)
            for sprite in all_sprites:
                camera.apply(sprite)

            player.update(left, right, up)
            player.draw(screen)

            enemies.update()
            enemies.draw(screen)

            for bullet in bullets:
                if SIZE_X > bullet.x > 0 and not pygame.sprite.spritecollideany(bullet, obstacles)\
                        and not pygame.sprite.spritecollideany(bullet, enemies):
                    bullet.rect.x += bullet.speed
                else:
                    bullets.pop(bullets.index(bullet))
                    shots.remove(bullet)

            shots.update(bullets)
            shots.draw(screen)

            obstacles.draw(screen)

            screen.blit(darkness_area, darkness_rect)
            screen.set_clip(None)

            pygame.display.flip()
            clock.tick(60)
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
