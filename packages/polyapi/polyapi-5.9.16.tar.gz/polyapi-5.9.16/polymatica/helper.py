#!/usr/bin/python3
""" Содержит вспомогательные (служебные) методы, использующиеся в основном модуле работы с Полиматикой """

import time
from datetime import datetime
from itertools import count
from typing import Any, List, Tuple

from polymatica.common import FUNCS, MEASURE_STR_INT_TYPES_MAP, raise_exception
from polymatica.exceptions import ParseError, PolymaticaException, ScenarioError


class Helper:
    def __init__(self, sc):
        """
        Инициализация вспомогательного класса.
        :param sc: экземпляр класса BusinessLogic
        """
        self.sc = sc
        # хранит функцию-генератор исключений
        self._raise_exception = raise_exception(self.sc)

    def get_cube_id(self, cubes_list: List, cube_name: str) -> str:
        """
        Получить id мультисферы (куба).
        :param cubes_list: список мультисфер
        :param cube_name: название мультисферы
        :return: id мультисферы
        """
        for cube in cubes_list:
            if cube["name"] == cube_name:
                return cube["uuid"]
        return self._raise_exception(
            ValueError,
            f'No such cube "{cube_name}" in cubes list!',
            with_traceback=False,
        )

    def get_measure_or_dim_id(
        self, multisphere_data: dict, measure_dim: str, name
    ) -> str:
        """
        Получить id факта/размерности по имени.
        :param multisphere_data: рабочая область мультисферы
        :param measure_dim: "facts" / "dimensions"
        :param name: название размерности / факта
        :return: id размерности / факта
        """
        for item in multisphere_data[measure_dim]:
            if item["name"].rstrip() == name.rstrip():
                return item["id"]
        error_msg = f'No such {measure_dim[:-1]}: "{name}"'
        return self._raise_exception(
            ValueError,
            error_msg,
            with_traceback=False,
        )

    def get_dim_id(self, multisphere_data: dict, name: str, cube_name: str) -> str:
        """
        Получить идентификатор размерности по её названию.
        :param multisphere_data: рабочая область мультисферы.
        :param name: название размерности.
        :param cube_name: название текущей мультисферы.
        :return: Идентификатор размерности.
        """
        for item in multisphere_data["dimensions"]:
            if item.get("name", "").rstrip() == name.rstrip():
                return item.get("id")
        error_msg = (
            f'Dimension name "{name}" is not valid for Multisphere "{cube_name}"!'
        )
        return self._raise_exception(ValueError, error_msg, with_traceback=False)

    def get_measure_id(self, multisphere_data: dict, name: str, cube_name: str) -> str:
        """
        Получить идентификатор факта по его названию.
        :param multisphere_data: информация по рабочей области мультисферы.
        :param name: название факта.
        :param cube_name: название текущей мультисферы.
        :return: идентификатор факта.
        """
        # поиск идентификатора факта по его названию
        name = name.strip()
        for item in multisphere_data.get("facts"):
            if item.get("name").strip() == name:
                return item.get("id")
        # если не найдено ничего - бросаем ошибку
        error_msg = f'Measure name "{name}" is not valid for Multisphere "{cube_name}"'
        return self._raise_exception(
            PolymaticaException, error_msg, with_traceback=False
        )

    def get_measure_or_dim_name_by_id(self, id_: str, type_: str) -> str:
        """
        Получить название факта/размерности по идентификатору.
        :param id_: (str) идентификатор факта/размерности.
        :param type_: (str) принимает одно из значений: "facts" или "dimensions".
        :return: (str) название факта/размерности.
        """
        # проверка
        if self.sc.multisphere_module_id == "":
            return self._raise_exception(
                ValueError,
                "First create cube and get data from it!",
                with_traceback=False,
            )

        # получить словать с размерностями, фактами и данными
        self.sc.get_multisphere_data()

        # поиск нужного имени
        data = self.sc.multisphere_data.get(type_)
        for item in data:
            if item.get("id") == id_:
                return item.get("name")
        error_msg = 'No {} with id "{}" in the multisphere!'.format(
            "measure" if type_ == "facts" else "dimension", id_
        )
        return self._raise_exception(
            PolymaticaException, error_msg, with_traceback=False
        )

    def get_measure_type(self, name: str) -> int:
        """
        Возвращает целочисленный вид факта по его строковому названию. При передаче неверного строкового вида факта
        будет сгенерирована ошибка.
        :param name: (str) вид факта (в строковом представлении)
        :return: (int) целочисленный вид факта.
        """
        if name not in MEASURE_STR_INT_TYPES_MAP:
            return self._raise_exception(
                ValueError,
                f"No such measure type: {name}",
                with_traceback=False,
            )
        return MEASURE_STR_INT_TYPES_MAP[name]

    def parse_formula(self, formula: str) -> List:
        """
        Парсинг формулы для создания вычислимого факта.
        Разбивает исходную формулу на составляющие, при этом склеивая названия фактов, содержащие пробелы.
        Примеры:
            1. "5 + [Сумма&Март] * 2 + corr([Сумма];[ID])" ->
                ["5", "+", "[Сумма&Март]", "*", "2", "+", "corr([Сумма];[ID])"]
            2. "top([Сумма по всем отделам]; 10) >= 94" -> ["top([Сумма по всем отделам]; 10)", ">=", "94"]
        :param formula: (str) исходная формула.
        :return: (List) составляющие исходной формулы.
        """
        splitted_formula = formula.split()
        result = []
        in_func, in_measure, func_parts, measure_parts = False, False, list(), list()

        for formula_part in splitted_formula:
            # является ли текущая часть формулы функцией
            if not in_func:
                for logic_func in FUNCS:
                    if f"{logic_func}(" in formula_part:
                        in_func = True
            if in_func:
                func_parts.append(formula_part)
                if ")" in formula_part:
                    result.append(" ".join(func_parts))
                    in_func, func_parts = False, list()
                continue

            # является ли текущая часть формулы фактом
            if not in_measure:
                if "[" in formula_part:
                    in_measure = True
            if in_measure:
                measure_parts.append(formula_part)
                if "]" in formula_part:
                    result.append(" ".join(measure_parts))
                    in_measure, measure_parts = False, list()
                continue

            # всё остальное (операнды, числа) добавляем безо всяких преобразований
            result.append(formula_part)
        return result

    def get_scenario_id_by_name(
        self, script_descs: dict, scenario_name: str, scenario_path: str = None
    ) -> str:
        """
        Получение идентификатор сценария по его имени.
        :param script_descs: (dict) данные по всем сценариям.
        :param scenario_name: (str) название сценария.
        :param scenario_path: (str) путь сценария (необязательный параметр).
        :return: идентификатор сценария
        """
        for script in script_descs:
            if script.get("name") == scenario_name and (
                not scenario_path
                or (scenario_path and script.get("path") == scenario_path)
            ):
                return script.get("id")
        return self._raise_exception(
            ScenarioError,
            'Scenario named "{}" not found!'.format(scenario_name),
            with_traceback=False,
        )

    def get_scenario_name_by_id(self, script_descs: dict, scenario_id: str) -> str:
        """
        Получение идентификатор сценария по его имени.
        :param script_descs: (dict) данные по всем сценариям.
        :param scenario_id: (str) идентификатор сценария.
        :return: название сценария
        """
        for script in script_descs:
            if script.get("id") == scenario_id:
                return script.get("name")
        return self._raise_exception(
            ScenarioError,
            'Scenario with id "{}" not found!'.format(scenario_id),
            with_traceback=False,
        )

    def wait_scenario_layer_loaded(self, sc_layer: str) -> Tuple:
        """
        Ожидание загрузки слоя с заданным сценарием.
        :param sc_layer: (str) идентификатор слоя с запускаемым сценарием.
        :return: (Tuple) количество обращений к серверу для получения текущего статуса, число законченных шагов.
        """
        need_check_progress, count_of_requests = True, 0
        while need_check_progress:
            # периодичностью раз в полсекунды запрашиваем результат с сервера и проверяем статус загрузки слоя
            # если не удаётся получить статус - скорее всего нет ответа от сервера - сгенерируем ошибку
            # в таком случае считаем, что сервер не ответил и генерируем ошибку
            time.sleep(0.5)
            count_of_requests += 1
            try:
                progress = self.sc.execute_manager_command(
                    command_name="script", state="run_progress", layer_id=sc_layer
                )
                status = self.parse_result(result=progress, key="status") or {}
                status_code, status_message = status.get("code", -1), status.get(
                    "message", "Unknown error!"
                )
            except Exception:
                # если упала ошибка - не удалось получить ответ от сервера: возможно, он недоступен
                return self._raise_exception(
                    ScenarioError,
                    "Failed to load script! Possible server is unavailable.",
                )

            # проверяем код статуса
            if status_code == 206:
                # сценарий в процессе воспроизведения
                need_check_progress = True
            elif status_code == 207:
                # сценарий полностью выполнен
                need_check_progress = False
            elif status_code == 208:
                # ошибка: сценарий остановлен пользователем (довольно редкий случай)
                return self._raise_exception(
                    ScenarioError,
                    "Script loading was stopped by user!",
                    with_traceback=False,
                )
            elif status_code == -1:
                # ошибка: не удалось получить код текущего статуса
                return self._raise_exception(
                    ScenarioError, "Unable to get status code!", with_traceback=False
                )
            else:
                # прочие ошибки
                return self._raise_exception(
                    ScenarioError, status_message, with_traceback=False
                )
        return count_of_requests, self.parse_result(
            result=progress, key="finished_steps_count"
        )

    def parse_result(
        self, result: dict, key: str, nested_key: str = None, default_value: Any = None
    ) -> Any:
        """
        Парсит и проверяет на ошибки ответ в виде ['queries'][0]['command']['значение']['необязательное значение'].
        :param result: (dict) нераспарсенный ответ от API.
        :param key: (str) ключ, значение которого нужно распарсить.
        :param nested_key: (str) вложенный ключ, значение которого нужно распарсить.
        :param default_value: (Any) значение по-умолчанию для ключа в случае, если этот ключ отсутствует;
            если при отсутствующем ключе данный параметр не будет задан, то будет сгенерирована ошибка.
        :return: (Any) Значение заданного поля.
        """
        base_error_msg = "Error while parsing response: ['queries'][0]['command']"
        request_queries = next(iter(result.get("queries")))
        request_command = request_queries.get("command")

        if key not in request_command:
            if default_value is None:
                error_msg = f"{base_error_msg}['{key}']"
                return self._raise_exception(
                    ParseError, error_msg, with_traceback=False
                )
            value = default_value
        else:
            value = request_command.get(key)

        if nested_key is not None:
            if not isinstance(value, dict):
                error_msg = f"{base_error_msg}['{key}'] is not dict!"
                return self._raise_exception(
                    ParseError, error_msg, with_traceback=False
                )
            if nested_key not in value:
                error_msg = f"{base_error_msg}['{key}']['{nested_key}']"
                return self._raise_exception(
                    ParseError, error_msg, with_traceback=False
                )
            return value.get(nested_key)

        return value

    def get_rows_cols(self, num_row: int = None, num_col: int = None) -> dict:
        """
        Загрузить строки и колонки мультисферы
        :param num_row: (int) количество строк мультисферы
        :param num_col: (int) количество колонок мультисферы
        :return: (dict) command_name="view", state="get_2"
        """
        if (num_row is not None) and (num_col is not None):
            return self.sc.execute_olap_command(
                command_name="view",
                state="get_2",
                from_row=0,
                from_col=0,
                num_row=num_row,
                num_col=num_col,
            )

        # 1000, 2000, 3000, ...
        gen = count(1000, 1000)

        prev_data = []

        result = self.sc.execute_olap_command(
            command_name="view",
            state="get_2",
            from_row=0,
            from_col=0,
            num_row=next(gen),
            num_col=next(gen),
        )
        data = self.parse_result(result=result, key="data")

        while len(prev_data) < len(data):
            prev_data = data
            result = self.sc.execute_olap_command(
                command_name="view",
                state="get_2",
                from_row=0,
                from_col=0,
                num_row=next(gen),
                num_col=next(gen),
            )
            data = self.parse_result(result=result, key="data")
        return result

    def get_pretty_size(
        self, num_bytes: int, presicion: int = 1, units_lang: str = "ru"
    ) -> str:
        """
        Перевод значения в байтах в более крупные единицы измерения.
        :param num_bytes: (int) исходный размер в байтах.
        :param presicion: (int) точность; количество знаков после запятой; по-умолчанию 1.
        :param units_lang: (str) язык отображения размерностей; доступны варианты "ru", "en".
        :return: (str) человеко-читабельная запись исходного размера в байтах; например: "3.5 MB", "7 bytes".
        """
        if units_lang == "ru":
            units = ["байт", "Кбайт", "Мбайт", "Гбайт", "Тбайт"]
        elif units_lang == "en":
            units = ["bytes", "kB", "MB", "GB", "TB"]
        else:
            raise ValueError('Wrong "units_lang" param: "{}"! Available: "ru", "en".')

        len_units = len(units)
        # предел; число, после которого единицы измерения переходят на уровень выше
        threshold = 1024
        for i in range(0, len_units):
            if num_bytes < threshold:
                return f"{num_bytes:g} {units[i]}"
            if i == len_units - 1:
                break
            num_bytes = round(num_bytes / threshold, presicion)
        return f"{num_bytes:g} {units[-1]}"

    def get_datetime_from_timestamp(
        self, timestamp: int, mask: str = r"%d.%m.%Y %H:%M"
    ) -> str:
        """
        Получение даты-времени в человеко-читаемом виде из исходного числа секунд (таймстампа).
        :param timestamp: (int) количество секунд.
        :param mask: (str) маска перевода в формат даты-времени.
        :return: (str) значение даты-времени в человеко-читаемом виде.
        """
        return datetime.fromtimestamp(int(timestamp / 10**6)).strftime(mask)

    def get_filter_rows(self, dim_id: str) -> dict:
        """
        Загрузить строки и колонки мультисферы
        :param dim_id: (str) id размерности
        :return: (dict) command_name="view", state="get_2"
        """

        # 1000, 2000, 3000, ...
        gen = count(1000, 1000)

        prev_data = []

        result = self.sc.execute_olap_command(
            command_name="filter",
            state="pattern_change",
            dimension=dim_id,
            pattern="",
            # кол-во значений отображается на экране, после скролла их становится больше:
            # num=30
            num=next(gen),
        )

        data = self.parse_result(result=result, key="data")

        while len(prev_data) < len(data):
            prev_data = data
            result = self.sc.execute_olap_command(
                command_name="filter",
                state="pattern_change",
                dimension=dim_id,
                pattern="",
                # кол-во значений отображается на экране, после скролла их становится больше:
                # num=30
                num=next(gen),
            )
            data = self.parse_result(result=result, key="data")
        return result

    def get_source_type(self, file_type: str) -> int:
        """
        Метод для получения параметра source_type по file_type. Используется
        в методе create_sphere.
        """
        return self.sc.server_codes["manager"]["data_source_type"][file_type]

    def get_file_type(self, source_type: int) -> str:
        """
        Метод для получения параметра file_type по source_type. Используется
        в методе update_cube.
        """
        data_source_type = self.sc.server_codes["manager"]["data_source_type"]
        return next((k for k, v in data_source_type.items() if v == source_type), None)

    def upload_file_to_server(self, filepath: str):
        """
        Метод для загрузки файла типа excel или csv на сервер. Используется
        в методах create_sphere, update_cube.
        """
        try:
            response = self.sc.exec_request.execute_request(
                params=filepath, method="PUT"
            )
        except Exception as e:
            return self.sc._raise_exception(PolymaticaException, str(e))
        if response.status_code == 200:
            encoded_file_name = response.headers["File-Name"]
            return encoded_file_name
        else:
            return self.sc._raise_exception(
                PolymaticaException,
                f"Unable to get file id from server! URL: {response.url}, STATUS_CODE: {response.status_code}",
                with_traceback=False,
            )

    def get_and_process_dims_and_measures(self, response: dict, file_type: str = None):
        """
        Метод для получения и обработки словарей с размерностями и фактами в методах
        create_sphere, update_cube.
        """
        dims = self.parse_result(result=response, key="dims")
        measures = self.parse_result(result=response, key="facts")
        for i in dims:
            i.update({"field_type": "field"})
            if file_type == "csv":
                self.sc.checks("check_bom_in_dims_and_measures", i)
        for i in measures:
            i.update({"field_type": "field"})
            if file_type == "csv":
                self.sc.checks("check_bom_in_dims_and_measures", i)
        return dims, measures
