#!/usr/bin/python3
"""
Описание типов данных и констант, использующихся в PPL.
"""

from typing import NewType

# типы данных
business_logic = NewType("BusinessLogic", str)
graph = NewType("Graph", str)
time_type = NewType("Time", str)
json_type = NewType("JSON", str)
datetime_type = NewType("Datetime", str)
responce = NewType("Responce", str)

# коды различных типов модулей
MULTISPHERE_ID = 500
GRAPH_ID = 600
MAP_ID = 700
ASSOCIATION_RULES_ID = 800
CLUSTERING_ID = 900
FORECAST_ID = 1000

# маппинг "код модуля - наименование модуля"
CODE_NAME_MAP = {
    MULTISPHERE_ID: "Мультисфера",
    GRAPH_ID: "Графика",
    MAP_ID: "Карты",
    ASSOCIATION_RULES_ID: "Ассоциативные правила",
    CLUSTERING_ID: "Кластеризация",
    FORECAST_ID: "Прогнозирование",
}

# соответствие числового и строкового типов, используемых Полиматикой
POLYMATICA_INT_TYPES_MAP = {
    0: "uint8",
    1: "uint16",
    2: "uint32",
    3: "uint64",
    4: "double",
    5: "string",
    6: "date",
    7: "time",
    8: "datetime",
    9: "date_year",
    10: "date_quarter",
    11: "date_month",
    12: "date_day",
    13: "date_week",
    14: "date_wday",
    15: "time_hour",
    16: "time_minute",
    17: "time_second",
    18: "none",
    19: "unknown",
}

# соответствие строкового и числового типов, используемых Полиматикой
POLYMATICA_TYPES_INT_MAP = {v: k for k, v in POLYMATICA_INT_TYPES_MAP.items()}

# соответствие типов, используемых Полиматикой, с типами данных Python Core
TYPES_MAP = {
    "uint8": "integer",
    "uint16": "integer",
    "uint32": "integer",
    "uint64": "integer",
    "double": "float",
    "string": "string",
    "date": "date",
    "time": "time",
    "datetime": "datetime",
    "date_year": "integer",
    "date_quarter": "integer",
    "date_month": "string",
    "date_day": "integer",
    "date_week": "integer",
    "date_wday": "string",
    "time_hour": "integer",
    "time_minute": "integer",
    "time_second": "integer",
    "none": "none",
    "unknown": "unknown",
}

# сопоставление положения размерности в мультисфере
POSITION_MAP = {0: "out", 1: "left", 2: "up"}

# описание типов фактов (строка - число)
MEASURE_STR_INT_TYPES_MAP = {
    "Значение": 0,
    "Процент": 1,
    "Ранг": 2,
    "Количество уникальных": 3,
    "Среднее": 4,
    "Отклонение": 5,
    "Минимум": 6,
    "Максимум": 7,
    "Изменение": 8,
    "Изменение в %": 9,
    "Нарастающее": 10,
    "ABC": 11,
    "Медиана": 12,
    "Количество": 13,
}

# описание типов фактов (число - строка)
MEASURE_INT_STR_TYPES_MAP = {v: k for k, v in MEASURE_STR_INT_TYPES_MAP.items()}

# месяцы
MONTHS = [
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь",
]

# дни недели
WEEK_DAYS = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье",
]
WEEK = {
    "понедельник": 0,
    "вторник": 1,
    "среда": 2,
    "четверг": 3,
    "пятница": 4,
    "суббота": 5,
    "воскресенье": 6,
}

# константы, использующиеся для создания вычислимых фактов
OPERANDS = ["=", "+", "-", "*", "/", "<", ">", "!=", "<=", ">="]
LOGIC_FUNCS = ["or", "and", "not"]
FUNCS = ["top", "total", "corr"]

# создания и обновления мультисфер
INTERVAL_MAP = {
    "с текущего дня": 0,
    "с предыдущего дня": 1,
    "с текущей недели": 2,
    "с предыдущей недели": 3,
    "с текущего месяца": 4,
    "с предыдущего месяца": 5,
    "с текущего квартала": 6,
    "с предыдущего квартала": 7,
    "с текущего года": 8,
    "с предыдущего года": 9,
    "с указанной даты": 10,
    "с и по указанную дату": 11,
}
UPDATE_TYPES = [
    "ручное",
    "по расписанию",
    "интервальное",
    "инкрементальное",
    "обновление измененных записей",
]
UPDATE_PERIOD = {"Ежедневно": 1, "Еженедельно": 2, "Ежемесячно": 3}
DB_SOURCE_TYPES = [4, 5, 6, 8, 10, 11, 18]
INTERVAL_BORDERS_DATE_FORMAT = "%d.%m.%Y"
CUBE_NAME_FORBIDDEN_CHARS = "%^&=;±§`~][}{<>"
SOURCE_NAME_ALLOWED_CHARS = (
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюяabcdefghijklmnopqrstuvwxyz0123456789 _-"
)
SOURCE_TYPES = ["excel", "csv", "mssql", "mysql", "psql", "jdbc", "odbc"]

# прочие
ISO_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
ALL_PERMISSIONS = 31
DEFAULT_POLYMATICA_VERSION = "5.9"
FORMAT_SETTINGS_KEYS = [
    "precision",
    "delim",
    "prefix",
    "suffix",
    "split",
    "measureUnit",
    "color",
]
API_VERSION = "v2"
ROOT_PARENT = "00000000"
EMPTY_ID = "00000000"
UNITS_LOAD_DATA_CHUNK = 1000
BASE_LAYER_NAME = "Слой"
MIN_MEASURE_CELL_WIDTH = 60
MIN_OLAP_WIDTH = 790
