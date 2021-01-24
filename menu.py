import math
import os
import pygame
import main

radio = None
pygame.init()


def draw_text(screen, text, pos_x, pos_y, color="White", font_size=50):
    """
    Рисует текст по заданным параметрам,
    если None, то ничего не рисует
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


def get_current_levels(all_levels, page):
    """
    :param all_levels: список с названиями всех уровней
    :param page: номер страницы, нумерация с 0

    :return: картеж с 2-мя списками:
    первый список - названия кнопок,
    второй - названия самих файлов с уровнями
    Названия кнопок - это просто названия файлов,
    начинающиеся с заглавной буквы и
    все '_' заменены на ' '
    Также название урезано до 20 символов
    Если page больше, чем
    math.ceil(len(all_levels) / 5), то
    просто вернет ([],[])
    (прикольный смайлик кстати)
    """
    current_levels = all_levels[page * 5:(page + 1) * 5]
    current_namings = []
    for name in current_levels:
        new_name = name.replace("_", " ").capitalize()
        if len(new_name) > 20:
            new_name = new_name[:20] + '...'
        current_namings.append(new_name)
    return current_levels, current_namings


def level_screen(menu_screen):
    menu_screen.fill((0, 0, 0))

    # Создание кнопок
    button_pos_y = 50
    buttons = []
    # Список вида [[rect кнопки, файл или функция, которой соответствует эта кнопка]]
    # Вернется в меню, если было нажатие на кнопку с индексом 5
    # Тут нету кнопок вправо и влево (они другого размера)

    # Подготовка надписей на кнопках с уровнями
    all_levels = get_levels_names('misc/levels')
    current_levels, buttons_names = get_current_levels(all_levels, 0)
    current_page = 0

    text_pos_y = 65
    # Начальный button_pos_y + 1/4 размера кнопки, чтобы ровно посередине
    text_delta = 100

    # Рисование кнопок
    for i in range(5):
        button_color = (0, 0, 0) if len(buttons_names) - 1 < i else (200, 200, 200)
        button = pygame.draw.rect(menu_screen, button_color, (350, button_pos_y, 530, 60))
        button_pos_y += 100
        if len(current_levels) - 1 < i:
            # Значит на странице должно быть меньше 5 кнопок
            buttons.append([button, None])
        else:
            buttons.append([button, current_levels[i]])

    button = pygame.draw.rect(menu_screen, (200, 10, 10), (350, button_pos_y, 530, 60))
    buttons.append([button, None])
    button_pos_y += 100
    left_button = pygame.draw.rect(menu_screen, (200, 200, 200), (350, button_pos_y, 245, 40))
    right_button = pygame.draw.rect(menu_screen, (200, 200, 200),
                                    (350 + 265 + 20, button_pos_y, 245, 40))

    # Отрисовка текста
    draw_texts(menu_screen, buttons_names, 355, text_pos_y, text_delta)
    draw_text(menu_screen, "Back to menu", 500, text_pos_y + text_delta * 5)  # x на глазок
    draw_text(menu_screen, "<", 472, text_pos_y + text_delta * 6 - 15)
    draw_text(menu_screen, ">", 757, text_pos_y + text_delta * 6 - 15)

    change_buttons = False
    # Переменная чтобы красивее было

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, button in enumerate(buttons):
                        # Проверка на совпадение координаты мыши с одной из кнопок
                        if pygame.Rect.collidepoint(button[0], pygame.mouse.get_pos()):
                            if i == 5:
                                start_screen()
                                return None
                            elif button[1] is None:
                                continue
                            else:
                                main.main(button[1])
                                return None

                    if pygame.Rect.collidepoint(left_button, pygame.mouse.get_pos()):
                        current_page -= 1 if current_page != 0 else 0
                        change_buttons = True
                    if pygame.Rect.collidepoint(right_button, pygame.mouse.get_pos()):
                        if current_page < math.ceil(len(all_levels) / 5) - 1:
                            current_page += 1
                            change_buttons = True
            if change_buttons:
                change_buttons = False
                current_levels, buttons_names = get_current_levels(all_levels, current_page)
                for i in range(5):
                    if len(buttons_names) - 1 < i:
                        buttons[i][1] = None
                    else:
                        buttons[i][1] = buttons_names[i]
                button_pos_y = 50

                # Отрисовка новых кнопок и названий
                for i in range(5):
                    if len(buttons_names) - 1 < i:
                        color = (0, 0, 0)
                    else:
                        color = (200, 200, 200)
                    pygame.draw.rect(menu_screen, color,
                                     (350, button_pos_y, 530, 60))
                    button_pos_y += 100

                draw_texts(menu_screen, buttons_names, 355, text_pos_y, text_delta)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    start_screen()
                    return None
        pygame.display.flip()


def ending_screen(screen, won=True):
    """
    Менюшка, надписи на которой зависят от того,
    победил игрок или нет
    :param screen: экран
    :param won: победил или нет
    :return: None
    """
    pygame.draw.rect(screen, (152, 130, 199), (300, 180, 600, 360))
    if won:
        bold_text = 'You won!'
        small_text = " " * 11 + '+ 5 coins'
    else:
        bold_text = 'You lost'
        small_text = 'Better luck next time'
    draw_text(screen, bold_text, 490, 250, font_size=75)
    draw_text(screen, small_text, 430, 425)
    quit_button = pygame.draw.rect(screen, (200, 0, 0), (825, 180, 75, 75))
    draw_text(screen, 'X', 845, 195, font_size=75)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if quit_button.collidepoint(pygame.mouse.get_pos()):
                    start_screen()
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
    buttons = [
        [pygame.rect.Rect(350, 230, 530, 60), (210, 200, 200), 'Start'],
        [pygame.rect.Rect(350, 320, 530, 60), (200, 200, 200), 'Levels'],
        [pygame.rect.Rect(350, 410, 530, 60), (200, 170, 170), 'Exit'],
        [pygame.rect.Rect(1110, 690, 75, 25), (150, 170, 170), 'Music'],
    ]
    # Список формата [[rect кнопки, RGB цвет, надпись на кнопке]]
    # Надписи будут сделаны белым цветом

    for i, button in enumerate(buttons):
        pygame.draw.rect(screen, button[1], button[0])
        if i == len(buttons) - 1:
            # Значит это кнопка радио
            draw_text(screen, button[2], 1125, 695, font_size=25)
        else:
            draw_text(screen, button[2], 550, 245 + 90 * i)
            # 245 = button[0][0].y + button[0][0].height // 4

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
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    if pygame.Rect.collidepoint(button[0], pygame.mouse.get_pos()):
                        if button[2] == "Start" or button[2] == "Levels":
                            # TODO сделать что-то со start и levels
                            radio.stop()
                            level_screen(screen)  # Отрисовываем меню с уровнями
                            return None

                        if button[2] == "Exit":
                            running = False
                            break

                        if button[2] == "Music":
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
