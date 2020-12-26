import pygame
import main

pygame.init()
size = width, height = 720, 480
screen = pygame.display.set_mode((720, 480))
screen2 = pygame.Surface(screen.get_size())

clock = pygame.time.Clock()

pygame.display.set_caption("menu")
running = True

circle_radius = 10
circle_color = (255, 255, 255)
circles = []
directions = []

radio = pygame.mixer.Sound('misc/music.mp3')
radio.play()
turned_on = True


pygame.display.flip()


def startGame():
    main.main()


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEMOTION:
            circles.append(list(event.pos))
            directions.append([-1, -1])

        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pos()[0] >= 640 and pygame.mouse.get_pos()[1] >= 450:
                if pygame.mouse.get_pos()[0] <= 690 and pygame.mouse.get_pos()[1] <= 470:
                    if turned_on:
                        radio.stop()
                        turned_on = False
                    else:
                        radio = pygame.mixer.Sound('misc/music.mp3')
                        radio.play()
                        turned_on = True

            if pygame.mouse.get_pos()[0] >= 190 and pygame.mouse.get_pos()[1] >= 250:
                if pygame.mouse.get_pos()[0] <= 510 and pygame.mouse.get_pos()[1] <= 360:
                    running = False

            if pygame.mouse.get_pos()[0] >= 190 and pygame.mouse.get_pos()[1] >= 160:
                if pygame.mouse.get_pos()[0] <= 510 and pygame.mouse.get_pos()[1] <= 360:
                    radio.stop()
                    startGame()

        screen2.fill((0, 0, 0))

        for i in range(len(circles)):
            for coord in (0, 1):
                if circles[i][coord] >= size[coord] - circle_radius or \
                        circles[i][coord] <= circle_radius:
                    directions[i][coord] *= -1
                circles[i][coord] += directions[i][coord]
            pygame.draw.circle(screen2, circle_color, circles[i], circle_radius, 0)
        screen.blit(screen2, (0, 0))

        quit_button = pygame.draw.rect(screen, (180, 150, 150), (190, 250, 320, 40))
        start_button = pygame.draw.rect(screen, (210, 200, 200), (190, 160, 320, 40))
        off_button = pygame.draw.rect(screen, (150, 170, 170), (640, 450, 50, 20))

        pygame.display.flip()
        clock.tick(1000)
