import pygame
import main

pygame.init()
pygame.display.set_caption("menu")
SIZE = WIDTH, HEIGHT = 1200, 720
screen = pygame.display.set_mode(SIZE)
screen2 = pygame.Surface(screen.get_size())
clock = pygame.time.Clock()

text_coord = 0
font = pygame.font.Font(None, 100)

circle_radius = 10
circle_color = (255, 255, 255)
circles = []
directions = []

radio = pygame.mixer.Sound('misc/music/music_in_menu.mp3')
radio.play()
turned_on = True


def startGame():
    main.main()


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEMOTION:
            circles.append(list(event.pos))
            directions.append([-1, -1])

        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pos()[0] >= 350 and pygame.mouse.get_pos()[1] >= 250:
                if pygame.mouse.get_pos()[0] <= 880 and pygame.mouse.get_pos()[1] <= 310:
                    radio.stop()
                    startGame()

            if pygame.mouse.get_pos()[0] >= 350 and pygame.mouse.get_pos()[1] >= 380:
                if pygame.mouse.get_pos()[0] <= 880 and pygame.mouse.get_pos()[1] <= 440:
                    running = False

            if pygame.mouse.get_pos()[0] >= 1110 and pygame.mouse.get_pos()[1] >= 690:
                if pygame.mouse.get_pos()[0] <= 1185 and pygame.mouse.get_pos()[1] <= 715:
                    if turned_on:
                        radio.stop()
                        turned_on = False
                    else:
                        radio = pygame.mixer.Sound('misc/music/music_in_menu.mp3')
                        radio.play()
                        turned_on = True

        screen2.fill((0, 0, 0))

        for i in range(len(circles)):
            for coord in (0, 1):
                if circles[i][coord] >= SIZE[coord] - circle_radius or \
                        circles[i][coord] <= circle_radius:
                    directions[i][coord] *= -1
                circles[i][coord] += directions[i][coord]
            pygame.draw.circle(screen2, circle_color, circles[i], circle_radius, 0)

        screen.blit(screen2, (0, 0))

        string_rendered = font.render('Murky gloom', 0, pygame.Color(255, 255, 240))
        intro_rect = string_rendered.get_rect()
        intro_rect.top = text_coord
        text_coord = intro_rect.height
        screen.blit(string_rendered, intro_rect)

        start_button = pygame.draw.rect(screen, (210, 200, 200), (350, 250, 530, 60))
        quit_button = pygame.draw.rect(screen, (180, 150, 150), (350, 380, 530, 60))
        off_button = pygame.draw.rect(screen, (150, 170, 170), (1110, 690, 75, 25))

        pygame.display.flip()
        clock.tick(1000)
