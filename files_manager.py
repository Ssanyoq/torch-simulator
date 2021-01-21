import pathlib
import time  # Для тестирования


def check_if_changed(file_path, since):
    """
    Проверяет, был ли изменен файл file с момента времени since
    file - относительный путь файла от программы
    since - кол-во секунд с начала эпохи или типа time
    Возвращает True, если файл был изменен
    и False, если дата изменения была до даты since
    """
    file_name = pathlib.Path(file_path)
    assert file_name.exists(), f"File {file_name} does not exist"
    last_change_time = file_name.stat().st_mtime
    print(last_change_time)
    print(since)
    return since <= last_change_time


def encode_file(file):
    '''
    Ну это типа кодировка, просто чтобы немного защищеннее было
    file - относительный путь файла от программы
    Вызывает ошибку, если его нету
    Ничего не возвращает, изменяет файл
    '''
    file = pathlib.Path(file)
    assert file.exists(), f"File {file} does not exist"
    with open(file, mode='r', encoding='utf-8') as f:
        file_data = f.read()
    new_data = ''
    count = 0
    for symbol in file_data:
        count += 1
        new_data += chr(ord(symbol) + count)
    with open(file, mode='w', encoding='utf-8') as f:
        f.write(new_data)


def decode_file(file):
    '''
    Ну это типа декодировка, просто чтобы немного защищеннее было
    file - относительный путь файла от программы
    Вызывает ошибку, если его нету
    Ничего не возвращает, изменяет файл
    '''
    file = pathlib.Path(file)
    assert file.exists(), f"File {file} does not exist"
    with open(file, mode='r', encoding='utf-8') as f:
        file_data = f.read()
    new_data = ''
    count = 0
    for symbol in file_data:
        count += 1
        new_data += chr(ord(symbol) - count)

    with open(file, mode='w', encoding='utf-8') as f:
        f.write(new_data)
