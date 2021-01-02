import pygame
import sys
import os

GRAVITY_FORCE = 5
SIZE_X = 1200
SIZE_Y = 720
WINDOW_CAPTION = 'Murky gloom'

entities = pygame.sprite.Group()


def load_image(name, color_key=None):
    # name - название файла с папкой,
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
        self.speed = 10
        self.jump_force = 20

    def update(self, left, right, up):
        if up:
            if self.is_onground:
                self.rect.y -= self.jump_force
        if left:
            self.rect.x -= self.speed
        if right:
            self.rect.x += self.speed
        # if not (left or right):
        #     self.entity.rect.x = 0
        if not self.is_onground:
            self.rect.y += GRAVITY_FORCE

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Platform:
    def __init__(self, size_x, size_y, x, y, color='#887C5D'):
        self.size_x = size_x
        self.size_y = size_y
        self.color = color

        self.x = x
        self.y = y

        self.surface = pygame.Surface((self.size_x, self.size_y))
        self.surface.fill(pygame.Color(self.color))
        self.rect = pygame.Rect(x, y, self.size_x, self.size_y)

    def draw(self, screen):
        screen.blit(self.color, (self.rect.x, self.rect.y))


def main():
    pygame.init()
    pygame.display.set_caption(WINDOW_CAPTION)

    size = SIZE_X, SIZE_Y
    screen = pygame.display.set_mode(size)

    clock = pygame.time.Clock()
    player = Player(50, 50, 100, 100, texture='entities/player 0.png')  # TODO Поменять файл

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
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_RIGHT, pygame.K_d]:
                right = True
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

        screen.fill((0, 0, 0))
        player.update(left, right, up)
        player.draw(screen)

        pygame.display.flip()
        clock.tick(50)
    pygame.quit()


if __name__ == '__main__':
    main()
