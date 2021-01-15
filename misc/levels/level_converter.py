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
                pass
                #  platform = Platform(30, 30, x, y, texture='obstacles/platform.jpg')
                #  obstacles.add(platform)
                #  all_sprites.add(platform)
                # platforms.append(platform)
            elif element == "*":
                pass
                # spike = Spike(30, 30, x, y, texture='obstacles/spike.png')
                # obstacles.add(spike)
                # all_sprites.add(spike)
                # platforms.append(spike)
            elif element == 'E':
                pass
                # a = [i for i in level[count + 1]]
                # max_length_right = a[x // 30:].index(' ') * 30
                # max_length_left = a[:x // 30][::-1].index(' ') * 30
                # enemy = Enemy(30, 30, x, y, max_length_right, max_length_left,
                #               texture='obstacles/platform.jpg')
                # enemies.add(enemy)
                # all_sprites.add(enemy)
            elif element == 'S':
                player_x, player_y = x, y
            x += 30
        count += 1
        y += 30
        x = 0

    return platforms, player_x, player_y