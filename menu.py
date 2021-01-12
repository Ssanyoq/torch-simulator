import pygame
import main


def level_screen(screen, font):
    screen.fill((0, 0, 0))

    button_text = ['level 1', 'level 2', 'level 3', 'level 4', 'level 5', 'Quit']  # Название кнопок
    button_coord = 100
    buttons = []

    text_coord = 50

    for i in range(len(button_text)):  # Создание кнопок
        button = pygame.draw.rect(screen, (200, 200, 200), (350, button_coord, 530, 60))
        button_coord += 100
        buttons.append(button)

    for text in button_text:  # Отрисовка текста
        string_rendered = font.render(text, 1, pygame.Color('White'))
        intro_rect = string_rendered.get_rect()
        text_coord += 65
        intro_rect.top = text_coord
        intro_rect.x = 550
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    # Проверка на совпадение координаты мыши с одной из кнопок
                    if pygame.Rect.collidepoint(button, pygame.mouse.get_pos()):
                        # По координате Y мы можем узнать на какую кнопку нажал пользователь
                        # т.е у первой кнопки Y равен 100, у второй 200 и т.д
                        if button.y == 600:
                            running = False
                            start_screen()
                        else:
                            main.main('level_' + str(button.y // 100))
        pygame.display.flip()


def start_screen():
    pygame.init()
    pygame.display.set_caption("menu")
    SIZE = WIDTH, HEIGHT = 1200, 720
    screen = pygame.display.set_mode(SIZE)

    start_button = pygame.draw.rect(screen, (210, 200, 200), (350, 230, 530, 60))
    level_button = pygame.draw.rect(screen, (200, 200, 200), (350, 320, 530, 60))
    exit_button = pygame.draw.rect(screen, (200, 170, 170), (350, 410, 530, 60))
    off_button = pygame.draw.rect(screen, (150, 170, 170), (1110, 690, 75, 25))
    # TODO сделать словарем

    text_coord = 190
    font = pygame.font.Font(None, 50)
    intro_text = ["Start", "Levels", "Exit"]

    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('White'))
        intro_rect = string_rendered.get_rect()
        text_coord += 55
        intro_rect.top = text_coord
        intro_rect.x = 550
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    screen.blit(pygame.font.Font(None, 25).render('Music', 1, pygame.Color('White')), (1125, 695, 75, 25))

    radio = pygame.mixer.Sound('misc/music/music_in_menu.mp3')
    radio.play()
    check_radio = True
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pos()[0] >= 350 and pygame.mouse.get_pos()[1] >= 230:
                    if pygame.mouse.get_pos()[0] <= 880 and pygame.mouse.get_pos()[1] <= 280:
                        radio.stop()
                        main.main('level_1')  # Загружаем не пройденный уровень

                if pygame.mouse.get_pos()[0] >= 350 and pygame.mouse.get_pos()[1] >= 320:
                    if pygame.mouse.get_pos()[0] <= 880 and pygame.mouse.get_pos()[1] <= 380:
                        level_screen(screen, font)  # Отрисовываем меню с уровнями

                if pygame.mouse.get_pos()[0] >= 350 and pygame.mouse.get_pos()[1] >= 410:
                    if pygame.mouse.get_pos()[0] <= 880 and pygame.mouse.get_pos()[1] <= 470:
                        running = False

                if pygame.mouse.get_pos()[0] >= 1110 and pygame.mouse.get_pos()[1] >= 690:
                    if pygame.mouse.get_pos()[0] <= 1185 and pygame.mouse.get_pos()[1] <= 715:
                        if check_radio:
                            radio.stop()
                            check_radio = False
                        else:
                            radio = pygame.mixer.Sound('misc/music.mp3')
                            radio.play()
                            check_radio = True
                            # TODO доделать радио
        pygame.display.flip()
        clock.tick(100)


if __name__ == '__main__':
    start_screen()