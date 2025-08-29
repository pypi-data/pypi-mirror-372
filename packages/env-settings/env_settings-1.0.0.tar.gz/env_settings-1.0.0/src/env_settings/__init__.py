from .config import config as settings_config
from .generator import generate_env_file
from .utils import (get_str_env_param, get_int_env_param, get_float_env_param, get_bool_env_param, get_file_env_param,
                    get_filedir_env_param, get_value_from_string, get_values_from_file, get_values,
                    endless_param_iterator, param_iterator, load_env_params)

__all__ = ['configure', 'reset_config', 'generate_env_file', 'get_str_env_param', 'get_int_env_param',
           'get_float_env_param', 'get_bool_env_param', 'get_file_env_param', 'get_filedir_env_param',
           'get_value_from_string', 'get_values_from_file', 'get_values', 'endless_param_iterator', 'param_iterator',
           'load_env_params']


def configure(**kwargs):
    """
    Настройка параметров модуля

    :example:
    configure(
                error_messages={
                    'required': 'Должен быть задан',
                    'integer': 'Должен быть числом',
                    'float': 'Должен быть дробным числом',
                    'file': 'Не найден файл',
                    'directory': 'Невозможно создать директорию'},
                error_handling = 'exit'
            )

    :param kwargs: Параметры конфигурации
    """
    settings_config.configure(**kwargs)


def reset_config():
    """Сброс конфигурации к значениям по умолчанию"""
    settings_config.reset()
