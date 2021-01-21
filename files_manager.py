import pathlib
import time  # Для тестирования


def last_change(file_path):
    """
    Возвращает дату последнего изменения
    файла с относительным путем file_path
    """
    file_name = pathlib.Path(file_path)
    assert file_name.exists(), f"File {file_name} does not exist"
    last_change_time = file_name.stat().st_mtime
    return last_change_time


def encode_file(file):
    '''
    Ну это типа кодировка, просто чтобы немного защищеннее было
    file - относительный путь файла от программы
    Вызывает ошибку, если его нету
    Ничего не возвращает, изменяет файл
    Возвращает зашифрованный файл в формате str
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
    return new_data


def decode_file(file):
    '''
    Ну это типа декодировка, просто чтобы немного защищеннее было
    file - относительный путь файла от программы
    Вызывает ошибку, если его нету
    Возвращает расшифрованный файл в формате str
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

    return new_data
