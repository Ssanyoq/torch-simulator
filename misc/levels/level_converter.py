def convert_level(level):
    with open(f"""{level}.txt""", encoding='utf-8') as f:
        data = f.readlines()

    level = []

    for i in data:
        level.append(i.rstrip())

    return level


# print(convert_level('level_1'))
