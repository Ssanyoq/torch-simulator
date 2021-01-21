import os
import pygame
import main

radio = None
pygame.init()


def draw_text(screen, text, pos_x, pos_y, color="White", font_size=50):
    """
    Рисует текст по заданным параметрам
    :param screen: полотно для рисования
    :param text: текст для рисования
    :param pos_x: x левого верхнего угла текста
    :param pos_y: y левого верхнего угла текста
    :param color: необязательный параметр, текст будет цвета color
    :param font_size: необязательный параметр, текст будет размера font_size
    :return: None
    """
    font = pygame.font.Font(None, font_size)
    string_rendered = font.render(text, 1, pygame.Color(color))
    intro_rect = string_rendered.get_rect()
    intro_rect.y = pos_y
    intro_rect.x = pos_x
    screen.blit(string_rendered, intro_rect)


def draw_texts(screen, text, pos_x, pos_y, text_delta=0, color='White', font_size=50):
    """
    Для цикличного отрисовывания как в draw_text, не особо универсально
    :param screen: полотно для рисования
    :param text: список из текстов для рисования
    :param pos_y: y первого текста
    :param pos_x: x всех текстов
    :param text_delta: какое расстояние должно быть между текстами
    :param color: необязательный параметр, текст будет цвета color
    :param font_size: необязательный параметр, текст будет размера font_size
    :return: None
    """
    for line in text:  # Отрисовка текст

        draw_text(screen, line, pos_x, pos_y, color=color, font_size=font_size)
        pos_y += text_delta


def get_levels_names(folder='misc/levels'):
    """
    Возвращает список с именами всех .txt файлов из
    папки folder, например, ['level1','example2','sadpjpajsdl']
    folder - относительный путь папки от данного файла
    """
    level_names = []
    for (dirpath, dirnames, filenames) in os.walk(folder):
        for filename in filenames:
            if filename.split('.')[1] == 'txt':
                # Проверка на .txt
                level_names.append(filename.split('.')[0])
    return level_names


def level_screen(menu_screen):
    menu_screen.fill((0, 0, 0))

    # Создание кнопок
    button_pos_y = 50
    buttons = []

    for i in range(5):
        button = pygame.draw.rect(menu_screen, (200, 200, 200), (350, button_pos_y, 530, 60))
        button_pos_y += 100
        buttons.append(button)
    button = pygame.draw.rect(menu_screen, (200, 10, 10), (350, button_pos_y, 530, 60))
    buttons.append(button)
    button_pos_y += 100
    left_button = pygame.draw.rect(menu_screen, (200, 200, 200), (350, button_pos_y, 245, 40))
    right_button = pygame.draw.rect(menu_screen, (200, 200, 200),
                                    (350 + 265 + 20, button_pos_y, 245, 40))

    # Создание надписей на кнопках
    all_levels = get_levels_names('misc/levels')
    current_page = 0
    buttons_names = []
    # Название кнопок
    for i in range(5):
        tmp_name = all_levels[i].replace('_', ' ').capitalize()
        buttons_names.append(tmp_name)
    text_pos_y = 65  # Начальный button_pos_y + 1/4 размера кнопки, чтобы ровно посередине
    text_delta = 100

    draw_texts(menu_screen, buttons_names, 550, text_pos_y, text_delta)
    draw_text(menu_screen, "Quit", 575, text_pos_y + text_delta * 5)  # x на глазок

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    # Проверка на совпадение координаты мыши с одной из кнопок
                    if pygame.Rect.collidepoint(button, pygame.mouse.get_pos()):
                        # По координате Y мы можем узнать на какую кнопку нажал пользователь
                        # т.е у первой кнопки Y равен 100, у второй 200 и т.д
                        if button.y == 600:
                            running = False
                            start_screen()
                            return None
                        else:
                            main.main('level_' + str(button.y // 100))
                            return None
        pygame.display.flip()


def start_screen():
    pygame.init()
    pygame.display.set_caption("Murky Gloom")
    SIZE = WIDTH, HEIGHT = 1200, 720
    screen = pygame.display.set_mode(SIZE)

    start_button = pygame.draw.rect(screen, (210, 200, 200), (350, 230, 530, 60))
    levels_button = pygame.draw.rect(screen, (200, 200, 200), (350, 320, 530, 60))
    exit_button = pygame.draw.rect(screen, (200, 170, 170), (350, 410, 530, 60))
    radio_button = pygame.draw.rect(screen, (150, 170, 170), (1110, 690, 75, 25))
    # Присваивание только для того, чтобы было понятно, какая кнопка к чему

    intro_text = ["Start", "Levels", "Exit"]
    text_pos_y = 245  # start_button.y + 60 // 4
    text_delta = 90

    draw_texts(screen, intro_text, 550, text_pos_y, text_delta)

    screen.blit(pygame.font.Font(None, 25).render('Music', True, pygame.Color('White')),
                (1125, 695, 75, 25))

    radio = pygame.mixer.Sound('misc/sounds/music_in_menu.mp3')
    radio.play()
    check_radio = True
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pos()[0] >= 350 and pygame.mouse.get_pos()[1] >= 230:
                    if pygame.mouse.get_pos()[0] <= 880 and pygame.mouse.get_pos()[1] <= 280:
                        radio.stop()
                        main.main('level_1')  # Загружаем непройденный уровень
                        return None

                if pygame.mouse.get_pos()[0] >= 350 and pygame.mouse.get_pos()[1] >= 320:
                    if pygame.mouse.get_pos()[0] <= 880 and pygame.mouse.get_pos()[1] <= 380:
                        radio.stop()
                        level_screen(screen)  # Отрисовываем меню с уровнями
                        return None

                if pygame.mouse.get_pos()[0] >= 350 and pygame.mouse.get_pos()[1] >= 410:
                    if pygame.mouse.get_pos()[0] <= 880 and pygame.mouse.get_pos()[1] <= 470:
                        running = False

                if pygame.mouse.get_pos()[0] >= 1110 and pygame.mouse.get_pos()[1] >= 690:
                    if pygame.mouse.get_pos()[0] <= 1185 and pygame.mouse.get_pos()[1] <= 715:
                        if check_radio:
                            radio.stop()
                            check_radio = False
                        else:
                            radio = pygame.mixer.Sound('misc/sounds/music_in_menu.mp3')
                            radio.play()
                            check_radio = True
                            # TODO доделать радио
        pygame.display.flip()
        clock.tick(100)
    radio.stop()


if __name__ == '__main__':
    start_screen()
