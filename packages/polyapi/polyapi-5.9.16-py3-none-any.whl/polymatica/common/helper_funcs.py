#!/usr/bin/python3
"""
Содержит набор общих вспомогательных классов и функций, использующихся во многих модулях библиотеки.
"""

import logging
import time
from datetime import date, datetime
from typing import Any, Callable, List, Tuple, Union

import requests
from pydantic import ValidationError

from polymatica.common.consts import (
    BASE_LAYER_NAME,
    TYPES_MAP,
    business_logic,
    time_type,
)
from polymatica.exceptions import AuthError, PolymaticaException


class TypeConverter:
    """
    Реализация преобразования типов, определённых Полиматикой, к Python-типам.
    """

    def __init__(
        self,
        sc: business_logic,
        default_value: Any = None,
        convert_empty_values: bool = True,
    ):
        """
        Конструктор класса.
        :param sc: экземпляр класса BusinessLogic.
        :param default_value: (Any) дефолтное значение, использующееся в случае,
            если не удалось преобразовать исходные данные к нужному типу.
        :param convert_empty_values: (bool) нужно ли преобразовывать строки формата "(Пустой)"/"(Empty)"
            к дефолтному значению (см. default_value); по-умолчанию нужно.
        """
        self.sc = sc
        self.default_value = default_value
        self.convert_empty_values = convert_empty_values
        self.datetime_format = sc.get_current_datetime_format()

    def _convert_to_int(self, value: Any) -> Union[int, Any]:
        """
        Преобразование исходных данных в целочисленный тип.
        Если преобразование не удалось - вернутся данные в исходном виде.
        :param value: (Any) исходные данные.
        :return: (int) исходные данные в целочисленном типе.
        """
        try:
            result = int(value)
        except (ValueError, TypeError):
            result = self.default_value
        return result

    def _convert_to_float(self, value: Any) -> Union[float, Any]:
        """
        Преобразование исходных данных в тип дробных чисел.
        Если преобразование не удалось - вернутся данные в исходном виде.
        :param value: (Any) исходные данные.
        :return: (float) исходные данные в виде дробного числа.
        """
        try:
            result = float(value)
        except (ValueError, TypeError):
            result = self.default_value
        return result

    def _convert_to_string(self, value: Any) -> Union[str, Any]:
        """
        Преобразование исходных данных в строковый тип.
        Если преобразование не удалось - вернутся данные в исходном виде.
        :param value: (Any) исходные данные.
        :return: (float) исходные данные в строковом типе.
        """
        try:
            result = str(value)
        except (ValueError, TypeError):
            result = self.default_value
        return result

    def _convert_to_date(self, value: Any) -> Union[date, Any]:
        """
        Преобразование исходных данных в формат даты.
        Если преобразование не удалось - вернутся данные в исходном виде.
        :param value: (Any) исходные данные.
        :return: (int) исходные данные в формате даты.
        """
        # немного костыльный способ, но пока ничего лучше не придумал; если упадёт где-нибудь - будем разбираться
        date_format = self.datetime_format.split(" ")[0]
        try:
            result = datetime.strptime(value, date_format).date()
        except (ValueError, TypeError):
            result = self.default_value
        return result

    def _convert_to_time(self, value: Any) -> Union[time_type, Any]:
        """
        Преобразование исходных данных в формат времени.
        Если преобразование не удалось - вернутся данные в исходном виде.
        :param value: (Any) исходные данные.
        :return: (int) исходные данные в формате времени.
        """
        # немного костыльный способ, но пока ничего лучше не придумал; если упадёт где-нибудь - будем разбираться
        time_format = self.datetime_format.split(" ")[1]
        try:
            result = datetime.strptime(value, time_format).time()
        except (ValueError, TypeError):
            result = self.default_value
        return result

    def _convert_to_datetime(self, value: Any) -> Union[datetime, Any]:
        """
        Преобразование исходных данных в формат дата-время.
        Если преобразование не удалось - вернутся данные в исходном виде.
        :param value: (Any) исходные данные.
        :return: (int) исходные данные в формате дата-время.
        """
        try:
            result = datetime.strptime(value, self.datetime_format)
        except (ValueError, TypeError):
            result = self.default_value
        return result

    def convert_data_types(self, types: list, data: list) -> list:
        """
        Непосредственно функция преобразования типов, определённых Полиматикой, к Python-типам.
        :param types: (list) список используемых типов.
        :param data: (list) набор начальных данных.
        :return: (list) начальные данные, преобразованные к нужному типу.
        """
        convert_funcs_map = {
            "integer": self._convert_to_int,
            "float": self._convert_to_float,
            "string": self._convert_to_string,
            "date": self._convert_to_date,
            "time": self._convert_to_time,
            "datetime": self._convert_to_datetime,
        }

        # по идее, в нормальной ситуации длина списков должна совпадать (длина списка типов равна количеству колонок, а
        # количество колонок должно совпадать с количеством данных); поэтому, если это не так - сгенерируем ошибку
        if len(types) != len(data):
            exception_func = raise_exception(self.sc)
            exception_func(
                PolymaticaException,
                "Length of column list does not match length of data list!",
                with_traceback=False,
            )

        # преобразовываем данные
        result = list()
        not_converted_values = [float("-inf"), float("inf")]
        empty_string_values = ["(пустой)", "(empty)"]
        for item in tuple(zip(data, types)):
            # значение текущего поля
            item_value = item[0]

            # если встретился неконвертируемый тип данных - никаких преобразований делать не нужно, добавляем как есть
            if item_value in not_converted_values:
                result.append(item_value)
                continue

            # если встретилась одна из "пустых" строк и параметром задано, что нужно преобразовать - преобразовываем
            # строку, состоящую только из пробелов, также считаем пустой
            if self.convert_empty_values:
                str_item_value = str(item_value)
                if (
                    str_item_value.lower() in empty_string_values
                    or str_item_value.strip() == ""
                ):
                    result.append(self.default_value)
                    continue

            # всё остальное конвертируем в нужные типы
            convert_func = convert_funcs_map.get(TYPES_MAP.get(item[1]))
            result.append(convert_func(item_value))
        return result


def timing(func: Callable) -> Callable:
    """
    Используется как декоратор функций класса BusinessLogic для профилирования времени работы.
    :param func: декорируемая функция.
    """

    def timing_wrap(self, *args, **kwargs) -> Any:
        """
        Непосредственно функция-декоратор.
        :param self: экземпляр класса BusinessLogic.
        """
        self.func_name = func.__name__
        try:
            logging.info(f'Exec func "{self.func_name}"')
            start_time = time.time()
            result = func(self, *args, **kwargs)
            end_time = time.time()
            self.func_timing = (
                f'func "{self.func_name}" exec time: {end_time - start_time:.2f} sec'
            )
            logging.info(self.func_timing)
            return result
        except SystemExit:
            logging.critical(
                f'Func "{self.func_name}" failure with SystemExit exception!'
            )
            raise

    return timing_wrap


def raise_exception(bl_instance: business_logic) -> Callable:
    """
    Обёртка над функцией-генератором исключений.
    Сделано для того, чтобы каждый раз не передавать в функцию экземпляр класса "BusinessLogic".
    :param bl_instance: экземпляр класса BusinessLogic.
    """

    def wrap(
        exception: Exception,
        message: str,
        extend_message: str = "",
        code: int = 0,
        with_traceback: bool = True,
    ):
        """
        Непосредственно функция, генерирующая пользовательские исключения с заданным сообщением.

        :param exception: вид исключения, которое нужно сгенерировать. Например, ValueError, PolymaticaException...
        :param message: сообщение об ошибке.
        :param extend_message: расширенное сообщение об ошибке (не обязательно).
        :param code: код ошибки (не обязательно).
        :param with_traceback: нужно ли показывать traceback ошибки (по-умолчанию True).
            True актуально только в случае, если функция, генерирующая исключение, вызывается в блоке Except.
            В любом другом случае для корректности отображения ошибки необходимо задавать параметр False.
        :return: (str) сообщение об ошибке, если работа с API происходит через Jupyter Notebook;
            в противном случае генерируется ошибка.
        """
        bl_instance.current_exception = message

        # записываем сообщение в логи
        # logging.error(msg, exc_info=True) аналогичен вызову logging.exception(msg) - вывод с трассировкой ошибки
        # logging.error(msg, exc_info=False) аналогичен вызову logging.error(msg) - вывод без трассировки ошибки
        logging.error(message, exc_info=with_traceback)
        logging.info("APPLICATION STOPPED")

        # если работа с API происходит через Jupyter Notebook, то выведем просто сообщение об ошибке
        if bl_instance.jupiter:
            return message

        # если текущее исключение является наследником класса PolymaticaException, то генерируем ошибку Полиматики
        if issubclass(exception, PolymaticaException):
            raise exception(message, extend_message, code)

        # прочие (стандартные) исключения, по типу ValueError, IndexError и тд
        raise exception(message)

    return wrap


def log(message: str, level: str = "info"):
    """
    Запись сообщения в логи.
    :param message: сообщение, записываемое в логи.
    :param level: уровень логирования; возможны варианты: 'debug', 'info', 'warning', 'error', 'critical'.
        По-умолчанию 'info'.
    """
    level = level.lower()
    if level not in ["debug", "info", "warning", "error", "critical"]:
        level = "info"
    if level == "debug":
        logging.debug(message)
    elif level == "info":
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)
    elif level == "critical":
        logging.critical(message)


def request_with_undefined_suffix_url(
    possible_suffix_urls: List, base_url: str, data: str, timeout: float, headers: dict
) -> Tuple[requests.Response, str]:
    for i, url_suffix in enumerate(possible_suffix_urls):
        current_url = f"{base_url}{url_suffix}"
        result = requests.post(
            url=current_url, data=data, timeout=timeout, headers=headers
        )

        # проверки и вывод результата
        status_code = result.status_code

        if result.ok:
            return result, url_suffix

        if status_code == 404:
            if i != len(possible_suffix_urls) - 1:
                continue
            else:
                error_msg = (
                    "Could not determine URL-address of Polymatica stand! "
                    f"Base URL: {base_url}, Suffixes: {possible_suffix_urls}, "
                    f'Code: {status_code}, Reason: "{result.reason}"'
                )
                raise AuthError(error_msg)
        else:
            error_msg = 'Invalid server response (URL: {}, Code: {}, Reason: "{}", Text: {})'.format(
                current_url,
                status_code,
                result.reason,
                "<empty>" if not result.text else result.text,
            )
            raise AuthError(error_msg)


def validate_params(model, raise_exception_func, **kwargs):
    type_name_map = {
        "string_type": "str",
        "type_error.str": "str",
        "bool_type": "bool",
        "value_error.strictbool": "bool",
        "int_type": "int",
        "type_error.integer": "int",
        "float_type": "float",
        "type_error.float": "float",
        "list_type": "list",
        "type_error.list": "list",
        "dict_type": "dict",
        "type_error.dict": "dict",
    }

    try:
        return model(**kwargs)
    except ValidationError as e:
        first = e.errors()[0]
        loc = first["loc"]
        raw_expected_type = first.get("type", "invalid_type")
        expected_type = type_name_map.get(raw_expected_type, raw_expected_type)
        if len(loc) == 2 and isinstance(loc[1], int):
            field = f'Elements of parameter "{loc[0]}"'
        else:
            field = "Parameter '" + ".".join(str(x) for x in loc) + "'"

        msg = f"{field} must be of type {expected_type}!"
        return raise_exception_func(ValueError, msg, with_traceback=False)


def generate_unique_layer_name(layers_names: list) -> str:
    """
    Метод для генерации уникального имени слоя. Если в списке слоёв есть слой с именем "",
    то фронтенд его преобразует в "Слой 1", поэтому этот метод не возвращает "Слой 1", если
    в списке слоёв есть "".
    """
    n = 1
    normalized_names = {name.strip() for name in layers_names}

    while True:
        new_name = f"{BASE_LAYER_NAME} {n}"
        if new_name not in normalized_names and (n != 1 or "" not in normalized_names):
            return new_name
        n += 1
