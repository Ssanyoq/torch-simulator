# Murky gloom (рейтинг R) 
Murky gloom - это 2D free to play инди RPG бродилка-платформер, где игрок путешествует по пещере, пытаясь найти выход. 
В пещере темно, но у игрока есть факелы, которые можно расставлять по пещере, тем самым освещая свой путь.
На пути к выходу из пещеры игрок может повстречать пещерных злодеев и наткнуться на раскаленную магму. 
Игроку нужно быть осторожным, ведь данные препятствия убьют, если к ним прикоснуться
***
## Фичи

### Возможность создавать пользовательские уровни
Делается путем добавления файла с расширением `.txt` в папку `misc/levels`. В файле с уровнем различные символы обозначают разное:
*  Для создания платформы используется символ `-`
*  Для создания стартовой точки персонажа используется символ `S` (в любом регистре)
*  Для создания выхода из пещеры используется символ `F` (тоже в любом регистре). Возможно наличие нескольких выходов, они выглядят красивее, если делать их высотой в 2 символа.
*  Для создания пещерного злодея используется символ `E` (опять же в любом регистре, русская `Е` тоже подойдет). 
   Злодей будет ходить по платформе, на которой появился. Если враг не на платформе, то он не будет заспавнен
*  Для создания блока магмы используется символ `*`. При соприкосновении с магмой персонаж погибает

### Магазин
В игре существует магазин, где можно купить факелы за внутриигровую валюту, условно называемую "Монеты". 
Их можно заработать за прохождение уровней, причем вознаграждение за уже пройденные уровни понижено 

### Сохранение данных
В файле `misc/playerdata.txt` сохраняется актуальная информация о количестве факелов и монет.
Также, по прохождении уровня сохраняется информация о названии файла и времени его прохождения

### Защита сохранений
Предусмотрена защита от подделки прохождения уровней. Сравнивается дата последнего изменения файла с уровнем и дата 
прохождения этого уровня. Если уровень был пройден до последнего изменения файла, то уровень перестает быть пройденым. 
Также файл, где сохранены данные о прохождении уровней и количестве монет и факелов немножко шифруется. Шифровка простая, 
но лучше, чем ничего
***