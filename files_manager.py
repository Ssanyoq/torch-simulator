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
