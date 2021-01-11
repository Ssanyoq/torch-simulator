import pygame
import sys
import os

GRAVITY_FORCE = 5
SIZE_X = 1200
SIZE_Y = 720
WINDOW_CAPTION = 'Murky gloom'
all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
entities = pygame.sprite.Group()
shots = pygame.sprite.Group()

darkness_radius = 180

darkness_area = pygame.Surface((SIZE_X, SIZE_Y), pygame.SRCALPHA)
darkness_area.fill((0, 0, 0))
pygame.draw.circle(darkness_area, (0, 0, 0, 0), (SIZE_X // 2, SIZE_Y // 2), darkness_radius)
platforms = []


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
                platform = Platform(30, 30, x, y, texture='levels/platform.jpg')
                obstacles.add(platform)
                all_sprites.add(platform)
                platforms.append(platform)
            elif element == "*":
                spike = Spike(30, 30, x, y)
                obstacles.add(spike)
                all_sprites.add(spike)
                platforms.append(spike)
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
        if self.vel_y > 10:
            self.vel_y = 10
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

    def death(self):
        pass


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
        self.x = 0
        self.y = 0

    def apply(self, obj):
        obj.rect.x += self.x
        obj.rect.y += self.y

    def update(self, target):
        self.x = -(target.rect.x + target.rect.w // 2 - SIZE_X // 2)
        self.y = -(target.rect.y + target.rect.h // 2 - SIZE_Y // 2)


def main():
    global platforms
    pygame.init()
    pygame.display.set_caption(WINDOW_CAPTION)

    size = SIZE_X, SIZE_Y
    screen = pygame.display.set_mode(size)

    clock = pygame.time.Clock()
    player = Player(50, 50, 100, 100, texture='entities/arrow.png')  # TODO Поменять файл
    all_sprites.add(player)

    platforms = convert_level('level_1')

    bullets = []
    bullet_direction = 'Right'

    camera = Camera()

    darkness_rect = pygame.Rect((0, 0), (darkness_radius * 2, darkness_radius * 2))
    screen.set_clip(darkness_rect)
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

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                facing = 1 if bullet_direction == 'Right' else -1
                bullet = Bullet(player.rect.x + 25 // 2, player.rect.y + 25 // 2, 5, (100, 255, 0), facing)
                shots.add(bullet)
                bullets.append(bullet)

        screen.fill((255, 255, 255))

        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)

        player.update(left, right, up)
        player.draw(screen)

        for bullet in bullets:
            if SIZE_X > bullet.x > 0 and not pygame.sprite.spritecollideany(bullet, obstacles):
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
        clock.tick(50)
    pygame.quit()


if __name__ == '__main__':
    main()
