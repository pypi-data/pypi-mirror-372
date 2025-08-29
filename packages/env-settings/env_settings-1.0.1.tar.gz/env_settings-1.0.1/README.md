# Модуль env-settings
Universal module for using Python program settings based on environment variables

env-settings - это Python-модуль для управления настройками приложения через переменные окружения.
Он предоставляет удобный интерфейс для загрузки, валидации и генерации шаблонов конфигурационных файлов.

# Основные возможности
* Гибкая загрузка настроек из переменных окружения
* Конфигурирование поведения модуля:
* Стратегии обработки ошибок (exit, raise, print, ignore)
* Кастомные сообщения об ошибках
* Строгий режим валидации
* Автоматическая генерация .env файлов на основе анализа кода
* Типизированные настройки с поддержкой значений по умолчанию

# Установка
```shell
pip install env-settings
```

# Использование
## Конфигурирование модуля
```python
from env_settings import config

# Конфигурирование
config.configure(
    error_handling="raise",
    error_messages={"required": "Параметр %s должен быть задан!"}
)

# Сброс к значениям по умолчанию
config.reset()
```
Модуль поддерживает 4 стратегии обработки ошибок.
Для этого необходимо в `error_handling` указать значение Enum `ErrorHandling` или строковое значение:
* `exit` - завершить программу
* `raise` - вызвать исключение
* `print` - вывести сообщение об ошибке в консоль
* `ignore` - игнорировать ошибку и продолжить выполнение

Можно изменить сообщения об ошибке, возникающие при получении параметов.
Для этого необходимо заполнить словарь `error_messages`, используются следующие ключи:
* `required` - обязательный параметр
* `integer` - преобразование параметра к целому числу
* `float` - преобразование параметра к дробному числу
* `file` - обязательное сущствование файла
* `directory` - неудачная попытка создания директории при обязательном существовании

## Определение настроек приложения
```python
# filename: settings.py
from env_settings import get_str_env_param, get_values, get_bool_env_param, get_int_env_param, param_iterator

# URL подключения к базе данных
DATABASE_URL = get_str_env_param('AUTH_USER', required=True)

# Ключ доступа
# может быть указан:
#  - путь до файла (полный или относительный), файл будет прочитана первая строка
#  - строковое значение до первого пробела
API_KEY = get_values(get_str_env_param('API_KEY', required=True), separator=' ')[0]

# Режим отладки
# если задан параметр, 1 (T,Y,True,Yes), то будет включен режим отладки
DEBUG = get_bool_env_param('DEBUG')

# Тайм-аут отведённый на запрос
TIMEOUT = get_int_env_param('TIMEOUT', default=2)

# Идентефикаторы объектов, список значений
# может быть указан:
#  - путь до файла (полный или относительный), одно значение в отдельной строке
#  - строковое значение, значения в наборе должны быть разделены символом ","
OBJECT_IDS = get_values(get_str_env_param('OBJECT_IDS'))


def param_object_ids_iterator():
    """
    Генератор для перебора значений параметра OBJECT_IDS
    :return: Итератор значений
    """
    yield from param_iterator(OBJECT_IDS)
```
Возможные функции получения параметров реализованы в `utils`

## Использование настроек приложения
```python
# filename: main.py
import settings
print(f"Подключение к {settings.DATABASE_URL}")
if settings.DEBUG:
    print(f"Тайм-аут подключения {settings.TIMEOUT}")
```
## Генерация .env файла
```python
# filename: manage.py
from env_settings import generate_env_file

generate_env_file(
    new_env_filename=".env.template",
    settings_filename="settings.py",
    modules_path="src",
    sub_modules_path="modules",
    include_sub_modules=("auth", "payment"),
    exclude_params=("SECRET_KEY",)
)
```
Результат:
```dotenv
# filename: .env.template
# URL подключения к базе данных
DATABASE_URL=

# Ключ доступа
# может быть указан:
#  - путь до файла (полный или относительный), файл будет прочитан
#  - строковое значение
API_KEY=

# Режим отладки
# если задан параметр, 1 (T,Y,True,Yes), то будет включен режим отладки
DEBUG=

# Тайм-аут отведённый на запрос
TIMEOUT=

# Идентефикаторы объектов, список значений
# может быть указан:
#  - путь до файла (полный или относительный), одно значение в отдельной строке
#  - строковое значение, значения в наборе должны быть разделены символом ","
OBJECT_IDS=
```

# Зависимости
Модуль требует стандартной библиотеки Python 3.9+
Для работы требуются библиотеки:
```txt
python-dotenv
```
