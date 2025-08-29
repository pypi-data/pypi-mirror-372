"""
Конфигурация поведения обработчиков для работы с настройками
"""
from enum import Enum
from typing import Union


class ErrorHandling(Enum):
    """Перечисление методов обработки ошибок"""
    EXIT = 'exit'  # Остановить работу программы
    RAISE = 'raise'  # Вызывать исключение
    PRINT = 'print'  # Вывести сообщение в консоль
    IGNORE = 'ignore'  # Не выполнять действий

    @classmethod
    def from_value(cls, value: Union[str, 'ErrorHandling']) -> 'ErrorHandling':
        """
        Преобразует строковое значение или экземпляр enum в элемент перечисления.
        Возвращает соответствующий элемент ErrorHandling.
        """
        if isinstance(value, ErrorHandling):
            return value
        try:
            return cls(value)
        except ValueError:
            valid_values = [e.value for e in cls]
            raise ValueError(f'Недопустимое значение: {value}'
                             f'Допустимые значения: {valid_values}') from None

    def __str__(self):
        return self.value


class _Config:
    def __init__(self):
        _msg_prefix = 'settings: Ошибка загрузки настроек! Параметр'
        # Параметры по умолчанию
        self._error_messages = {
            'required': f'{_msg_prefix} %s должен быть задан!',
            'integer': f'{_msg_prefix} %s=%s. Должен быть числом!',
            'float': f'{_msg_prefix} %s=%s. Должен быть дробным числом (с разделителем точка: 0.0)!',
            'file': f'{_msg_prefix} %s=%s. Не найден указанный файл!',
            'directory': f'{_msg_prefix} %s=%s. Невозможно создать директорию! %s'
        }
        self._error_handling = ErrorHandling.RAISE
        self._env_generator_pattern = r'^(?:\s*(?:#.*)?\s*[\r\n]+)*\s*[A-Z0-9_-]+\s*=\s.*?param.*?\(.*?\).*$'

    @property
    def error_messages(self):
        return self._error_messages

    @property
    def error_handling(self):
        return self._error_handling

    @property
    def env_generator_pattern(self):
        return self._env_generator_pattern

    def configure(self, error_messages: dict = None, error_handling: Union[str, ErrorHandling] = None,
                  env_generator_pattern: str = None):
        """Обновление параметров конфигурации"""
        if error_messages:
            if not isinstance(error_messages, dict):
                raise TypeError('error_messages должен быть словарем')
            self._error_messages.update(error_messages)

        if error_handling:
            self._error_handling = ErrorHandling.from_value(error_handling)

        if env_generator_pattern:
            self._env_generator_pattern = env_generator_pattern

    def reset(self):
        """Сброс настроек к значениям по умолчанию"""
        self.__init__()


# Экземпляр синглтона для глобального доступа
config = _Config()
