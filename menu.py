import pygame
import main

pygame.init()


def draw_text(screen, text, text_coord, text_delta, color='White', size=50, text_coord_2=550):
    font = pygame.font.Font(None, size)

    for line in text:  # Отрисовка текста
        string_rendered = font.render(line, 1, pygame.Color(color))
        intro_rect = string_rendered.get_rect()
        text_coord += text_delta
        intro_rect.top = text_coord
        intro_rect.x = text_coord_2
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)


def end_screen(screen, victory, level):
    screen.fill((0, 0, 0))

    button_coord = 400
    buttons = []

    for i in range(2):  # Создание кнопок
        button = pygame.draw.rect(screen, (200, 200, 225), (350, button_coord, 530, 60))
        button_coord += 100
        buttons.append(button)

    text_coord = 350
    text_delta = 65

    if victory:
        draw_text(screen, ['You win'], 100, 0, color='Green', size=200, text_coord_2=350)
        button_text = ['Continue', 'Quit']
    else:
        draw_text(screen, ['You lose'], 100, 0, color='Red', size=200, text_coord_2=325)
        button_text = ['Restart', 'Quit']

    draw_text(screen, button_text, text_coord, text_delta)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if pygame.Rect.collidepoint(button, pygame.mouse.get_pos()):
                        if button.y == 400 and victory:
                            running = False
                            pass  # Загружаем следующий уровень
                        else:
                            running = False
                            pass  # Перезагружаем уровень
                        if button.y == 500:
                            running = False
                            start_screen()
        pygame.display.flip()


def level_screen(menu_screen):
    menu_screen.fill((0, 0, 0))

    button_coord = 100
    buttons = []

    for i in range(6):  # Создание кнопок
        button = pygame.draw.rect(menu_screen, (200, 200, 200), (350, button_coord, 530, 60))
        button_coord += 100
        buttons.append(button)

    button_text = ['level 1', 'level 2', 'level 3', 'level 4', 'level 5', 'Quit']  # Название кнопок
    text_coord = 50
    text_delta = 65

    draw_text(menu_screen, button_text, text_coord, text_delta)

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
                            running = False
                            # main.main('level_' + str(button.y // 100))
        pygame.display.flip()


def start_screen():
    pygame.init()
    pygame.display.set_caption("menu")
    SIZE = WIDTH, HEIGHT = 1200, 720
    screen = pygame.display.set_mode(SIZE)

    pygame.draw.rect(screen, (210, 200, 200), (350, 230, 530, 60))
    pygame.draw.rect(screen, (200, 200, 200), (350, 320, 530, 60))
    pygame.draw.rect(screen, (200, 170, 170), (350, 410, 530, 60))
    pygame.draw.rect(screen, (150, 170, 170), (1110, 690, 75, 25))

    intro_text = ["Start", "Levels", "Exit"]
    text_coord = 190
    text_delta = 55

    draw_text(screen, intro_text, text_coord, text_delta)

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
                        running = False
                        # main.main('level_1')  # Загружаем не пройденный уровень

                if pygame.mouse.get_pos()[0] >= 350 and pygame.mouse.get_pos()[1] >= 320:
                    if pygame.mouse.get_pos()[0] <= 880 and pygame.mouse.get_pos()[1] <= 380:
                        running = False
                        level_screen(screen)  # Отрисовываем меню с уровнями

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
    # end_screen(screen, True, 'level_1')
