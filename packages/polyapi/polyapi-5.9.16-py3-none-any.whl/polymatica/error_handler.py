#!/usr/bin/python3
""" Модуль обработки ошибок из ответа """

import datetime
import os
import re
from datetime import datetime as dt

import requests
from packaging.version import Version

from polymatica.common.consts import (
    CUBE_NAME_FORBIDDEN_CHARS,
    FUNCS,
    INTERVAL_BORDERS_DATE_FORMAT,
    INTERVAL_MAP,
    LOGIC_FUNCS,
    MONTHS,
    SOURCE_NAME_ALLOWED_CHARS,
    SOURCE_TYPES,
    UPDATE_PERIOD,
    UPDATE_TYPES,
    WEEK,
    WEEK_DAYS,
)
from polymatica.common.helper_funcs import raise_exception


def request_asserts(response: dict, r: requests.models.Response) -> bool:
    """
    Проверка ответов сервера.
    :param response: (dict) ответ сервера в формате json (по сути, это r.json()).
    :param r: <class 'requests.models.Response'>
    :return: True, если все проверки прошли успешно, иначе будет сгенерирован AssertionError.
    """
    # парсинг ответа
    response_queries = response.get("queries")
    assert len(response_queries) > 0, 'No field "queries" in response!'
    resp_queries = next(iter(response_queries))  # [0] element in vector
    resp_command = resp_queries.get("command")
    resp_command_err = resp_command.get("error")

    assert resp_command, str(resp_command_err)
    assert r.status_code == 200, "Response code != 200"

    if "error" in resp_command:
        resp_command_err_code = resp_command_err.get("code")
        resp_command_err_message = resp_command_err.get("message")
        assert (
            resp_command_err_code == 0
        ), f"Error in response: {resp_command_err_message}"

    if ("error" in resp_command) and ("status" in resp_command):
        resp_command_status = resp_command.get("status")
        resp_command_status_code = resp_command_status.get("code")
        resp_command_status_message = resp_command_status.get("message")
        assert (
            resp_command_status_code == 0
        ), f"Error in response: {resp_command_status_message}"

    if ("error" in resp_command) and ("datasources" in resp_command):
        resp_command_datasources = next(
            iter(resp_command.get("datasources"))
        )  # [0] element in vector
        datasources_status = resp_command_datasources.get("status")
        datasources_status_code = datasources_status.get("code")
        resp_command_status_message = datasources_status.get("message")
        assert (
            datasources_status_code == 0
        ), f"Error in response: {resp_command_status_message}"

    return True


def check_time(time: str) -> bool:
    """
    Проверка формата времени.
    Вернёт False, если формат времени задан неправильно, иначе True.
    """
    try:
        splitted_time = time.split(":")
        datetime.time(int(splitted_time[0]), int(splitted_time[1]))
        return True
    except (ValueError, TypeError):
        return False


def check_cube_name(cube_name, forbidden_chars):
    trimmed_cube_name = cube_name.strip()
    if len(trimmed_cube_name) < 5:
        raise ValueError(
            "The cube name must contain at least 5 characters "
            "after removing leading and trailing spaces!"
        )
    if any(char in forbidden_chars for char in trimmed_cube_name):
        raise ValueError(
            "The cube name must not contain forbidden characters: "
            "% ^ & = ; ± § ` ~ ] [ } { < >"
        )


def generate_unique_cube_name(cube_name: str, cubes_list: list, n: int = 0) -> str:
    while True:
        new_name = cube_name.strip() if n == 0 else f"{cube_name.strip()}({n})"
        if not any(cube["name"] == new_name for cube in cubes_list):
            return new_name
        n += 1


def get_date(date: str, date_format: str) -> datetime:
    """
    Возвращает дату объекта datetime по строковому формату даты.
    Если преобразование строковой даты по заданному формату невозможно - будет сгенерирована ошибка.
    :param date: строка даты
    :param date_format: ожидаемый формат строки даты
    :return: объект datetime
    """
    return datetime.datetime.strptime(date, date_format)


class Validator:
    """
    Класс для проверки входных параметров различных методов
    """

    def __init__(self, bl):
        """
        :param bl: экземпляр класса BusinessLogic
        """
        self.bl = bl
        # хранит функцию-генератор исключений
        self._raise_exception = raise_exception(self.bl)
        # Словарь для маппинга названий функций на соответствующие методы проверки
        self.validation_methods_mapping = {
            "rename_group": self.check_rename_group,
            "move_dimension": self.check_move_dimension,
            "polymatica_health_check_multisphere_updates": self.check_polymatica_health_check,
            "select_unselect_impl": self.check_select_unselect_impl,
            "sort_measure": self.check_sort_measure,
            "unfold_all_dims": self.check_unfold_all_dims,
            "set_width_columns": self.check_set_width_columns,
            "put_dim_filter": self.check_put_dim_filter,
            "export": self.check_export,
            "run_scenario": self.check_run_scenario,
            "set_measure_precision": self.check_set_measure_precision,
            "set_measure_format": self.check_set_measure_format,
            "create_sphere": self.check_create_sphere,
            "update_cube": self.check_update_cube,
            "execute_olap_command": self.check_execute_olap_command,
            "load_sphere_chunk": self.check_load_sphere_chunk,
            "set_measure_level": self.check_set_measure_level,
            "set_measure_select": self.check_set_measure_select,
            "set_all_measure_visibility": self.check_set_all_measure_visibility,
            "set_measure_direction": self.check_set_measure_direction,
            "get_scenario_metadata": self.check_get_scenario_metadata,
            "reset_filters": self.check_reset_filters,
            "get_cube_info": self.check_get_cube_info,
            "clone_olap_module": self.check_clone_olap_module,
            "create_calculated_measure": self.check_create_calculated_measure,
            "group_dimensions": self.check_group_dimensions,
            "wait_cube_loading": self.check_wait_cube_loading,
            "create_consistent_dim": self.check_create_consistent_dim,
            "check_bom_in_dims_and_measures": self.check_bom_in_dims_and_measures,
        }

    def validate(self, func_name, *args):
        """
        Основной метод проверки входных параметров.
        :param func_name: название функции
        :param args: аргументы для проверки
        :return: результат проверки или поднимает исключение ValueError
        """
        if func_name not in self.validation_methods_mapping:
            return self._raise_exception(
                ValueError,
                f"No function to check: {func_name}",
                with_traceback=False,
            )

        return self.validation_methods_mapping.get(func_name)(*args)

    @staticmethod
    def check_rename_group(group_uuid, group_name, new_name):
        if not group_uuid:
            raise ValueError(f"No such group: {group_name}")
        if not new_name:
            raise ValueError("New group name cannot be empty!")
        return True

    def check_move_dimension(self, position, level, dim_name):
        if not self.bl.multisphere_module_id:
            raise ValueError("First create cube and get data from it!")

        if not isinstance(position, str):
            raise ValueError('Param "position" must be str type!')
        if level is not None and not isinstance(level, int):
            raise ValueError('Param "level" must be int type or None!')

        num_position = {"left": 1, "up": 2, "out": 0}.get(position, -1)
        if num_position == -1:
            raise ValueError(
                f'Position "{position}" does not exist! It can only be "up", "left" or "out"!'
            )

        dim_id = self.bl.get_dim_id(dim_name)
        if num_position in [1, 2]:
            if level is None:
                raise ValueError(
                    "When moving a dimension to the left/up, "
                    'the parameter "level" must be explicitly specified!'
                )

            result = self.bl.execute_olap_command(
                command_name="view",
                state="get",
                from_row=0,
                from_col=0,
                num_row=1,
                num_col=1,
            )
            left_active_dim_ids = self.bl.h.parse_result(
                result, "left_dims", default_value=list()
            )
            top_active_dim_ids = self.bl.h.parse_result(
                result, "top_dims", default_value=list()
            )
            active_ids = (
                left_active_dim_ids if num_position == 1 else top_active_dim_ids
            )
            if level > len(active_ids):
                raise ValueError(
                    f"Invalid level! Total levels: {len(active_ids) - 1}, current level: {level}"
                )

        return dim_id, num_position

    @staticmethod
    def check_polymatica_health_check(cubes_list, cube_name):
        for cube in cubes_list:
            if cube["name"] == cube_name:
                return True
        raise ValueError(f"No such cube in cubes list: {cube_name}!")

    @staticmethod
    def check_select_unselect_impl(left_dims, top_dims, position):
        if position not in ["left", "top"]:
            raise ValueError('Param "position" must be either "left" or "top"!')
        if position == "left" and not left_dims:
            raise ValueError("Left dimensions required!")
        if position == "top" and not top_dims:
            raise ValueError("Top dimensions required!")
        return 1 if position == "left" else 2

    @staticmethod
    def check_sort_measure(sort_type):
        common_types = {"off": 0, "ascending": 1, "descending": 2}
        if sort_type not in common_types:
            raise ValueError(
                'Param "sort_type" can only equals "ascending" or "descending" or "off"!'
            )
        return common_types[sort_type]

    @staticmethod
    def check_unfold_all_dims(position, level):
        # проверка позиции
        if position not in ["left", "up"]:
            raise ValueError('Param "position" must be either "left" or "up"!')
        # проверка значения уровня
        if level < 0:
            raise ValueError('Param "level" can be only positive!')
        return 1 if position == "left" else 2

    @staticmethod
    def check_set_width_columns(measures, measures_list, left_dims, left_dims_data):
        error_msg = ""
        if len(measures) != len(measures_list):
            error_msg = (
                'The length of the list in the "measures" parameter '
                "must match the number of unhidden facts in the multisphere!"
            )
        if len(left_dims) != len(left_dims_data):
            error_msg = (
                'The length of the list in the "left_dims" parameter must '
                "match the number of left dimensions of the multisphere!"
            )
        if error_msg:
            raise ValueError(error_msg)
        return True

    def check_put_dim_filter(
        self, filter_name, start_date, end_date, filter_field_format, dim_name, dim_id
    ):
        """
        Проверка параметров для функции put_dim_filter.
        :param filter_name: имя фильтра
        :param start_date: начальная дата
        :param end_date: конечная дата
        :param filter_field_format: формат поля фильтра
        :param dim_name: имя измерения
        :param dim_id: ID измерения
        :return: список дат
        """
        # Базовые проверки параметров
        self._validate_filter_params(
            filter_name, start_date, end_date, dim_name, dim_id
        )

        # Обработка дат и формирование списка фильтрации
        dates_list = []
        if (filter_name is None) and (start_date is not None and end_date is not None):
            dates_list = self._process_date_range(
                start_date, end_date, filter_field_format
            )

        return dates_list

    @staticmethod
    def _validate_filter_params(filter_name, start_date, end_date, dim_name, dim_id):
        """
        Проверка базовых параметров фильтрации.
        :param filter_name: имя фильтра
        :param start_date: начальная дата
        :param end_date: конечная дата
        :param dim_name: имя измерения
        :param dim_id: ID измерения
        """
        if (filter_name is None) and (start_date is None and end_date is None):
            raise ValueError(
                "If you don't filter one value by param filter_name,"
                " please assign value to args start_date AND end_date!"
            )
        elif (filter_name is not None) and (
            start_date is not None and end_date is not None
        ):
            raise ValueError(
                "Please, fill in arg filter_name for filtering one value OR:\n"
                "args start_date AND end_date for filtering date interval!"
            )
        if dim_name is None and dim_id is None:
            raise ValueError("You should specify dim_name or dim_id")

    def _process_date_range(self, start_date, end_date, filter_field_format):
        """
        Обработка диапазона дат.
        :param start_date: начальная дата
        :param end_date: конечная дата
        :param filter_field_format: формат поля фильтра
        :return: список дат
        """
        # Обработка дат различных форматов
        if isinstance(start_date, str) and isinstance(end_date, str):
            if self._is_week_day_format(start_date, end_date):
                return self._process_week_days(start_date, end_date)
            elif self._is_month_format(start_date, end_date):
                return self._process_months(start_date, end_date)
            else:
                return self._process_date_strings(
                    start_date, end_date, filter_field_format
                )
        elif isinstance(start_date, int) and isinstance(end_date, int):
            return self._process_numeric_dates(start_date, end_date)
        else:
            raise ValueError(
                f"Unknown date format! start_date: {start_date}, end_date: {end_date}"
            )

    @staticmethod
    def _is_week_day_format(start_date, end_date):
        """
        Проверка, являются ли даты днями недели.
        :param start_date: начальная дата
        :param end_date: конечная дата
        :return: True, если обе даты - дни недели
        """
        return start_date in WEEK_DAYS and end_date in WEEK_DAYS

    @staticmethod
    def _is_month_format(start_date, end_date):
        """
        Проверка, являются ли даты месяцами.
        :param start_date: начальная дата
        :param end_date: конечная дата
        :return: True, если обе даты - месяцы
        """
        return start_date in MONTHS and end_date in MONTHS

    @staticmethod
    def _process_week_days(start_date, end_date):
        """
        Обработка дней недели.
        :param start_date: начальный день недели
        :param end_date: конечный день недели
        :return: список дней недели
        """
        start_ind = WEEK_DAYS.index(start_date)
        end_ind = WEEK_DAYS.index(end_date)
        if start_ind > end_ind:
            raise ValueError("Start week day can not be more than the end week day!")
        return WEEK_DAYS[start_ind : end_ind + 1]

    @staticmethod
    def _process_months(start_date, end_date):
        """
        Обработка месяцев.
        :param start_date: начальный месяц
        :param end_date: конечный месяц
        :return: список месяцев
        """
        start_ind = MONTHS.index(start_date)
        end_ind = MONTHS.index(end_date)
        if start_ind > end_ind:
            raise ValueError("Start month can not be more than the end month!")
        return MONTHS[start_ind : end_ind + 1]

    @staticmethod
    def _process_numeric_dates(start_date, end_date):
        """
        Обработка числовых дат.
        :param start_date: начальная дата (число)
        :param end_date: конечная дата (число)
        :return: список дат в виде строк
        """
        if start_date > end_date:
            raise ValueError("Start date can not be more than the end date!")
        end_date += 1
        return [str(x) for x in range(start_date, end_date)]

    def _process_date_strings(self, start_date, end_date, filter_field_format):
        """
        Обработка строковых дат различных форматов.
        :param start_date: начальная дата (строка)
        :param end_date: конечная дата (строка)
        :param filter_field_format: формат поля фильтра
        :return: список дат
        """
        if not filter_field_format:
            raise ValueError("filter_field_format must be specified!")
        try:
            start_dt = dt.strptime(start_date, filter_field_format)
            end_dt = dt.strptime(end_date, filter_field_format)
            start = start_dt if "%S" in filter_field_format else start_dt.date()
            end = end_dt if "%S" in filter_field_format else end_dt.date()
        except ValueError:
            raise ValueError(
                f"Unknown date format! start_date: {start_date}, end_date: {end_date}"
            )

        if start > end:
            raise ValueError("Start date can not be more than the end date!")

        # Заполняем dates_list
        dates_list = []
        step = datetime.timedelta(days=1)

        # если версия аналитикс 5.9.12 или выше, то добавляем миллисекунды к датам
        current_polymatica_version = self.bl.full_polymatica_version.split("-")[0]
        current_polymatica_version = Version(current_polymatica_version)
        edge_version = Version("5.9.12")
        while start <= end:
            if (
                current_polymatica_version >= edge_version
                and "%S" in filter_field_format
            ):
                dates_list.append(
                    self._format_datetime_with_millis(start, filter_field_format)
                )
            else:
                dates_list.append(start.strftime(filter_field_format))
            start += step

        return dates_list

    @staticmethod
    def _format_datetime_with_millis(dt: datetime.datetime, pattern: str) -> str:
        base = dt.strftime(pattern)
        millis = f"{dt.microsecond // 1000:03d}"
        if "%f" in pattern:
            # Если %f есть, то заменим его на миллисекунды
            base = base.replace(dt.strftime("%f"), millis)
        else:
            # Иначе просто добавим миллисекунды в конце через точку
            base = f"{base}.{millis}"
        return base

    @staticmethod
    def check_export(file_format, file_path):
        """
        Проверка параметров для функции export.
        :param file_format: формат файла
        :param file_path: путь к файлу
        :return: True, если проверка прошла успешно
        """
        if file_format not in ["csv", "xls", "json"]:
            raise ValueError(
                f'Wrong file format: "{file_format}". Only .csv, .xls, .json formats allowed!'
            )
        if not file_path:
            raise ValueError("Empty file path!")
        return True

    @staticmethod
    def check_run_scenario(scenario_id, scenario_name, _):
        """
        Проверка параметров для функции run_scenario.
        :param scenario_id: ID сценария
        :param scenario_name: имя сценария
        :param _: неиспользуемый параметр
        :return: True, если проверка прошла успешно
        """
        if (scenario_id is None) and (scenario_name is None):
            raise ValueError(
                "You need to enter either the uuid or "
                "the scenario name and, if necessary, the path to it!"
            )
        return True

    @staticmethod
    def check_set_measure_precision(measure_names, precisions):
        """
        Проверка параметров для функции set_measure_precision.
        :param measure_names: имена мер
        :param precisions: точности
        :return: True, если проверка прошла успешно
        """
        if len(measure_names) != len(precisions):
            raise ValueError(
                "Length of list with fact names (%s) != length of list with fact precisions (%s).",
                (len(measure_names), len(precisions)),
            )
        for precision in precisions:
            if not isinstance(precision, int) or precision < 0 or precision > 9:
                raise ValueError(
                    "The fact precision must be specified as a number (int) from 0 to 9."
                )
        return True

    @staticmethod
    def check_set_measure_format(measure_names, measure_formats, extracted_settings):
        """
        Проверка параметров для функции set_measure_format.
        :param measure_names: имена мер
        :param measure_formats: форматы мер
        :param extracted_settings: извлеченные настройки
        :return: True, если проверка прошла успешно
        """
        if len(measure_names) != len(measure_formats):
            raise ValueError(
                "Length of list with fact names (%s) != length of list with fact formats (%s)."
                % (len(measure_names), len(measure_formats))
            )

        # Проверка точности
        for precision in extracted_settings.get("precision"):
            if not isinstance(precision, int) or precision < 0 or precision > 9:
                raise ValueError(
                    "The fact precision must be specified as a number (int) from 0 to 9."
                )

        # Проверка разделителя
        for delim in extracted_settings.get("delim"):
            if delim not in (",", ".", " "):
                raise ValueError(
                    'The delimiter (delim) must be a period, comma, or space. (",", ".", " ")'
                )

        # Проверка префикса
        for prefix in extracted_settings.get("prefix"):
            if not isinstance(prefix, str):
                raise ValueError("Prefix must be specified as a string (str)!")

        # Проверка суффикса
        for suffix in extracted_settings.get("suffix"):
            if not isinstance(suffix, str):
                raise ValueError("Suffix must be specified as a string (str)!")

        # Проверка разделения
        for split in extracted_settings.get("split"):
            if not isinstance(split, bool):
                raise ValueError("The split parameter must be True or False (bool)!")

        # Проверка единицы измерения
        for measureUnit in extracted_settings.get("measureUnit"):
            if measureUnit not in ("", "thousand", "million", "billion"):
                raise ValueError(
                    "The measureUnit parameter must be a value from the list: "
                    '["", "thousand", "million", "billion"]'
                )

        # Проверка цвета
        color_pattern = r"^#[0-9A-Fa-f]{6}$"
        for color in extracted_settings.get("color"):
            if not re.match(color_pattern, color):
                raise ValueError(
                    "The color must be specified in hexadecimal format, "
                    'for example "#FFFFFF", "#000000"'
                )

        return True

    @staticmethod
    def check_bom_in_dims_and_measures(arg):
        """
        Проверка есть ли в названиях размерностей и фактов метка порядка байтов
        U + FEFF Byte Order МАРК (BOM)
        :return: True, если проверка прошла успешно
        """
        search_str = "\ufeff"
        if search_str in arg.get("name", str()) or search_str in arg.get(
            "db_field", str()
        ):
            raise ValueError(
                "Change the encoding of the source file to UTF-8 without BOM!"
            )
        return True

    def check_create_sphere(
        self,
        update_params,
        file_type,
        sql_params,
        user_interval,
        source_name,
        cube_name,
        time_zones,
        increment_dim,
        interval_dim,
        interval_borders,
        encoding,
        relevance_date,
        indirect_cpu_load_parameter,
    ):
        """
        Проверка параметров функции create_sphere.
        :param update_params: параметры обновления
        :param file_type: тип файла
        :param sql_params: параметры SQL
        :param user_interval: интервал обновлений
        :param source_name: имя источника
        :param cube_name: имя куба
        :param time_zones: временные зоны
        :param increment_dim: размерность для инкрементального обновления
        :param interval_dim: размерность для интервального обновления
        :param interval_borders: границы интервала
        :param relevance_date: параметры отображения даты актуальности данных
        :param indirect_cpu_load_parameter: параметры предельного процента использования CPU
        :return: имя куба
        """
        # проверка, что создается мультисфера с уникальным названием
        cubes_list = self.bl.get_cubes_list()
        cube_name = generate_unique_cube_name(cube_name, cubes_list)

        # проверка названия мультисферы на запрещенные символы
        check_cube_name(cube_name=cube_name, forbidden_chars=CUBE_NAME_FORBIDDEN_CHARS)

        # проверка типа файла
        self._validate_file_type(file_type)

        # проверка заданного типа обновления и его параметров
        self._validate_update_params(update_params=update_params, time_zones=time_zones, file_type=file_type)

        # проверки инкрементального и интервального обновления
        update_type = update_params.get("type")
        self._validate_increment_update(update_type, increment_dim)
        self._validate_interval_update(
            update_type, interval_dim, user_interval, interval_borders
        )

        # проверка корректности параметров в словаре sql_params
        self._validate_sql_params(file_type, sql_params)

        # проверка длины и отсутствия пробелов в имени источника
        self._validate_source_name(source_name)

        # проверка кодировки
        self._validate_encoding(file_type, encoding)

        # проверка параметров даты актуальности данных
        self._validate_relevance_date(relevance_date)

        # проверка параметров предельного процента использования CPU
        indirect_cpu_load_parameter = self._validate_indirect_cpu_load_parameter(indirect_cpu_load_parameter)

        self.bl.func_name = "create_sphere"
        return cube_name, indirect_cpu_load_parameter

    def _validate_indirect_cpu_load_parameter(self, indirect_cpu_load_parameter):
        """
        Проверка параметров предельного процента использования CPU
        """
        default_cpu_load_percent = self.bl.config.get("indirect_sort_cpu_load_percent")
        indirect_sort_enabled = default_cpu_load_percent is not None

        if not indirect_sort_enabled:
            if indirect_cpu_load_parameter is not None:
                self.bl.logger.warning("Indirect sort is disabled in Polymatica Analytics config. "
                                       "The parameter 'indirect_cpu_load_parameter' is not applicable.")
            indirect_cpu_load_parameter = None
            default_cpu_load_percent = 80

        if indirect_cpu_load_parameter is None:
            indirect_cpu_load_parameter = {
                "percent": default_cpu_load_percent,
                "use_default_value": True,
            }
        else:
            percent = indirect_cpu_load_parameter.get("percent")
            use_default_value = indirect_cpu_load_parameter.get("use_default_value")

            if not isinstance(use_default_value, bool):
                raise ValueError(f'Param "use_default_value" in indirect_cpu_load_parameter '
                                 f'can only be boolean: True / False!')
            elif not use_default_value and not isinstance(percent, int):
                raise ValueError(f'Param "percent" in indirect_cpu_load_parameter '
                                 f'can only be int!')
            elif not use_default_value and (percent < 1 or percent > 100):
                raise ValueError(f'Param "percent" in indirect_cpu_load_parameter '
                                 f'must be in the range from 1 to 100!')
            elif use_default_value or (not use_default_value and percent > default_cpu_load_percent):
                indirect_cpu_load_parameter["percent"] = default_cpu_load_percent

        return indirect_cpu_load_parameter

    def _validate_encoding(self, file_type, encoding):
        """
        Проверка кодировки. Для источника формата csv она должна быть обязательно задана.
        """
        if file_type == "csv" and encoding == "":
            raise ValueError("For csv source encoding must be specified!")

    def _validate_relevance_date(self, relevance_date):
        if relevance_date:
            required_keys = ("relevance_date_dimension", "format", "consider_filter")
            if set(relevance_date.keys()) != set(required_keys):
                keys_str = ", ".join(required_keys)
                raise ValueError(f'There must be all required keys: {keys_str} in relevance date dict.')
            relevance_date_dimension = relevance_date.get("relevance_date_dimension")
            relevance_date_format = relevance_date.get("format")
            consider_filter = relevance_date.get("consider_filter")

            if not isinstance(relevance_date_dimension, str):
                raise ValueError('Param "relevance_date_dimension" for relevance date can only be str!')
            if relevance_date_format not in ("datetime", "date"):
                raise ValueError(f'Unknown format: {relevance_date_format} for relevance date. Allowed formats: '
                                 f'"datetime", "date".')
            if not isinstance(consider_filter, bool):
                raise ValueError('Param "consider_filter" for relevance date can only be boolean: True / False!')

    def _validate_file_type(self, file_type):
        if file_type not in SOURCE_TYPES:
            raise ValueError(f'Unknown file type: {file_type}. Allowed file types: '
                             f'"excel", "csv", "mssql", "mysql", "psql", "jdbc", "odbc".')

    def _validate_update_params(self, update_params, time_zones, file_type=None):
        """
        Проверка параметров обновления.
        :param update_params: параметры обновления
        :param file_type: тип файла, только для метода create_sphere.
        :param time_zones: временные зоны
        """
        update_type = update_params.get("type")
        if update_type not in UPDATE_TYPES:
            raise ValueError(f"Unknown update type: {update_type}")
        if file_type is not None and file_type in ("excel", "csv") and update_type != "ручное":
            raise ValueError(
                "For multispheres created from file sources, only full update is available!"
            )
        if update_type != "ручное":
            self._validate_schedule(
                update_params.get("schedule", list()), update_type, time_zones
            )
        if update_type == "по расписанию" and not update_params.get("schedule"):
            raise ValueError(
                "Update_params must include a schedule!"
            )


    @staticmethod
    def _validate_schedule(user_schedule, update_type, time_zones):
        """
        Проверка расписания.
        :param user_schedule: пользовательское расписание
        :param update_type: тип обновления
        :param time_zones: временные зоны
        """

        schedules = (
            user_schedule if isinstance(user_schedule, list) else [user_schedule]
        )
        for schedule in schedules:
            # проверка времени
            if "time" in schedule and not check_time(schedule["time"]):
                raise ValueError('Time "{}" has wrong format!'.format(schedule["time"]))
            # проверка часовой зоны
            if "time_zone" in schedule and schedule["time_zone"] not in time_zones:
                raise ValueError(
                    'Time zone "{}" does not exist!'.format(schedule["time_zone"])
                )
            # проверка периода
            if "type" in schedule and schedule["type"] not in UPDATE_PERIOD:
                raise ValueError(
                    'Update period "{}" not found!'.format(schedule["type"])
                )
            # проверка дня недели
            if "week_day" in schedule and schedule["week_day"] not in WEEK:
                raise ValueError(
                    'Wrong day of week: "{}"!'.format(schedule["week_day"])
                )
            # проверка номера дня в месяце
            if "day" in schedule and (schedule["day"] < 0 or schedule["day"] > 31):
                raise ValueError('Wrong date in month: "{}"!'.format(schedule["day"]))

    @staticmethod
    def _validate_increment_update(update_type, increment_dim):
        """
        Проверка инкрементального обновления.
        :param update_type: тип обновления
        :param increment_dim: инкрементальное измерение
        """
        if update_type == "инкрементальное" and not increment_dim:
            raise ValueError('Please enter "increment_dim" param!')

    @staticmethod
    def _validate_interval_update(
        update_type, interval_dim, user_interval, interval_borders
    ):
        """
        Проверка интервального обновления.
        :param update_type: тип обновления
        :param interval_dim: интервальное измерение
        :param user_interval: интервал обновлений
        :param interval_borders: границы интервала
        """
        if update_type == "интервальное":
            if not interval_dim:
                raise ValueError('Please enter "interval_dim" param!')
            if user_interval not in INTERVAL_MAP:
                raise ValueError(f'No such interval: "{user_interval}"')
            if user_interval == "с указанной даты":
                if len(interval_borders) < 1:
                    raise ValueError(
                        'For the current update interval parameter "interval_borders" must have at least one element!'
                    )
                _ = get_date(interval_borders[0], INTERVAL_BORDERS_DATE_FORMAT)
            if user_interval == "с и по указанную дату":
                if len(interval_borders) < 2:
                    raise ValueError(
                        'For the current update interval parameter "interval_borders" must have at least two elements!'
                    )
                if get_date(
                    interval_borders[0], INTERVAL_BORDERS_DATE_FORMAT
                ) > get_date(interval_borders[1], INTERVAL_BORDERS_DATE_FORMAT):
                    raise ValueError("Start date must be greater than end date!")

    @staticmethod
    def _validate_sql_params(file_type, sql_params):
        """
        Проверка параметров SQL.
        :param file_type: тип файла
        :param sql_params: параметры SQL
        """
        if (file_type != "excel") and (file_type != "csv"):
            if sql_params is None:
                raise ValueError(
                    'If your sourse is sql: fill in param "sql_params"!\n\n'
                    'In other cases: it is wrong param "file_type": %s\n\nIt can be only:\n'
                    "excel OR csv" % file_type
                )
            if not (
                {"server", "login", "passwd", "sql_query"} <= set(sql_params.keys())
            ):
                raise ValueError(
                    "Please check the following params names in sql_params:\n-server\n-login\n-passwd\n-sql_query"
                )

    @staticmethod
    def _validate_source_name(source_name):
        """
        Проверка имени источника.
        :param source_name: имя источника
        """
        if not 5 <= len(source_name) <= 100:
            raise ValueError("The source name must contain from 5 to 100 characters!")
        if not all(char in SOURCE_NAME_ALLOWED_CHARS for char in source_name.lower()):
            raise ValueError(
                "The source name may only contain Russian and English letters,"
                " numbers, space, '_', '-'"
            )

    def check_update_cube(
        self,
        cube_name,
        new_cube_name,
        cubes_list,
        update_params,
        user_interval,
        increment_dim,
        interval_dim,
        interval_borders,
        time_zones,
        relevance_date,
        indirect_cpu_load_parameter,
        filepath,
        encoding,
    ):
        """
        Проверка параметров функции update_cube.
        :param cube_name: имя куба
        :param new_cube_name: новое имя куба
        :param cubes_list: список кубов
        :param update_params: параметры обновления
        :param user_interval: интервал обновлений
        :param increment_dim: размерность для инкрементального обновления
        :param interval_dim: размерность для интервального обновления
        :param interval_borders: границы интервала
        :param time_zones: временные зоны
        :param relevance_date: параметры отображения даты актуальности данных
        :param indirect_cpu_load_parameter: параметры предельного процента использования CPU
        :param filepath: путь к новому файлу
        :param encoding: кодировка для csv-источника
        :return: tuple (cube_id, new_cube_name, indirect_cpu_load_parameter, new_file_type)
            new_file_type - тип нового загружаемого файла ("excel" или "csv")
        """
        # проверка куба на существование
        try:
            cube_id = self.bl.h.get_cube_id(cubes_list, cube_name)
        except ValueError as ex:
            raise ValueError(ex)

        if new_cube_name:
            # проверка, что новое название мультисферы уникально
            cubes_list = self.bl.get_cubes_list()
            new_cube_name = generate_unique_cube_name(new_cube_name, cubes_list)

            # проверка нового названия мультисферы на запрещенные символы
            check_cube_name(
                cube_name=new_cube_name, forbidden_chars=CUBE_NAME_FORBIDDEN_CHARS
            )

        # проверка заданного типа обновления и его параметров
        self._validate_update_params(update_params=update_params, time_zones=time_zones)

        # проверки инкрементального и интервального обновления
        update_type = update_params.get("type")
        self._validate_increment_update(update_type, increment_dim)
        self._validate_interval_update(
            update_type, interval_dim, user_interval, interval_borders
        )

        # проверка параметров даты актуальности данных
        self._validate_relevance_date(relevance_date)

        # проверка параметров предельного процента использования CPU
        indirect_cpu_load_parameter = self._validate_indirect_cpu_load_parameter(indirect_cpu_load_parameter)

        new_file_type = ""
        if filepath:
            new_file_type = self._validate_new_file_type(filepath)

            # проверка кодировки
            self._validate_encoding(new_file_type, encoding)

        self.bl.func_name = "update_cube"
        return cube_id, new_cube_name, indirect_cpu_load_parameter, new_file_type

    @staticmethod
    def _validate_new_file_type(filepath):

        new_file_format = os.path.splitext(filepath)[1].lstrip('.')
        if new_file_format == "":
            raise ValueError(f'The file path "{filepath}" must include '
                             f'the file extension, for example, ".csv".')

        elif new_file_format not in ("xls", "xlsx", "csv"):
            raise ValueError(f'Unknown file format: {new_file_format}. Allowed file formats: '
                             f'"xls", "xlsx", "csv".')

        return "excel" if new_file_format in ("xls", "xlsx") else "csv"

    def check_execute_olap_command(self):
        """
        Проверка параметров для функции execute_olap_command.
        :return: True, если проверка прошла успешно
        """
        if self.bl.multisphere_module_id == "":
            raise ValueError("First create cube and get data from it!")
        return True

    @staticmethod
    def check_load_sphere_chunk(units, convert_type, convert_empty_values):
        """
        Проверка параметров для функции load_sphere_chunk.
        :param units: единицы
        :param convert_type: конвертировать тип
        :param convert_empty_values: конвертировать пустые значения
        """
        is_int = False
        error_msg = 'Param "units" must be a positive integer number!'
        try:
            is_int = int(units) == float(units)
        except ValueError:
            raise ValueError(error_msg)
        if not is_int or int(units) <= 0:
            raise ValueError(error_msg)
        if not isinstance(convert_type, bool):
            raise ValueError('Param "convert_type" can only be boolean: True / False!')
        if not isinstance(convert_empty_values, bool):
            raise ValueError(
                'Param "convert_empty_values" can only be boolean: True / False!'
            )

    @staticmethod
    def check_set_measure_level(
        level: int, left_dims_count: int, top_dims_count: int, horizontal: bool
    ):
        """
        Проверка параметров для функции set_measure_level.
        :param level: уровень
        :param left_dims_count: количество левых размерностей
        :param top_dims_count: количество верхних размерностей
        :param horizontal: направление расчёта факта
        """
        error_msg = ""
        if horizontal and top_dims_count < 3:
            error_msg = "3 or more top dimensions must be taken out!"
        elif not horizontal and left_dims_count < 3:
            error_msg = "3 or more left dimensions must be taken out!"
        elif level <= 0:
            error_msg = 'Param "level" must be positive!'
        elif horizontal and level > top_dims_count - 1:
            error_msg = (
                f'Invalid "level" param! Max allowable value: {top_dims_count - 1}'
            )
        elif not horizontal and level > left_dims_count - 1:
            error_msg = (
                f'Invalid "level" param! Max allowable value: {left_dims_count - 1}'
            )
        if error_msg:
            raise ValueError(error_msg)

    @staticmethod
    def check_set_measure_select(measure_id, measure_name):
        """
        Проверка параметров для функции set_measure_select.
        :param measure_id: ID меры
        :param measure_name: имя меры
        """
        if not measure_id and not measure_name:
            raise ValueError(
                "Need to specify either measure identifier or measure name!"
            )

    @staticmethod
    def check_set_all_measure_visibility(is_visible):
        """
        Проверка параметров для функции set_all_measure_visibility.
        :param is_visible: видимость
        :return: True, если проверка прошла успешно
        """
        if not isinstance(is_visible, bool):
            raise ValueError('Param "is_visible" can only be boolean: True / False')
        return True

    @staticmethod
    def check_set_measure_direction(is_horizontal):
        """
        Проверка параметров для функции set_measure_direction.
        :param is_horizontal: горизонтальное направление
        """
        if is_horizontal not in [True, False]:
            raise ValueError('Param "is_horizontal" must be "True" or "False"!')

    @staticmethod
    def check_get_scenario_metadata(script_id):
        """
        Проверка параметров для функции get_scenario_metadata.
        :param script_id: ID сценария
        """
        if not isinstance(script_id, str):
            raise ValueError('Param "script_id" must be "str" type!')
        if not script_id:
            raise ValueError('Param "script_id" not set!')

    @staticmethod
    def check_reset_filters(dimensions):
        """
        Проверка параметров для функции reset_filters.
        :param dimensions: измерения
        :return: список измерений
        """
        if isinstance(dimensions, str):
            return [dimensions] if dimensions else []
        elif isinstance(dimensions, (list, tuple)):
            return dimensions
        else:
            raise ValueError(
                'Param "dimensions" must be "str", "list" or "tuple" type!'
            )

    @staticmethod
    def check_get_cube_info(cube):
        """
        Проверка параметров для функции get_cube_info.
        :param cube: куб
        """
        if not isinstance(cube, str):
            raise ValueError('Param "cube" must be "str" type!')

    @staticmethod
    def check_clone_olap_module(module, set_focus_on_copied_module, copied_module_name):
        """
        Проверка параметров для функции clone_olap_module.
        :param module: модуль
        :param set_focus_on_copied_module: установить фокус на скопированный модуль
        :param copied_module_name: имя скопированного модуля
        """
        if not isinstance(module, str):
            raise ValueError('Param "module" must be "str" type!')
        if not isinstance(set_focus_on_copied_module, bool):
            raise ValueError('Param "set_focus_on_copied_module" must be "bool" type!')
        if not isinstance(copied_module_name, str):
            raise ValueError('Param "copied_module_name" must be "str" type!')

    def check_create_calculated_measure(self, measure_name, formula):
        """
        Проверка параметров для функции create_calculated_measure.
        :param measure_name: имя меры
        :param formula: формула
        """
        self._check_type_and_value(measure_name, "new_name")
        self._check_type_and_value(formula, "formula")
        self._check_new_name_param(measure_name)

    @staticmethod
    def _check_type_and_value(param_value: str, param_name: str):
        """
        Проверка типа и значения заданного параметра.
        :param param_value: значение параметра
        :param param_name: имя параметра
        """
        if not isinstance(param_value, str):
            raise ValueError(f'Param "{param_name}" must be "str" type!')
        if not param_value:
            raise ValueError(f'Param "{param_name}" has empty value!')

    @staticmethod
    def _check_new_name_param(measure_name: str):
        """
        Проверка имени создаваемого вычислимого факта на соответствие с названиями функций и логических операндов.
        :param measure_name: имя меры
        """
        lower_measure_name = measure_name.lower()
        if (
            lower_measure_name in FUNCS
            or lower_measure_name in LOGIC_FUNCS
            or lower_measure_name == "if"
        ):
            raise ValueError(
                f'Value "{measure_name}" of "new_name" parameter is invalid!'
            )

    @staticmethod
    def check_group_dimensions(group_name, items, position):
        """
        Проверка параметров для функции group_dimensions.
        :param group_name: имя группы
        :param items: элементы
        :param position: позиция
        """
        # check "group_name" param
        if not isinstance(group_name, str):
            raise ValueError('Param "group_name" must be "str" type!')
        if not group_name:
            raise ValueError('Group name cannot be empty (param "group_name")!')
        # check items
        if not isinstance(items, (list, set, tuple)):
            raise ValueError('Param "dim_items" must be "list", "set" or "tuple" type!')
        # check position
        if position not in ["left", "top"]:
            raise ValueError('Param "position" must be either "left" or "top"!')

    @staticmethod
    def check_wait_cube_loading(cube_name, time_sleep, max_attempt):
        """
        Проверка параметров для функции wait_cube_loading.
        :param cube_name: имя куба
        :param time_sleep: время ожидания
        :param max_attempt: максимальное количество попыток
        """
        # check cube_name
        if not isinstance(cube_name, str):
            raise ValueError('Param "cube_name" must be "str" type!')
        # check time_sleep
        if not isinstance(time_sleep, int):
            raise ValueError('Param "time_sleep" must be "int" type!')
        if time_sleep < 1:
            raise ValueError('Value of "time_sleep" param must be greater than 0!')
        # check max_attempt
        if max_attempt is not None and not isinstance(max_attempt, int):
            raise ValueError('Param "max_attempt" must be "int" type or None!')
        if isinstance(max_attempt, int) and max_attempt < 1:
            raise ValueError('Value of "max_attempt" param must be greater than 0!')

    @staticmethod
    def check_create_consistent_dim(separator):
        if separator not in ("*", "-", ",", " "):
            raise ValueError('Param "separator" must be "*", "-", "," or " "!')
