"""
Утилиты для работы с настройками
"""

from os import makedirs, path, getenv
from sys import maxsize
from typing import Optional

from dotenv import load_dotenv

from .config import config, ErrorHandling


def _env_param_error(msg: str):
    """
    Обрабатывает сообщение об ошибке, возникшее при работе с настройками

    В зависимости от конфигурации:
        - останавливает работу программы
        - вызывает исключение
        - выводит сообщение в консоль
        - не выполняет ни каких действий

    :param msg: str: Сообщение об ошибке
    """
    error_handling = ErrorHandling.EXIT if not config.error_handling else config.error_handling
    if error_handling == ErrorHandling.EXIT:
        exit(msg)
    elif error_handling == ErrorHandling.RAISE:
        raise ValueError(msg)
    elif error_handling == ErrorHandling.PRINT:
        print(msg)


def _create_directory(name: str, is_filename: bool = False):
    """
    Создает файловый каталог, если он не существует

    :param name: str: Имя файлового каталога или имя файла
    :param is_filename: bool, default=False: Если в *name* указано имя файла, установить в True
    """
    if name:
        absolute_name = path.abspath(name)
        if is_filename:
            directory = path.dirname(absolute_name)
        else:
            directory = absolute_name
        if not path.exists(directory):
            makedirs(directory)


def get_str_env_param(name: str, required: bool = False, default: str = None) -> Optional[str]:
    """
    Получает значение из переменной окружения *name*

    В случае отсутствия значения, берет значение по умолчанию *default*.
    Если указана обязательность параметра *required* = *True* и отсутствует значение, вызывает обработчик ошибок

    :param name: str: Наименование переменной окружения
    :param required: bool, default=False: Обязательность параметра
    :param default: str, optional: Значение по умолчанию
    :return: str or None: Значение переменной окружения *name* или None
    """
    result = getenv(name, default=str(default) if default else None)
    result = None if not result or not result.strip() else result.strip()
    if required and not result:
        _env_param_error(config.error_messages['required'] % name)
    return result


def get_int_env_param(name: str, required: bool = False, default: int = None) -> Optional[int]:
    """
    Получает *int* значение из переменной окружения *name*

    В случае отсутствия значения, берет значение по умолчанию *default*.
    Если указана обязательность параметра *required* = *True* и отсутствует значение, вызывает обработчик ошибок.
    В случае невозможности привести значение к типу *int* (исключение *ValueError*), вызывает обработчик ошибок

    :param name: str: Наименование переменной окружения
    :param required: bool, default=False: Обязательность параметра
    :param default: int, optional: Значение по умолчанию
    :return: int or None: Значение переменной окружения *name*
    """
    result = get_str_env_param(name, required, str(default) if default else None)
    try:
        result = None if not result else int(result)
        return result
    except ValueError:
        _env_param_error(config.error_messages['integer'] % (name, result))
        return None


def get_float_env_param(name: str, required: bool = False, default: float = None) -> Optional[float]:
    """
    Получает *float* значение из переменной окружения *name*

    В случае отсутствия значения, берет значение по умолчанию *default*.
    Если указана обязательность параметра *required* = *True* и отсутствует значение, вызывает обработчик ошибок.
    В случае невозможности привести значение к типу *float* (исключение *ValueError*), вызывает обработчик ошибок

    :param name: str: Наименование переменной окружения
    :param required: bool, default=False: Обязательность параметра
    :param default: float, optional: Значение по умолчанию
    :return: float or None: Значение переменной окружения *name*
    """
    result = get_str_env_param(name, required, str(default) if default else None)
    try:
        result = None if not result else float(result.replace(',', '.'))
        return result
    except ValueError:
        _env_param_error(config.error_messages['float'] % (name, result))
        return None


def get_bool_env_param(name: str, required: bool = False, default: bool = False) -> bool:
    """
    Получает *boolean* значение из переменной окружения *name*

    В случае отсутствия значения, берет значение по умолчанию *default*.
    Если указана обязательность параметра *required* = *True* и отсутствует значение, вызывает обработчик ошибок.
    В случае значений равных одному из списка *yes,true,t,y,1* результат *True* в иных случаях *False*

    :param name: str: Наименование переменной окружения
    :param required: bool, default=False: Обязательность параметра
    :param default: optional: Значение по умолчанию
    :return: bool: Значение переменной окружения *name*
    """
    result = get_str_env_param(name, required, str(default) if default else False)
    return True if result and result.lower() in ('true', 'yes', 't', 'y', '1') else False


def get_file_env_param(name: str, required: bool = False, default: str = None, file_mast_exist: bool = True,
                       dir_mast_exist: bool = True) -> Optional[str]:
    """
    Получает значение пути к файлу из переменной окружения *name*

    В случае отсутствия значения, берет значение по умолчанию *default*.
    Если указана обязательность параметра *required* = *True* и отсутствует значение, вызывает обработчик ошибок.

    Если указана обязательность существования файла *file_mast_exist* = *True* и файл не существует,
    вызывает обработчик ошибок.
    Если указана обязательность существования файлового каталога *dir_mast_exist* = *True* и каталог не существует,
    создаёт файловый каталог, при невозможности создания каталога, вызывает обработчик ошибок.

    :param name: str: Наименование переменной окружения
    :param required: bool, default=False: Обязательность параметра
    :param default: str, optional: Значение по умолчанию
    :param file_mast_exist: bool, default=True: Обязательность существования файла
    :param dir_mast_exist: bool, default=True: Обязательность существования каталога
    :return: str or None: Значение переменной окружения *name*
    """
    result = get_str_env_param(name, required, default)
    if file_mast_exist:
        if path.exists(result) and path.isfile(result):
            return result
        else:
            _env_param_error(config.error_messages['file'] % (name, result))
            return None
    else:
        if dir_mast_exist:
            try:
                _create_directory(result, is_filename=True)
                return result
            except OSError as e:
                _env_param_error(config.error_messages['directory'] % (name, result, str(e)))
                return None
        else:
            return result


def get_filedir_env_param(name: str, required: bool = False, default=None, dir_mast_exist=True) -> Optional[str]:
    """
    Получает значение пути к файловому каталогу из переменной окружения *name*

    В случае отсутствия значения, берет значение по умолчанию *default*.
    Если указана обязательность параметра *required* = *True* и отсутствует значение, вызывает обработчик ошибок.
    Если указана обязательность существования файлового каталога *dir_mast_exist* = *True* и каталог не существует,
    создаёт файловый каталог, при невозможности создания каталога вызывает обработчик ошибок.

    :param name: str: Наименование переменной окружения
    :param required: bool, default=False: Обязательность параметра
    :param default: str, optional: Значение по умолчанию
    :param dir_mast_exist: bool, default=True: Обязательность существования каталога
    :return: str or None: Значение переменной окружения *name*
    """
    result = get_str_env_param(name, required, default)
    if dir_mast_exist:
        if path.exists(result) and path.isdir(result):
            return result
        else:
            try:
                _create_directory(result)
                return result
            except OSError as e:
                _env_param_error(config.error_messages['directory'] % (name, result, str(e)))
                return None
    else:
        return result


def get_value_from_string(delimited_string: str, index: int = 1, separator: str = ';') -> Optional[str]:
    """
    Возвращает значение из строки с разделителями по указанному индексу

    :param delimited_string: str: Исходная строка с разделителями
    :param index: int, defailt=1: Индекс начиная с еденицы
    :param separator: str, default=';': Разделитель значений
    :return: str or None: Строковое значение
    """
    if delimited_string:
        values_array = delimited_string.split(separator)
        if 0 < index <= len(values_array):
            return values_array[index - 1]
    return None


def get_values_from_file(filename: str, encoding='utf-8') -> [str]:
    """
    Загружает данные из файла в виде списка(статического кортежа) строк

    :param filename: str: Имя файла
    :param encoding: str, default='utf-8': Кодировка файла
    :return: [str]: Кортеж из строк файла
    """
    with open(filename, mode='r', encoding=encoding) as file:
        return file.read().splitlines()


def get_values(param_value: str, default_value: str = None, separator: str = ',') -> [str]:
    """
    Определяет тип значения параметра (файл или строка значений) и возвращает кортеж значений
        - в случае отсутствия значения, возвращается кортеж из одного значения по умолчанию или пустой кортеж
        - в случае, если указан существующий файл, возвращается кортеж строк из файла
        - в остальных случаях, возвращается кортеж из значений разделенных *separator*, либо кортеж из одного значения

    :param param_value: str: Значение параметра
    :param default_value: str, default=None: Значение по умолчанию
    :param separator: str, default=',': Разделитель значений
    :return: [str]: Кортеж значений
    """
    if not param_value:
        if default_value:
            return [default_value]
        return []

    if path.exists(param_value) and path.isfile(param_value):
        return get_values_from_file(param_value)

    return param_value.split(separator)


def endless_param_iterator(param_values: list) -> iter:
    """
    Условно "бесконечный" генератор для цикличного перебора значений из указанного списка

    После достижения последнего значения в списке, генератор возвращает первое

    :param param_values: list: Список значений
    :return: iter: Итератор значений
    """
    for i in range(maxsize):
        yield param_values[i % len(param_values)]


def param_iterator(param_values: list) -> iter:
    """
    Генератор для перебора значений из указанного списка

    :param param_values: list: Список значений
    :return: iter: Итератор значений
    """
    for i in range(len(param_values)):
        yield param_values[i]


def load_env_params(env_filename: str = None, **kwargs) -> bool:
    """
    Загружает .env файл, используя `dotenv.load_dotenv()`

    :param env_filename: str, optional: Имя файла
    :param kwargs: **, optional: Параметры для передачи в функцию *load_dotenv*
    :return: bool: True, если установлен хотя бы один параметр (переменная среды), иначе False
    """
    return load_dotenv(env_filename, **kwargs)
