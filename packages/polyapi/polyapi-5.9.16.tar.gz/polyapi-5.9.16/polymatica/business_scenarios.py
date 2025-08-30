#!/usr/bin/python3
"""
Модуль работы с бизнес-сценариями Полиматики.
"""
# Default lib

import ast
import copy
import datetime
import json
import logging
import os
import re
import time
from collections import Counter
from logging import NullHandler
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin

import pandas as pd
import requests

# Polymatica imports
from polymatica.authorization import Authorization
from polymatica.commands import GraphCommands, ManagerCommands, OlapCommands
from polymatica.common import (
    ALL_PERMISSIONS,
    API_VERSION,
    CODE_NAME_MAP,
    DB_SOURCE_TYPES,
    DEFAULT_POLYMATICA_VERSION,
    EMPTY_ID,
    FORMAT_SETTINGS_KEYS,
    GRAPH_ID,
    INTERVAL_MAP,
    ISO_DATE_FORMAT,
    LOGIC_FUNCS,
    MEASURE_INT_STR_TYPES_MAP,
    MIN_MEASURE_CELL_WIDTH,
    MIN_OLAP_WIDTH,
    MULTISPHERE_ID,
    OPERANDS,
    POLYMATICA_INT_TYPES_MAP,
    POLYMATICA_TYPES_INT_MAP,
    POSITION_MAP,
    ROOT_PARENT,
    TYPES_MAP,
    UNITS_LOAD_DATA_CHUNK,
    UPDATE_PERIOD,
    TypeConverter,
    json_type,
    log,
    raise_exception,
    request_with_undefined_suffix_url,
    timing,
)
from polymatica.common.helper_funcs import generate_unique_layer_name, validate_params
from polymatica.common.params_models import (
    CleanUpParams,
    CreateConsistentDimParams,
    CreateLayerParams,
    CreateSphereParams,
    DeleteDimFilterParams,
    GetMeasuresParams,
    RenameDimsParams,
    SetMeasuresParams,
    SetMeasureVisibilityParams,
    UpdateCubeParams,
)
from polymatica.error_handler import Validator
from polymatica.exceptions import (
    AuthError,
    CubeError,
    CubeNotFoundError,
    DBConnectionError,
    ExportError,
    FilterError,
    GraphCommandError,
    GraphError,
    ManagerCommandError,
    OLAPCommandError,
    OLAPModuleNotFoundError,
    PolymaticaException,
    RightsError,
    ScenarioError,
    UserNotFoundError,
)
from polymatica.executor import Executor
from polymatica.graph import IGraph
from polymatica.helper import Helper

# ----------------------------------------------------------------------------------------------------------------------

# настройка логирования
logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())


# ----------------------------------------------------------------------------------------------------------------------


class BusinessLogic:
    """
    Базовый класс, описывающий бизнес-сценарии использования Полиматики.
    Используемые переменные класса:

    # Флаг работы в Jupiter Notebook
    self.jupiter

    # Флаг гостевого пользователя при беспарольной авторизации
    self.is_guest

    # Текст ошибки присваивается в случае аварийного завершения работы; может быть удобно при работе в Jupiter Notebook
    self.current_exception

    # Версия сервера Полиматики; например, '5.9'
    self.polymatica_version

    # Полная версия сервера Полиматики; например, '5.9.11-de4488b5'
    self.full_polymatica_version

    # Язык интерфейса. Задается во время авторизации. Возможно задать следующие значения: "ru", "en".
    # По-умолчанию "ru"
    self.language

    # Базовый URL стенда Полиматики (тот, что передаётся в конструктор при инициализации класса)
    self.base_url

    # Таймаут выполнения запросов
    self.timeout

    # Логин пользователя Полиматики
    self.login

    # Для измерения времени работы функций бизнес-логики
    self.func_timing

    # Таблица команд и состояний
    self.server_codes

    # Идентификатор активного OLAP-модуля (мультисферы)
    self.multisphere_module_id

    # Идентификатор куба, соответствующего активному OLAP-модулю
    self.cube_id

    # Название куба, соответствующего активному OLAP-модулю
    self.cube_name

    # Список идентификаторов всех слоёв
    self.layers_list

    # Идентификатор активного слоя
    self.active_layer_id

    # Данные мультисферы в формате {"dimensions": "", "facts": "", "data": ""}
    self.multisphere_data

    # Общее число строк текущего (активного) OLAP-модуля
    self.total_row

    # Идентификатор активного модуля графиков
    self.graph_module_id

    # URL стенда Полиматики, использующийся для вызова серверных команд
    self.command_url

    # URL стенда Полиматики для обращения к ресурсам
    self.resources_url

    # Идентификатор сессии
    self.session_id

    # Идентификатор (uuid) авторизации
    self.authorization_uuid

    # Класс, выполняющий HTTP-запросы
    self.exec_request

    # Объект выполнения команд модуля Manager
    self.manager_command

    # Объект выполнения команд модуля OLAP
    self.olap_command

    # Объект выполнения команд модуля Graph
    self.graph_command

    # Helper class
    self.h

    # Сохранённое имя функции для избежания конфликтов с декоратором
    self.func_name

    # Содержимое DataFrame
    self.df

    # Колонки DataFrame
    self.df_cols

    """

    def __init__(
        self,
        login: str,
        url: str,
        password: str = None,
        session_auth: Optional[dict] = None,
        is_guest: bool = False,
        timeout: float = 60.0,
        jupiter: bool = False,
        language: str = "ru",
        suffixes_url: List = None,
        script_mode: bool = False
    ):
        """
        Инициализация класса BusinessLogic.
        :param login: логин пользователя Полиматика.
        :param url: URL стенда Полиматика.
        :param password: (необязательный) пароль пользователя Полиматика.
        :param session_auth: (необязательный) идентификаторы сессии:
            {'session_id': "...",
             'manager_uuid': "...",
             'full_polymatica_version': "..."
            }.
        :param is_guest: (необязательный) гостевой доступ при беспарольной авторизации; по-умолчанию False.
        :param timeout: (необязательный) таймаут выполнения запросов, по-умолчанию 60 секунд.
        :param jupiter: (необязательный) запускается ли скрипт из Jupiter Notebook, по-умолчанию False.
        :param language: (необязательный) язык локализации; возможны значения: "ru"/"en"/"de"/"fr"; по-умолчанию "ru".
        :param suffixes_url: (необязательный) список возможных суффиксов URL-адреса стенда Полиматики;
            рекомендуется не задавать этот параметр без острой на то необходимости.
        :param script_mode: (необязательный) используется ли класс BusinessLogic для специального скрипта,
            по умолчанию False, внутренний параметр.
        """
        # logger
        self.logger = logger
        self.logger.info("BusinessLogic init")

        # флаг работы в Jupiter Notebook
        self.jupiter = jupiter

        # флаг гостевого пользователя при беспарольной авторизации
        self.is_guest = is_guest

        # текст ошибки присваивается в случае аварийного завершения работы;
        # может быть удобно при работе в Jupiter Notebook
        self.current_exception = ""

        # хранит функцию-генератор исключений
        self._raise_exception = raise_exception(self)

        # версия сервера Полиматики
        self.polymatica_version = DEFAULT_POLYMATICA_VERSION

        # полная версия сервера Полиматики; по-умолчанию мы её не заполняем, а потом подтягиваем во время авторизации
        # необходим для нужд пользователей
        self.full_polymatica_version = ""

        # язык, возможны варианты: "ru", "en", "de" или "fr"
        self.language = language

        # базовый URL стенда Полиматики (тот, что передаётся в конструктор при инициализации класса)
        self.base_url = self._get_prepare_url(url)

        # таймаут выполнения запросов
        self.timeout = timeout

        # логин пользователя Полиматики
        self.login = login

        # для измерения времени работы функций бизнес-логики
        self.func_timing = ""

        # таблица команд и состояний
        self.server_codes = Executor.get_server_codes(self.base_url)

        # переменные, хранящие текущую конфигурацию
        # идентификатор активного OLAP-модуля (мультисферы)
        self.multisphere_module_id = ""
        # идентификатор куба, соответствующего активному OLAP-модулю
        self.cube_id = ""
        self.cube_name = ""  # название куба, соответствующего активному OLAP-модулю
        self.layers_list = list()  # список идентификаторов всех слоёв
        self.active_layer_id = ""  # идентификатор активного слоя
        # данные мультисферы в формате {"dimensions": "", "facts": "", "data": ""}
        self.multisphere_data = dict()
        self.total_row = 0  # общее число строк текущего (активного) OLAP-модуля
        self.graph_module_id = ""  # идентификатор активного модуля графиков

        if not suffixes_url:
            suffixes_url = ["", "api/v1"]

        # авторизация на сервере Полиматики, если задан логин и пароль
        # в методе _login инкапсулирована инициализация следующих переменных:
        # self.session_id, self.authorization_uuid, self.full_polymatica_version, self.polymatica_version
        if session_auth:
            self.session_id = session_auth.get("session_id")
            self.authorization_uuid = session_auth.get("manager_uuid")
            self.full_polymatica_version = session_auth.get("full_polymatica_version")
            self.polymatica_version = self._get_polymatica_version(
                self.full_polymatica_version or ""
            )
            # проверка подключения к аналитике
            suffix_url = self._check_connection(suffixes_url)
        elif login:
            suffix_url = self._login(password, suffixes_url)

        else:
            raise ValueError(
                "Set login with password or session params: "
                "'session_id', 'manager_uuid' and 'full_polymatica_version'"
            )

        # получаем все необходимые урлы (URL для API-запросов, URL для ресурсов)
        self.command_url, self.resources_url = self._get_urls(suffix_url)

        # класс, выполняющий HTTP-запросы
        self.exec_request = Executor(
            self.session_id,
            self.authorization_uuid,
            self.base_url,
            self.command_url,
            timeout,
            self.polymatica_version,
        )

        # инициализация модуля Manager
        self.manager_command = ManagerCommands(
            self.session_id, self.authorization_uuid, self.server_codes, self.jupiter
        )

        # инициализация модуля Olap
        # ВАЖНО! OLAP модуль базируется на конкретной (активной) мультисфере, поэтому после переключения фокуса
        # на другую мультисферу (т.е. после того, как стала активна другая мультисфера)
        # необходимо заново инициализировать OLAP-модуль
        self.set_multisphere_module_id(self.multisphere_module_id)

        # инициализация модуля графиков
        # ВАЖНО! модуль графиков базируется на конкретном (активном) графике, поэтому после переключения фокуса
        # на другой график (т.е. после того, как стал активен другой график)
        # необходимо заново инициализировать этот модуль
        self._set_graph_module_id(self.graph_module_id)

        # helper
        self.h = Helper(self)

        # экземпляр класса Validator для проверки методов BusinessLogic
        self.validator = Validator(self)

        # сохранённое имя функции для избежания конфликтов с декоратором
        self.func_name = ""

        # если пользователь задан свой идентификатор сессии - получаем начальные данные
        if session_auth and not (login and password):
            self._get_initial_config()

        # DataFrame content, DataFrame columns
        self.df, self.df_cols = "", ""

        # хранит информацию о количестве копий указанных OLAP-модулей
        self._copied_counter = Counter()

        # хранит информацию об именах клонируемых OLAP-модулей
        self._copied_names = dict()

        # загружаем конфиг
        self.config = self._get_interface_config()

        self.API_VERSION = API_VERSION
        self.ROOT_PARENT = ROOT_PARENT
        self.script_mode = script_mode

    def checks(self, func_name: str, *args):
        """
        Реализация проверок методов BusinessLogic
        """
        return self.validator.validate(func_name, *args)

    @property
    def copied_counter(self) -> int:
        """
        Возвращает количество копий указанных OLAP-модулей.
        """
        return self._copied_counter

    @copied_counter.setter
    def set_counter(self, olap_module_id: str):
        """
        Увеличение счётчика копий указанного OLAP-модуля.
        :param olap_module_id: (str) идентификатор OLAP-модуля.
        """
        self._copied_counter.update({olap_module_id: 1})

    @property
    def copied_names(self) -> dict:
        """
        Возвращает словарь с информацией об именах клонируемых OLAP-модулей
        """
        return self._copied_names

    @copied_names.setter
    def set_copied_names(self, module_data: tuple):
        """
        Добавление имени копируемого модуля в общий скоп имён.
        :param module_data: (tuple) кортеж, содержащий идентификатор и заданное название копируемого OLAP-модуля.
        """
        olap_module_id, name = module_data[0], module_data[1]
        if olap_module_id in self._copied_names:
            self._copied_names[olap_module_id].add(name)
        else:
            self._copied_names.update({olap_module_id: {name}})

    def __str__(self):
        # вернём ссылку на просмотр сессии в интерфейсе
        return f"{self.base_url}login?login={self.login}&session_id={self.session_id}"

    def _get_prepare_url(self, url: str) -> str:
        """
        Удаление лишних слешей на конце URL-адреса стенда Полиматики.
        По итогу, в конце URL-адреса должен остаться один слеш.
        :param url: (str) URL-адрес стенда Полиматики.
        :return: (str) базовый URL стенда Полиматики.
        """
        if not url:
            return self._raise_exception(PolymaticaException, "URL address not set!")
        while url and url[-1] == "/":
            url = url[:-1]
        return f"{url}/"

    def _get_urls(self, suffix_url: str) -> Tuple[str, str]:
        """
        Формирует и возвращает все необходимые URL-адреса для работы с Полиматикой.
        :param suffix_url: (str) окончание текущего URL-адреса Полиматики.
        :return: (str) основной URL-адрес стенда Полиматики, использующийся для вызова серверных команд.
        :return: (str) URL-адрес для получения ресурсов.
        """
        return (
            f"{self.base_url}{suffix_url}",
            f"{self.base_url}resources",
        )

    def set_multisphere_module_id(self, module_id: str):
        """
        Установка идентификатора новой активной мультисферы. После смены активной мультисферы происходит
        переинициализация объекта, исполняющего OLAP команды.
        :param module_id: идентификатор мультисферы.
        """
        self.multisphere_module_id = module_id
        self.olap_command = OlapCommands(
            self.session_id, self.multisphere_module_id, self.server_codes, self.jupiter
        )

    def _set_graph_module_id(self, module_id: str):
        """
        Установка идентификатора нового активного графика. После смены активного графика происходит
        переинициализация объекта, исполняющего команды модуля Graph.
        :param module_id: идентификатор активного модуля графиков.
        """
        self.graph_module_id = module_id
        self.graph_command = GraphCommands(
            self.session_id, self.graph_module_id, self.server_codes, self.jupiter
        )

    @timing
    def _login(self, password: str, suffixes_url: List) -> str:
        """
        Авторизация на сервере Полиматики.
        :param password: (str) пароль авторизации.
        :param suffixes_url: (List) список возможных суффиксов URL-адреса стенда Полиматики.
        :return: (str) окончание URL-адреса, определённое в ходе авторизации.
        """
        try:
            (
                self.session_id,
                self.authorization_uuid,
                polymatica_version,
                suffix_url,
            ) = Authorization().login(
                user_name=self.login,
                base_url=self.base_url,
                server_codes=self.server_codes,
                timeout=self.timeout * 2,
                language=(self.language or "ru").lower(),
                suffixes_url=suffixes_url,
                is_guest=self.is_guest,
                password=password,
            )
            self.full_polymatica_version = polymatica_version
            self.polymatica_version = self._get_polymatica_version(
                polymatica_version or ""
            )
            self.logger.info("Login success")
            return suffix_url
        except AssertionError as ex:
            error_info = ex.args[0]
            if isinstance(error_info, dict):
                error_msg = "Auth failure: {}".format(
                    error_info.get("message", str(ex))
                )
                return self._raise_exception(
                    AuthError, message=error_msg, code=error_info.get("code", 0)
                )
            else:
                return self._raise_exception(AuthError, f"Auth failure: {error_info}")
        except Exception as ex:
            return self._raise_exception(AuthError, f"Auth failure: {ex}")

    def _get_polymatica_version(self, polymatica_version: str) -> str:
        """
        Формирование мажорной версии Полиматики.
        """
        return (
            ".".join(polymatica_version.split(".")[0:2]) or DEFAULT_POLYMATICA_VERSION
        )

    @timing
    def _check_connection(
        self,
        suffix_urls: List,
        command_name: str = "user_layer",
        state: str = "get_session_layers",
    ) -> str:
        """
        Проверка подключения посредством вызова заданной команды, показывающая, валиден ли пользовательский
        идентификатор сессии. Актуально только если пользователем был передан идентификатор сессии.
        Ничего не возвращает, но может сгенерировать исключение AuthError, если идентификатор невалиден.
        :param command_name: название команды.
        :param state: состояние команды.
        """
        # подготовка данных для отправки запроса
        headers = {"Accept": "text/plain", "Content-Type": "application/json"}
        manager_commands = self.server_codes.get("manager", {}).get("command", {})
        if not manager_commands:
            return self._raise_exception(
                PolymaticaException, "Manager commands not found!", with_traceback=False
            )
        data = {
            "state": 0,
            "session": self.session_id,
            "queries": [
                {
                    "uuid": self.authorization_uuid,
                    "command": {
                        "plm_type_code": manager_commands.get(command_name, {}).get(
                            "id"
                        ),
                        "state": manager_commands.get(command_name, {})
                        .get("state", {})
                        .get(state),
                    },
                }
            ],
        }

        # отправка запроса
        response, suffix_url = request_with_undefined_suffix_url(
            suffix_urls, self.base_url, json.dumps(data), self.timeout, headers
        )
        response_json = response.json()

        # анализ ответа
        command_result = next(iter(response_json.get("queries"))).get("command", {})
        if "error" in command_result:
            error_data = command_result.get("error", {})
            error_code, error_msg = error_data.get("code", 0), error_data.get(
                "message", "No error description!"
            )
            if error_code == 270:
                # неверная сессия/uuid авторизации
                return self._raise_exception(
                    AuthError,
                    "Session does not exist",
                    code=error_code,
                    with_traceback=False,
                )
            # любая другая ошибка
            return self._raise_exception(
                PolymaticaException, error_msg, code=error_code, with_traceback=False
            )

        return suffix_url

    @timing
    def _get_initial_config(self):
        """
        Получение начальных данных (см. блок переменных, хранящих текущую конфигурацию в методе __init__).
        Актуально только если пользователем был передан идентификатор сессии.
        """
        # получаем список слоёв
        layers = self.get_layer_list()
        self.layers_list = [layer[0] for layer in layers]

        # получаем идентификатор активного слоя
        self.active_layer_id = self.get_active_layer_id()

        # получаем все модули на текущем слое (это и OLAP-модули, и модули графиков и тд)
        layer_settings = self.execute_manager_command(
            command_name="user_layer", state="get_layer", layer_id=self.active_layer_id
        )
        layer_modules = (
            self.h.parse_result(
                result=layer_settings, key="layer", nested_key="module_descs"
            )
            or list()
        )

        # на текущем слое может быть несколько открытых модулей одного типа (несколько OLAP, несколько графиков и тд);
        # активным будем считать последний из них - поэтому проходим по реверсированному списку
        search_map = {"olap": True, "graph": True}
        for module in reversed(layer_modules):
            module_type, module_uuid = module.get("type_id"), module.get("uuid")
            # получаем идентификатор активного OLAP-модуля и соответствующий ему идентификатор куба
            if search_map.get("olap") and module_type == MULTISPHERE_ID:
                self.set_multisphere_module_id(module_uuid)
                self.cube_id = module.get("cube_id")
                search_map["olap"] = False
            # получаем идентификатор модуля графиков
            if search_map.get("graph") and module_type == GRAPH_ID:
                self._set_graph_module_id(module_uuid)
                search_map["graph"] = False

        # получаем имя куба
        if self.cube_id:
            cubes_list = self.get_cubes_list() or list()
            for cube in cubes_list:
                if cube.get("uuid") == self.cube_id:
                    self.cube_name = cube.get("name")
                    break

        # обновляем общее количество строк, если открыт OLAP-модуль
        if self.multisphere_module_id:
            self.update_total_row()
        self.func_name = "_get_initial_config"

    @timing
    def _get_interface_config(self) -> dict:
        """
        Получить текущую конфигурацию интерфейса.
        """
        config_data = self.execute_manager_command(
            command_name="user_iface", state="get_configuration"
        )
        config = self.h.parse_result(config_data, "configuration")
        return config

    def execute_manager_command(self, command_name: str, state: str, **kwargs) -> dict:
        """
        Выполнить любую команду модуля Manager.
        :param command_name: (str) название выполняемой команды.
        :param state: (str) название состояния команды.
        :param kwargs: дополнительные параметры, передаваемые в команду.
        :return: (dict) ответ на запрашиваемую команду;
            если же передана неверная (несуществующая) команда, будет сгенерировано исключение ManagerCommandError.
        :call_example:
            1. Инициализируем класс БЛ: bl_test = BusinessLogic(login="login", password="password", url="url")
            2. Выполняем команду модуля Manager:
                bl_test.execute_manager_command(command_name="command_name", state="state")
                Например: bl_test.execute_manager_command(command_name="user_layer", state="get_session_layers").
        """
        try:
            # вызов команды
            self.logger.info(
                f"Starting manager command: command_name='{command_name}' state='{state}'"
            )
            command = self.manager_command.collect_command(
                "manager", command_name, state, **kwargs
            )
            query = self.manager_command.collect_request(command)

            # executing query and profiling
            result = self.exec_request.execute_request(query)
            return (
                str(result).encode("utf-8")
                if command_name == "admin" and state == "get_user_list"
                else result
            )
        except Exception as e:
            return self._raise_exception(ManagerCommandError, str(e))

    def execute_olap_command(self, command_name: str, state: str, **kwargs) -> dict:
        """
        Выполнить любую команду модуля OLAP.
        :param command_name: (str) название выполняемой команды.
        :param state: (str) название состояния команды.
        :param kwargs: дополнительные параметры, передаваемые в команду.
        :return: (dict) ответ на запрашиваемую команду;
            если же передана неверная (несуществующая) команда, будет сгенерировано исключение OLAPCommandError.
        :call_example:
            1. Инициализируем класс БЛ: bl_test = BusinessLogic(login="login", password="password", url="url")
            2. Выполняем команду модуля Manager:
                bl_test.execute_olap_command(command_name="command_name", state="state")
                Например: bl_test.execute_olap_command(command_name="fact", state="list_rq").
        """
        try:
            # проверки
            self.checks(self.execute_olap_command.__name__)

            # вызов команды
            self.logger.info(
                f"Starting OLAP command: command_name='{command_name}' state='{state}'"
            )
            command = self.olap_command.collect_command(
                "olap", command_name, state, **kwargs
            )
            query = self.olap_command.collect_request(command)

            # executing query and profiling
            return self.exec_request.execute_request(query)
        except Exception as e:
            return self._raise_exception(OLAPCommandError, str(e), with_traceback=False)

    def execute_graph_command(self, command_name: str, state: str, **kwargs) -> dict:
        """
        Выполнить любую команду модуля Graph.
        :param command_name: (str) название выполняемой команды.
        :param state: (str) название состояния команды.
        :param kwargs: дополнительные параметры, передаваемые в команду.
        :return: (dict) ответ на запрашиваемую команду;
            если же передана неверная (несуществующая) команда, будет сгенерировано исключение ManagerCommandError.
        :call_example:
            1. Инициализируем класс БЛ: bl_test = BusinessLogic(login="login", password="password", url="url")
            2. Выполняем команду модуля Graph:
                bl_test.execute_graph_command(command_name="command_name", state="state")
                Например: bl_test.execute_graph_command(command_name="graph", state="get_available_types").
        """
        try:
            # вызов команды
            self.logger.info(
                f"Starting graph command: command_name='{command_name}' state='{state}'"
            )
            command = self.graph_command.collect_command(
                "graph", command_name, state, **kwargs
            )
            query = self.graph_command.collect_request(command)

            # executing query and profiling
            return self.exec_request.execute_request(query)
        except Exception as e:
            return self._raise_exception(GraphCommandError, str(e))

    def get_row_and_col_num(
        self,
        with_total_cols: bool = True,
        with_total_rows: bool = True,
        measure_only: bool = False,
        with_column_names: bool = False,
    ) -> Tuple[int, int]:
        """
        Возвращает общее число строк и колонок в OLAP-модуле по заданным параметрам.
        :param with_total_cols: (bool) учитывать промежуточные и итоговые тоталы в колонках;
            True - учитывать, False - не учитывать; по-умолчанию True.
        :param with_total_rows: (bool) учитывать промежуточные и итоговые тоталы в строчках;
            True - учитывать, False - не учитывать; по-умолчанию True.
        :param measure_only: (bool) учитывать ли размерности как колонки при вычислении числа колонок;
            True - только факты (размерности не учитывать), False - факты и размерности; по-умолчанию False.
        :param with_column_names: (bool) - учитывать ли строку названия колонок как строку данных;
            True - учитывать, False - не учитывать; по-умолчанию False.
        :return: (int, int) число строк, число колонок в OLAP-модуле.
        """
        if not self.multisphere_module_id:
            return self._raise_exception(
                PolymaticaException, "No active OLAP-module!", with_traceback=False
            )

        total_num_row, total_num_col = 0, 0
        args = dict(from_row=0, from_col=0, num_row=1, num_col=1)
        row_field, col_field = "total_row", "total_col"

        # получение данных командой "get"
        get_cmd_result = self.execute_olap_command(
            command_name="view", state="get", **args
        )
        total_row_get_cmd, total_col_get_cmd = self.h.parse_result(
            get_cmd_result, row_field
        ), self.h.parse_result(get_cmd_result, col_field)
        left_dims_count = len(self.h.parse_result(get_cmd_result, "left_dims") or [])

        # получение данных командой "get"
        get_2_cmd_result = self.execute_olap_command(
            command_name="view", state="get_2", **args
        )
        total_row_get_2_cmd, total_col_get_2_cmd = self.h.parse_result(
            get_2_cmd_result, row_field
        ), self.h.parse_result(get_2_cmd_result, col_field)

        # строки
        if with_total_rows:
            total_num_row = (
                total_row_get_cmd + 1 if with_column_names else total_row_get_cmd
            )
        else:
            total_num_row = (
                total_row_get_2_cmd + 1 if with_column_names else total_row_get_2_cmd
            )
        # колонки
        if with_total_cols:
            total_num_col = (
                total_col_get_cmd
                if measure_only
                else total_col_get_cmd + left_dims_count
            )
        else:
            total_num_col = (
                total_col_get_2_cmd - left_dims_count
                if measure_only
                else total_col_get_2_cmd
            )

        return total_num_row, total_num_col

    def update_total_row(self, **kwargs):
        """
        Обновляет количество строк мультисферы. Ничего не возвращает.
        По-умолчанию в общем количестве строк учитываются все промежуточные и общие тоталы.
        :param kwargs: (dict) дополнительные параметры обновления числа строк; словарь может содержать следующие ключи:
            with_total_cols: (bool) учитывать промежуточные и итоговые тоталы в колонках;
                True - учитывать, False - не учитывать; по-умолчанию True.
            with_total_rows: (bool) учитывать промежуточные и итоговые тоталы в строчках;
                True - учитывать, False - не учитывать; по-умолчанию True.
            measure_only: (bool) учитывать ли размерности как колонки при вычислении числа колонок;
                True - только факты (размерности не учитывать), False - факты и размерности; по-умолчанию False.
            with_column_names: (bool) - учитывать ли строку названия колонок как строку данных;
                True - учитывать, False - не учитывать; по-умолчанию False.
        """
        total_row, _ = self.get_row_and_col_num(**kwargs)
        self.total_row = total_row

    @timing
    def get_cube(self, cube_name: str, num_row: int = 100, num_col: int = 100) -> str:
        """
        Открыть OLAP-модуль по заданному кубу. Если передано неверное имя куба, будет сгенерировано исключение.
        :param cube_name: (str) имя куба (мультисферы).
        :param num_row: (int) количество строк, которые будут выведены; по-умолчанию 100.
        :param num_col: (int) количество колонок, которые будут выведены; по-умолчанию 100.
        :return: (str) идентификатор открытого куба.
        :call_example:
            1. Инициализируем класс БЛ: bl_test = BusinessLogic(login="login", password="password", url="url")
            2. Вызов метода:
                cube_id = bl_test.get_cube(cube_name="cube_name", num_row="num_row", num_col="num_col")
        """
        self.cube_name = cube_name

        # получение списка описаний мультисфер
        cubes_list = self.get_cubes_list()

        # получить cube_id из списка мультисфер
        try:
            self.cube_id = self.h.get_cube_id(cubes_list, cube_name)
        except Exception as e:
            return self._raise_exception(CubeNotFoundError, str(e))

        # создаём OLAP-модуль
        self._create_olap_module(num_row=num_row, num_col=num_col)

        # обновляем число трок в мультисфере и возвращаем результат
        self.update_total_row()
        self.func_name = "get_cube"
        return self.cube_id

    def get_multisphere_data(self, num_row: int = 100, num_col: int = 100) -> dict:
        """
        Получить данные мультисферы
        :param num_row: количество отображаемых строк
        :param num_col: количество отображаемых столбцов
        :return: (dict) multisphere data, format: {"dimensions": "", "facts": "", "data": ""}
        """

        # инициализация модуля Olap
        self.set_multisphere_module_id(self.multisphere_module_id)

        # рабочая область прямоугольника
        view_params = {
            "from_row": 0,
            "from_col": 0,
            "num_row": num_row,
            "num_col": num_col,
        }

        # получить список размерностей и фактов, а также текущее состояние таблицы со значениями
        # (рабочая область модуля мультисферы)
        query = self.olap_command.multisphere_data_query(
            self.multisphere_module_id, view_params
        )
        try:
            result = self.exec_request.execute_request(query)
        except Exception as e:
            return self._raise_exception(PolymaticaException, str(e))

        # multisphere data
        self.multisphere_data = {"dimensions": "", "facts": "", "data": ""}
        for item, index in [("dimensions", 0), ("facts", 1), ("data", 2)]:
            self.multisphere_data[item] = result["queries"][index]["command"][item]
        return self.multisphere_data

    @timing
    def get_cube_without_creating_module(self, cube_name: str) -> str:
        """
        Получить id куба по его имени, без создания модуля мультисферы
        :param cube_name: (str) имя куба (мультисферы)
        :return: id куба
        """
        self.cube_name = cube_name

        # получение списка описаний мультисфер
        cubes_list = self.get_cubes_list()

        # получить cube_id из списка мультисфер
        try:
            self.cube_id = self.h.get_cube_id(cubes_list, cube_name)
        except ValueError:
            return "Cube '%s' not found" % cube_name
        self.func_name = "get_cube_without_creating_module"
        return self.cube_id

    @timing
    def move_dimension(self, dim_name: str, position: str, level: int = None) -> dict:
        """
        Вынести размерность влево/вверх, либо убрать размерность из таблицы мультисферы.
        При передаче неверных параметров генерируется исключение ValueError.
        :param dim_name: (str) название размерности.
        :param position: (str) "left" (вынети влево) / "up" (вынести вверх) / "out" (вынести из таблицы).
        :param level: (int) 0, 1, ... (считается слева-направо для левой позиции, сверху-вниз для верхней размерности);
            обязательно должно быть задано при значении параметра position = "left" или position = "up";
            при значении параметра position = "out" параметр level игнорируется (даже если передано какое-то значение).
        :return: (dict) результат OLAP-команды ("dimension", "move").
        :call_example:
            1. Инициализируем класс БЛ: bl_test = BusinessLogic(login="login", password="password", url="url")
            2. Примеры вызова метода:
                bl_test.move_dimension(dim_name="dim_name", position="left", level=1)
                bl_test.move_dimension(dim_name="dim_name", position="up", level=1)
                bl_test.move_dimension(dim_name="dim_name", position="out")
        """
        try:
            # position: 0 - вынос размерности из таблицы, 1 - вынос размерности влево, 2 - вынос размерности вверх
            dim_id, position = self.checks(self.func_name, position, level, dim_name)
        except Exception as e:
            return self._raise_exception(ValueError, str(e), with_traceback=False)

        result = self.execute_olap_command(
            command_name="dimension",
            state="move",
            position=position,
            id=dim_id,
            level=level if position != 0 else 0,
        )
        self.update_total_row()
        return result

    @timing
    def get_measure_id(self, measure_name: str, need_get_data: bool = True) -> str:
        """
        Получить идентификатор факта по его названию.
        :param measure_name: название факта.
        :param need_get_data: нужно ли перед поиском нужного факта получать данные мультисферы.
            По-умолчанию нужно. Крайне не рекомендуется менять этот параметр без необходимости.
        :return: (str) идентификатор факта.
        """
        # получить словарь с размерностями, фактами и данными, если нужно;
        # если не нужно - подразумевается, что данные уже есть
        if need_get_data:
            self.get_multisphere_data()
        return self.h.get_measure_id(
            self.multisphere_data, measure_name, self.cube_name
        )

    @timing
    def get_dim_id(self, dim_name: str) -> str:
        """
        Получить идентификатор размерности по его названию.
        :param dim_name: (str) название размерности.
        :return: (str) идентификатор размерности.
        """
        # получить словарь с размерностями, фактами и данными
        self.get_multisphere_data()
        return self.h.get_dim_id(self.multisphere_data, dim_name, self.cube_name)

    @timing
    def get_measure_name(self, measure_id: str) -> str:
        """
        Получить название факта по его идентификатору.
        :param measure_id: (str) идентификатор факта.
        :return: (str) название факта.
        """
        try:
            result = self.h.get_measure_or_dim_name_by_id(measure_id, "facts")
        except Exception as ex:
            return self._raise_exception(PolymaticaException, str(ex))
        return result

    @timing
    def get_dim_name(self, dim_id: str) -> str:
        """
        Получить название размерности по его идентификатору.
        :param dim_id: (str) идентификатор размерности.
        :return: (str) название размерности.
        """
        try:
            result = self.h.get_measure_or_dim_name_by_id(dim_id, "dimensions")
        except Exception as ex:
            return self._raise_exception(PolymaticaException, str(ex))
        return result

    @timing
    def filter_pattern_change(self, dim_id: str, num: int, pattern_list: list) -> dict:
        """
        Вызов команды ("filter", "pattern_change").
        :param dim_id: (str) идентификатор размерности;
            при вводе несуществующего идентификатора будет сгенерировна ошибка.
        :param num: (int) количество считываемых элементов.
        :param pattern_list: (list) список паттернов; должен включать в себя словари формата
            {"pattern": <value>, "type": <value>}, где:
                pattern - любой паттерн поиска в строковом виде, не может быть пустым;
                type - одно из следующих значений:
                    'strict' - точное вхождение
                    'inclusion' - вхождение
                    'regex' - регулярное выражение
        :return: (dict) Результат команды ("filter", "pattern_change").
        """
        # проверяем, существует ли размерность с таким идентификатором;
        # если не существует - будет сгенерирована ошибка
        _ = self.get_dim_name(dim_id)

        # функция проверки словаря из списка pattern_list
        # strict - точное вхождение, inclusion - вхождение, 'regex' - регулярное выражение
        def check_pattern(pattern) -> bool:
            return (
                isinstance(pattern, dict)
                and {"pattern", "type"}.issubset(pattern)
                and pattern.get("type") in ["strict", "inclusion", "regex"]
            )

        # проверка pattern_list и формирование нового pattern_list
        new_pattern_list = list()
        for current_pattern in pattern_list:
            # пустой словарь пропускаем
            if not current_pattern:
                continue

            pattern, type_ = current_pattern.get("pattern"), current_pattern.get("type")

            # проверка поля "pattern" на строковый тип и на пустоту
            if not isinstance(pattern, str):
                return self._raise_exception(
                    FilterError,
                    '"pattern" field must be str type!',
                    with_traceback=False,
                )
            if not pattern:
                error_msg = (
                    'Found an empty search element: "pattern" field cannot be empty!'
                )
                return self._raise_exception(
                    FilterError, error_msg, with_traceback=False
                )

            # проверяем текущий словарь
            if check_pattern(current_pattern):
                new_pattern_list.append({"pattern": pattern, "type": type_})
            else:
                return self._raise_exception(
                    FilterError,
                    f'Incorrect pattern_list format: "{current_pattern}"',
                    with_traceback=False,
                )

        # вернём результат команды
        self.func_name = "filter_pattern_change"
        return self.execute_olap_command(
            command_name="filter",
            state="pattern_change",
            dimension=dim_id,
            num=num,
            pattern_list=new_pattern_list,
        )

    @timing
    def clear_all_dim_filters(self, dim_name: str, num_row: int = 100) -> dict:
        """
        Очистить все фильтры размерности
        :param dim_name: (str) Название размерности
        :param num_row: (int) Количество строк, которые будут отображаться в мультисфере
        :return: (dict) результат команды ("filter", "apply_data").
        """
        # получить словарь с размерностями, фактами и данными
        self.get_multisphere_data(num_row=num_row)

        # получение id размерности
        dim_id = self.h.get_measure_or_dim_id(
            self.multisphere_data, "dimensions", dim_name
        )

        # Наложить фильтр на размерность (в неактивной области)
        # получение списка активных и неактивных фильтров
        result = self.filter_pattern_change(dim_id, num_row, [])
        filters_values = self.h.parse_result(
            result=result, key="marks"
        )  # получить список on/off [0,0,...,0]

        # подготовить список для снятия меток: [0,0,..,0]
        for i in range(len(filters_values)):
            filters_values[i] = 0

        # 1. сначала снять все отметки
        self.execute_olap_command(
            command_name="filter", state="filter_all_flag", dimension=dim_id
        )

        # 2. нажать применить
        command1 = self.olap_command.collect_command(
            "olap", "filter", "apply_data", dimension=dim_id, marks=filters_values
        )
        command2 = self.olap_command.collect_command(
            "olap", "filter", "set", dimension=dim_id
        )
        query = self.olap_command.collect_request(command1, command2)

        try:
            result = self.exec_request.execute_request(query)
        except Exception as e:
            return self._raise_exception(PolymaticaException, str(e))

        self.update_total_row()
        self.func_name = "clear_all_dim_filters"
        return result

    @timing
    def reset_filters(self, dimension: Union[str, list, tuple] = "") -> bool:
        """
        Сброс (снятие) всех фильтров с указанных размерностей. В случае, если размерности не указаны, будет
        осуществлён сброс существующих фильтров по всем размерностям. При этом расположение размерностей неважно:
        они могут быть как в рабочей области (слева/наверху), так и в общем списке размерностей.
        По сути метод является аналогом сброса фильтра через ctrl-клик в UI.
        :param dimension: (str/list/tuple) список размерностей, по которым необходимо осуществить сброс фильтров;
            может быть задана как одна размерность (строка), так и список/кортеж размерностей;
            в случае если параметр не передан, либо передан пустой список/кортеж,
                будет осуществлён сброс существующих фильтров по всем размерностям;
            если хотя бы одна размерность из переданных не существует - будет сгенерировано исключение.
        :return: (bool) True, если были сброшены все необходимые фильтры.
        """
        # получаем список размерностей
        try:
            dimension = self.checks(self.func_name, dimension)
        except Exception as e:
            return self._raise_exception(ValueError, str(e), with_traceback=False)

        # получаем список всех размерностей
        all_dims_list = self._get_dimensions_list()

        # непосредственно функция очистки фильтров
        def _reset_filters_impl(check_func: Callable):
            """
            Внутренняя функция очистки фильтров.
            """
            commands = list()
            for current_dim in all_dims_list:
                # обрабатываем условие, по которому пропускаем текущую запись:
                # если список dimension пуст, то условием является отсутствие фильтра на размерности;
                # а если этот список не пуст - условием является отсутствие фильтра на размерности и несоответствие имён
                if check_func(current_dim):
                    continue
                dim_id = current_dim.get("id")
                commands.append(
                    self.olap_command.collect_command(
                        "olap", "filter", "clear", dimension=dim_id
                    )
                )
            # если мы собрали хотя бы одну команду - исполняем
            if commands:
                query = self.olap_command.collect_request(*commands)
                try:
                    self.exec_request.execute_request(query)
                except Exception as ex:
                    return self._raise_exception(PolymaticaException, str(ex))

        if not dimension:
            # если список пуст - сбрасываем все существующие размерности
            _reset_filters_impl(lambda item: not item.get("haveFilter"))
        else:
            # в противном случае сбрасываем фильтры с размерностей, заданных пользователем
            # проверяем, все ли заданные размерности существуют в мультисфере
            user_dimensions_set, exists_dimensions_set = set(dimension), {
                dim.get("name") for dim in all_dims_list
            }
            if not (user_dimensions_set <= exists_dimensions_set):
                diff_dims = user_dimensions_set - exists_dimensions_set
                pretty_diff_dims = [f'"{dim}"' for dim in diff_dims]
                error_msg = "Dimension{} {} not found in current multisphere!".format(
                    "s" if len(diff_dims) > 1 else "",
                    str(pretty_diff_dims)[1:-1].replace("'", ""),
                )
                return self._raise_exception(PolymaticaException, error_msg)
            # снимаем фильтры с указанных размерностей
            _reset_filters_impl(
                lambda item: not item.get("haveFilter")
                or item.get("name") not in dimension
            )
        return True

    @timing
    def get_current_datetime_format(self) -> str:
        """
        Получить из текущей конфигурации Полиматики формат хранения даты-времени.
        Если в конфигурации нет сответствующего параметра, или он есть, но принимает пустое значение,
        то вернётся значение по-умолчанию (маска даты-времени в ISO-формате).
        :return: (str) формат даты-времени в виде маски.
        """
        datetime_field = self.config.get("datetime_format")

        if datetime_field is None:
            return ISO_DATE_FORMAT
        return datetime_field

    @timing
    def put_dim_filter_by_value(
        self, value: str, dim_id: str, clear_filter: bool = False
    ):
        if clear_filter:
            self.execute_olap_command(
                command_name="filter", state="filter_all_flag", dimension=dim_id
            )

        res = self.execute_olap_command(
            command_name="filter",
            state="pattern_change",
            dimension=dim_id,
            pattern_list=[{"pattern": value, "type": "strict"}],
            num=100,
        )

        filters_values = self.h.parse_result(result=res, key="marks")

        if len(filters_values) == 0:
            self.execute_olap_command(
                command_name="filter", state="set", dimension=dim_id
            )
            return

        command1 = self.olap_command.collect_command(
            "olap", "filter", "apply_data", dimension=dim_id, marks=[1]
        )

        command2 = self.olap_command.collect_command(
            "olap", "filter", "set", dimension=dim_id
        )

        query = self.olap_command.collect_request(command1, command2)

        try:
            self.exec_request.execute_request(query)
        except Exception as e:
            return self._raise_exception(PolymaticaException, str(e))

        self.update_total_row()
        self.func_name = "put_dim_filter_by_value"

        return

    @timing
    def put_dim_filter(
        self,
        dim_name: str = None,
        filter_name: Union[str, List, None] = None,
        start_date: Union[int, str] = None,
        end_date: Union[int, str] = None,
        filter_field_format: Union[str, None] = None,
        dim_id: str = None,
    ) -> dict:
        """
        Установка фильтра по размерностям.
        :param dim_name: (str) Название размерности, по которой производится фильтрация.
        :param dim_id: (str) ID размерности, по которой производится фильтрация.
        :param filter_name: (Union[str, List, None]) Название фильтра;
            может быть задано строкой (один фильтр) или списком (несколько фильтров);
            в случае, если нужно указать интервал дат, необходимо передать None.
        :params start_date, end_date: (Union[int, str]) Начальная и конечная дата фильтрации соответственно.
            Начальная и конечная дата фильтрации формируют по сути интервал дат.
            Несколько особенностей задания этих параметров:
                1. Если используются месяцы, то необходимо использовать следующие значения (с учётом регистра):
                    ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"].
                2. Если используются дни недели, то необходимо использовать следующие значения (с учётом регистра):
                    ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
                3. Если указаны целочисленные значения, то подразумевается интервал дат.
                4. Если указаны строки-даты, то действует ряд правил и ограничений:
                    1. Допустимые форматы задания:
                        "ДД.ММ.ГГГГ"
                        "ДД-ММ-ГГГГ"
                        "ДД.ММ.ГГГГ ЧЧ:ММ:СС"
                        "ДД-ММ-ГГГГ ЧЧ:ММ:СС"
                    2. Во всех допустимых форматах задания допустимо менять местами год и число,
                        т.е. можно задать как "ДД-ММ-ГГГГ", так и "ГГГГ-ММ-ДД". Месяц всегда должен оставаться в центре
                    3. Год необходимо указывать в полном 4х-значном формате (без сокращений): например, 2021, а не 21;
                        из этого следует, что фильтровать можно только те даты, в которых год 4х-значный (от 1000г н.э.)
                    4. Если помимо даты указывается также и время, то его формат везде одинаков: "... ЧЧ:ММ:СС"
                    5. Оба параметра фильтрации должны иметь один формат (в противном случае будет сгенерирована ошибка)
                    6. Если в одном из параметров будет указано неверная дата/время (например, 30.02.2021) -
                        также будет сгенерирована ошибка
                5. В противном случае, если указано что-то иное - будет сгенерирована ошибка.
        :filter_field_format (Union[str, None]): формат даты-времени, в котором фильтруемая размерность
            представлена в Полиматике. Обязателен, если в параметрах start_date и end_date указаны строки-даты.
            Параметр необходим для корректной фильтрации даты-времени.
            Пример: filter_field_format='%d.%m.%Y %H:%M:%S.%f' или '%Y-%m-%d'.
        :return: (dict) результат команды ("filter", "apply_data").
        """
        # заполнение списка dates_list в зависимости от содержания параметров filter_name, start_date, end_date
        try:
            dates_list = self.checks(
                self.func_name,
                filter_name,
                start_date,
                end_date,
                filter_field_format,
                dim_name,
                dim_id,
            )
        except Exception as e:
            return self._raise_exception(
                PolymaticaException, str(e), with_traceback=False
            )

        # получение id размерности
        dim_id = dim_id or self.get_dim_id(dim_name)

        # Наложить фильтр на размерность (в неактивной области)
        # получение списка активных и неактивных фильтров
        result = self.h.get_filter_rows(dim_id)
        filters_list = self.h.parse_result(
            result=result, key="data"
        )  # получить названия фильтров
        filters_values = self.h.parse_result(
            result=result, key="marks"
        )  # получить список on/off [0,0,...,0]

        try:
            if (filter_name is not None) and (filter_name not in filters_list):
                if isinstance(filter_name, List):
                    for elem in filter_name:
                        if elem not in filters_list:
                            raise ValueError(
                                f"No filter '{elem}' in dimension '{dim_name}'"
                            )
                else:
                    raise ValueError(
                        f"No filter '{filter_name}' in dimension '{dim_name}'"
                    )
        except ValueError as e:
            return self._raise_exception(PolymaticaException, str(e))

        # подготовить список для снятия меток: [0,0,..,0]
        length = len(filters_values)
        for i in range(length):
            filters_values[i] = 0

        # сначала снять все отметки
        self.execute_olap_command(
            command_name="filter", state="filter_all_flag", dimension=dim_id
        )

        # подготовить список фильтров с выбранными отмеченной меткой
        for idx, elem in enumerate(filters_list):
            if isinstance(filter_name, List):
                if elem in filter_name:
                    filters_values[idx] = 1
            # если фильтр по интервалу дат:
            elif filter_name is None:
                if elem in dates_list:
                    filters_values[idx] = 1
            # если фильтр выставлен по одному значению:
            elif elem == filter_name:
                ind = filters_list.index(filter_name)
                filters_values[ind] = 1
                break

        # 2. нажать применить
        command1 = self.olap_command.collect_command(
            "olap", "filter", "apply_data", dimension=dim_id, marks=filters_values
        )
        command2 = self.olap_command.collect_command(
            "olap", "filter", "set", dimension=dim_id
        )
        query = self.olap_command.collect_request(command1, command2)

        try:
            result = self.exec_request.execute_request(query)
        except Exception as e:
            return self._raise_exception(PolymaticaException, str(e))

        self.update_total_row()
        self.func_name = "put_dim_filter"
        return result

    @timing
    def delete_dim_filter(
        self,
        dim_name: str,
        filter_name: Union[str, list, set, tuple],
        num_row: int = 100,
    ) -> dict:
        """
        Убрать выбранный фильтр размерности.
        Позволяет работать с любыми типами размерностей: верхними, левыми, не вынесенными в мультисферу.
        :param dim_name: (str) Название размерности.
        :param filter_name: (str/list/set/tuple) Название метки/фильтра;
            может быть задано как строкой, так и списком/множеством/кортежем.
        :param num_row: (int) Количество строк, которые будут отображаться в мультисфере.
        :return: (dict) результат команды ("filter", "apply_data").
        """
        # проверки типов параметров
        params = validate_params(
            DeleteDimFilterParams,
            self._raise_exception,
            dim_name=dim_name,
            filter_name=filter_name,
            num_row=num_row,
        )
        dim_name, filter_name, num_row = (
            params.dim_name,
            params.filter_name,
            params.num_row,
        )

        if not filter_name:
            raise ValueError('Param "filter_name" cannot be empty!')
        filter_names = [filter_name] if isinstance(filter_name, str) else filter_name

        # получить словарь с размерностями, фактами и данными
        self.get_multisphere_data()

        # получаем идентификатор размерности по её названию
        dim_id = self.h.get_measure_or_dim_id(
            self.multisphere_data, "dimensions", dim_name
        )

        # получаем данные размерности (обрезаем все ненужные пробелы)
        result = self.filter_pattern_change(dim_id, num_row, [])
        filters_list = self.h.parse_result(result=result, key="data")
        filters_list = list(map(lambda item: (item or "").strip(), filters_list))

        # получаем индексы данных (0 - не отмечено, 1 - отмечено)
        filters_values = self.h.parse_result(result=result, key="marks")

        # проверяем, есть ли заданный пользователем фильтр в списке данных;
        # если есть - снимаем с него метку
        for filter_name in filter_names:
            if filter_name not in filters_list:
                error_msg = f'Element "{filter_name}" is missing in the filter of specified dimension'
                return self._raise_exception(
                    ValueError, error_msg, with_traceback=False
                )
            filters_values[filters_list.index(filter_name)] = 0

        # применяем выбранные фильтры
        command1 = self.olap_command.collect_command(
            "olap", "filter", "apply_data", dimension=dim_id, marks=filters_values
        )
        command2 = self.olap_command.collect_command(
            "olap", "filter", "set", dimension=dim_id
        )
        query = self.olap_command.collect_request(*[command1, command2])
        try:
            result = self.exec_request.execute_request(query)
        except Exception as e:
            return self._raise_exception(PolymaticaException, str(e))

        self.update_total_row()
        self.func_name = "delete_dim_filter"
        return result

    @timing
    def create_consistent_dim(
        self, formula: str, separator: str, dimension_list: List[str]
    ) -> dict:
        """
        Создать составную размерность.
        :param formula: (str) Имя составной размерности, рекомендуемый формат: [Размерность1]*[Размерность2]
        :param separator: (str) Разделитель, который будет отображаться между элементами
            составной размерности. Может принимать одно из значений: "*", "-", "," и " ".
        :param dimension_list: (List) Список имён исходных размерностей - ["Размерность1", "Размерность2"]
        :return: (dict) результат команды ("dimension", "create_union").
        """
        # проверки типов
        params = validate_params(
            CreateConsistentDimParams,
            self._raise_exception,
            formula=formula,
            separator=separator,
            dimension_list=dimension_list,
        )
        formula, separator, dimension_list = (
            params.formula,
            params.separator,
            params.dimension_list,
        )

        # проверка значения separator
        try:
            self.checks(self.func_name, separator)
        except Exception as e:
            return self._raise_exception(ValueError, str(e), with_traceback=False)

        # получить словарь с размерностями, фактами и данными
        self.get_multisphere_data()

        # подготовка списка с id размерностей
        dim_ids = []
        for i in dimension_list:
            dim_id = self.h.get_measure_or_dim_id(
                self.multisphere_data, "dimensions", i
            )
            dim_ids.append(dim_id)

        return self.execute_olap_command(
            command_name="dimension",
            state="create_union",
            name=formula,
            separator=separator,
            dim_ids=dim_ids,
            union_dims_visibility=[1] * len(dim_ids),
        )

    @timing
    def switch_unactive_dims_filter(self) -> dict:
        """
        Переключить фильтр по неактивным размерностям
        :return: (dict) команда модуля Olap "dimension", состояние "set_filter_mode"
        """
        result = self.execute_olap_command(
            command_name="dimension", state="set_filter_mode"
        )
        self.update_total_row()
        return result

    @timing
    def copy_measure(self, measure_name: str) -> str:
        """
        Копировать заданный факт.
        :param measure_name: (str) имя копируемого факта.
        :return: (str) идентификатор копии факта.
        """
        # получить словарь с размерностями, фактами и данными
        self.get_multisphere_data()

        # Получить id факта
        measure_id = self.h.get_measure_or_dim_id(
            self.multisphere_data, "facts", measure_name
        )
        result = self.execute_olap_command(
            command_name="fact", state="create_copy", fact=measure_id
        )
        return self.h.parse_result(result=result, key="create_id")

    @timing
    def rename_measure(self, measure_name: str, new_measure_name: str) -> dict:
        """
        Переименовать факт.
        :param measure_name: (str) старое имя факта.
        :param new_measure_name: (str) новое имя факта.
        :return: (dict) результат команды ("fact", "rename").
        """
        # получить словарь с размерностями, фактами и данными
        self.get_multisphere_data()

        # получить id факта
        measure_id = self.h.get_measure_or_dim_id(
            self.multisphere_data, "facts", measure_name
        )
        return self.execute_olap_command(
            command_name="fact", state="rename", fact=measure_id, name=new_measure_name
        )

    @timing
    def measure_rename_group(self, group: str, new_name: str, module: str = "") -> dict:
        """
        Переименование группы фактов.
        :param group: (str) название/идентификатор группы фактов, которую нужно переименовать.
        :param new_name: (str) новое название группы фактов; не может быть пустым.
        :param module: (str) название/идентификатор OLAP-модуля, в котором нужно переименовать группу фактов;
            если модуль указан, но такого нет - сгенерируется исключение;
            если модуль не указан, то берётся текущий (активный) модуль (если его нет - сгенерируется исключение).
        :return: (dict) результат команды ("fact", "rename").
        :call_example:
            1. Инициализируем класс БЛ: bl_test = BusinessLogic(login="login", password="password", url="url")
            2. Вызов метода:
                group, new_name = "group_id_or_group_name", "new_name"
                bl_test.measure_rename_group(group=group, new_name=new_name)
            3. Вызов метода с передачей валидного идентификатора/названия модуля:
                group, new_name, module = "group_id_or_group_name", "new_name", "valid_module_id_or_valid_module_name"
                bl_test.measure_rename_group(group=group, new_name=new_name, module=module)
            4. Вызов метода с передачей невалидного идентификатора/названия модуля:
                group, new_name = "group_id_or_group_name", "new_name"
                module = "invalid_module_id_or_invalid_module_name"
                bl_test.measure_rename_group(group=group, new_name=new_name, module=module)
                output: exception "Module cannot be found by ID or name".
        """
        # проверка нового имени на пустоту
        if not new_name:
            return self._raise_exception(
                ValueError,
                "New name of measure group cannot be empty!",
                with_traceback=False,
            )

        # получаем идентификатор указанного OLAP-модуля и получаем список его фактов
        module_id = self._get_olap_module_id(module)
        self.set_multisphere_module_id(module_id)
        measures_list = self.get_olap_module_info(module_id).get("measures")

        # переименовать группу, если в мультисфере есть такая группа фактов
        query = ""
        for item in measures_list:
            item_id = item.get("id")
            if group == item.get("name") or group == item_id:
                query = self.execute_olap_command(
                    command_name="fact",
                    state="tree_rename_group_request",
                    id=item_id,
                    name=new_name,
                )
                break

        # если же в мультисфере нет указанной группы фактов - выбрасываем исключение
        if not query:
            return self._raise_exception(
                ValueError, f'Group "{group}" not found', with_traceback=False
            )

        # снять выделение фактов
        self.execute_olap_command(command_name="fact", state="unselect_all")
        return query

    @timing
    def measure_remove_group(self, group: str, module: str = "") -> dict:
        """
        Удаление (разгруппировка) группы фактов.
        :param group: (str) название/идентификатор группы фактов, которую нужно удалить.
        :param module: (str) название/идентификатор OLAP-модуля, в котором нужно удалить группу фактов;
            если модуль указан, но такого нет - сгенерируется исключение;
            если модуль не указан, то берётся текущий (активный) модуль (если его нет - сгенерируется исключение).
        :return: (dict) результат команды ("fact", "del").
        :call_example:
            1. Инициализируем класс БЛ: bl_test = BusinessLogic(login="login", password="password", url="url")
            2. Вызов метода:
                group = "group_id_or_group_name"
                bl_test.measure_remove_group(group=group)
            3. Вызов метода с передачей валидного идентификатора/названия модуля:
                group, module = "group_id_or_group_name", "valid_module_id_or_valid_module_name"
                bl_test.measure_remove_group(group=group, module=module)
            4. Вызов метода с передачей невалидного идентификатора/названия модуля:
                group, module = "group_id_or_group_name", "invalid_module_id_or_invalid_module_name"
                bl_test.measure_remove_group(group=group, module=module)
                output: exception "Module cannot be found by ID or name".
        """
        # получаем идентификатор указанного OLAP-модуля и получаем список его фактов
        module_id = self._get_olap_module_id(module)
        self.set_multisphere_module_id(module_id)
        measures_list = self.get_olap_module_info(module_id).get("measures")

        # удалить группу, если в мультисфере есть такая такая группа фактов
        query = ""
        for item in measures_list:
            item_id = item.get("id")
            if group == item.get("name") or group == item_id:
                query = self.execute_olap_command(
                    command_name="fact",
                    state="tree_delete_groups_request",
                    groups=[item_id],
                )
                break

        # если же в мультисфере нет указанной группы фактов - выбрасываем исключение
        if not query:
            return self._raise_exception(
                ValueError, f'Group "{group}" not found', with_traceback=False
            )

        # снять выделение фактов
        self.execute_olap_command(command_name="fact", state="unselect_all")
        self.func_name = "measure_remove_group"
        return query

    def _get_measures_list(self) -> List:
        """
        Получить список фактов текущей (активной) мультисферы.
        """
        result = self.execute_olap_command(command_name="fact", state="list_rq")
        return self.h.parse_result(result, "facts") or list()

    def _get_tree_dimension_list(self) -> List:
        result = self.execute_olap_command(
            command_name="dimension", state="tree_get_request"
        )
        return self.h.parse_result(result, "nodes") or list()

    def _get_tree_fact_list(self):
        result = self.execute_olap_command(
            command_name="fact", state="tree_get_request"
        )
        return self.h.parse_result(result, "nodes")

    def _get_dimensions_list(self) -> List:
        """
        Получить список размерностей текущей (активной) мультисферы.
        """
        result = self.execute_olap_command(command_name="dimension", state="list_rq")
        return self.h.parse_result(result, "dimensions") or list()

    @timing
    def rename_dimension(self, dim_name: str, new_name: str) -> dict:
        """
        Переименовать размерность, не копируя её.
        Переименовывать можно как вынесенную (влево/вверх), так и невынесенную размерность.
        :param dim_name: (str) название размерности, которую требуется переименовать.
        :param new_name: (str) новое название размерности.
        :return: (dict) результат выполнения команды ("dimension", "rename").
        :call_example:
            1. Инициализируем класс БЛ: bl_test = BusinessLogic(login="login", password="password", url="url")
            2. Вызов метода: bl_test.rename_dimension(dim_name="dim_name", new_name="new_name")
        """
        # проверки
        params = validate_params(
            RenameDimsParams,
            self._raise_exception,
            dim_name=dim_name,
            new_name=new_name,
        )
        dim_name, new_name = params.dim_name, params.new_name

        # получить id размерности и переименовать её
        dim_id = self.get_dim_id(dim_name)
        self.func_name = "rename_dimension"
        return self.execute_olap_command(
            command_name="dimension", state="rename", id=dim_id, name=new_name
        )

    @timing
    def change_measure_type(self, measure_name: str, type_name: str) -> dict:
        """
        Поменять вид факта.
        :param measure_name: (str) название факта
        :param type_name: (str) название вида факта; принимает значения, как на интерфейсе:
            "Значение"
            "Процент"
            "Ранг"
            "Изменение"
            "Изменение в %"
            "Нарастающее"
            "ABC"
            "Среднее"
            "Количество уникальных"
            "Количество"
            "Медиана"
            "Отклонение"
            "Минимум"
            "Максимум"
        :return: (dict) результат OLAP-команды ("fact", "set_type")
        :call_example:
            1. Инициализируем класс БЛ: bl_test = BusinessLogic(login="login", password="password", url="url")
            2. Вызов метода: bl_test.change_measure_type(measure_name="measure_name", type_name="type_name")
                В случае, если были переданы некорректные данные, сгенерируется ошибка.
        """
        # Получить вид факта (id)
        measure_type = self.h.get_measure_type(type_name)

        # по имени факта получаем его идентификатор
        measure_id = self.get_measure_id(measure_name)

        # выбрать вид факта
        self.func_name = "change_measure_type"
        return self.execute_olap_command(
            command_name="fact", state="set_type", fact=measure_id, type=measure_type
        )

    def _download_file(self, url: str, file_path: str, file_name: str):
        """
        Загрузить файл из заданного url-адреса.
        :param url: адрес, по которому находится исходных загружаемый файл.
        :param file_path: директория файла, содержащего загруженные данные; если указанной директории не сущестует -
            она будет создана; директория имеет вид "path_to_file/file_name".
        :param file_name: имя файла, содержащий загруженные данные.
        """
        # проверка на существование директории: если её нет - то создаё
        if not os.path.exists(file_path):
            log(
                f'Path "{file_path}" not exists! Creating path recursively...',
                level="error",
            )
            os.makedirs(file_path, exist_ok=True)

        # формирование полного пути файла
        full_file_path = os.path.join(file_path, file_name)

        # непосредственно загрузка файла;
        # т.к. файл может быть довольно большим, загружаем данные чанками;
        # в противном случае все загруженные данные будут сохранены в памяти, которой может не хватит - тогда, возможно,
        # может упасть ошибка MemoryError.
        # инфо:
        # https://github.com/tableau/server-client-python/issues/105
        # https://docs.python-requests.org/en/master/user/advanced/#body-content-workflow
        log("Start download file")
        try:
            with requests.get(
                url, cookies={"session": self.session_id}, stream=True
            ) as r:
                with open(full_file_path, "wb") as file:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                            file.flush()
        except Exception as e:
            return self._raise_exception(ExportError, str(e))
        log("End download file")

    @timing
    def export(self, path: str, file_format: str) -> Tuple[str, str]:
        """
        Экспортировать мультисферу в файл в заданную директорию. Если указанной директории не сущестует - она будет
        создана. Непосредственно имя файла будет сгенерировано автоматически.
        :param path: (str) директория, в которой нужно сохранить файл; также, директория не может быть пустой
            (т.е. не может содержать пустую строку или None).
        :param file_format: (str) формат сохраненного файла: "csv", "xls", "json".
        :return (str): file_name - название файла.
        :return (str): path - директория файла.
        """
        # проверки
        try:
            self.checks(self.func_name, file_format, path)
        except Exception as e:
            return self._raise_exception(ValueError, str(e), with_traceback=False)

        # начать экспорт данных и дождаться загрузки
        self.execute_olap_command(
            command_name="xls_export",
            state="start",
            export_format=file_format,
            export_destination_type="local",
        )
        need_check_progress = True
        while need_check_progress:
            # небольшая задержка
            time.sleep(1)

            # получаем статус загрузки
            try:
                progress_data = self.execute_olap_command(
                    command_name="xls_export", state="check"
                )
                status_info = self.h.parse_result(progress_data, "status")
                progress_value = self.h.parse_result(progress_data, "progress")
                status_code, status_message = status_info.get(
                    "code", -1
                ), status_info.get("message", "Unknown error!")
                log(f"Export data: status: {status_code}, progress: {progress_value}")
            except Exception:
                # если упала ошибка - не удалось получить ответ от сервера: возможно, он недоступен
                return self._raise_exception(
                    ExportError,
                    "Failed to export data! Possible server is unavailable.",
                )

            # анализируем статус загрузки
            if status_code == 206:
                # в процессе
                need_check_progress = True
            elif status_code == 207:
                # выполнено
                need_check_progress = False
            elif status_code == 208:
                # ошибка: чем-то или кем-то остановлено (например, пользователем)
                return self._raise_exception(
                    ExportError, "Export data was stopped!", with_traceback=False
                )
            elif status_code == -1:
                # ошибка: не удалось получить код текущего статуса
                return self._raise_exception(
                    ExportError, "Unable to get status code!", with_traceback=False
                )
            else:
                # прочие ошибки
                return self._raise_exception(
                    ExportError, status_message, with_traceback=False
                )

        # имя файла в результате команды ('xls_export', 'check') приходит только после полной загрузки файла
        # формируем название нужного файла
        format_map = {"csv": ["csv"], "xls": ["xls", "xlsx"], "json": ["json"]}
        server_f_name = self.h.parse_result(result=progress_data, key="file_name")
        download_file_name = server_f_name.replace(":", "-")
        download_file_name = (
            download_file_name[:-8]
            if download_file_name.split(".")[-1] not in format_map.get(file_format)
            else download_file_name
        )

        # скачивание файла
        self._download_file(
            f"{self.resources_url}/{server_f_name}", path, download_file_name
        )

        # проверка что файл скачался после экспорта
        assert download_file_name in os.listdir(
            path
        ), f'File "{download_file_name}" not in path "{path}"!'
        return download_file_name, path

    @staticmethod
    def _is_numeric(value: str) -> bool:
        """
        Проверка, является ли заданная строка числом.
        :param value: (str) строка для проверки.
        :return: (bool) True - строка является числом, False - в противном случае.
        """
        is_float = True
        try:
            float(value.replace(",", "."))
        except ValueError:
            is_float = False
        return value.isnumeric() or is_float

    @timing
    def create_calculated_measure(self, new_name: str, formula: str) -> dict:
        """
        Создать вычислимый факт.
        Список используемых операндов: ["=", "+", "-", "*", "/", "<", ">", "!=", "<=", ">="].
        Список используемых логических функций: ["not", "and", "or"].
        Список доступных функций: ["top", "total", "corr"].
        Правила написания формул:
            1. При объявлении фунции между её именем и открывающей скобкой не должно быть пробелов. Таким образом
                обозначается, что открывающая скобка относится к функции.
                Верное написание: "top(", "total(", "corr(".
                Неверное использование: "top (", "total (", "corr (".
            2. Формат задания фактов без верхних размерностей: [Сумма].
            3. Формат задания фактов с учётом верхних размерностей: [Апрель&Payment], где до амперсанда (&) указывается
                название верхней размерности, а после - название факта. При этом амперсанд можно либо писать слитно,
                либо разделять пробелами.
            4. В случае, если в OLAP-модуле вынесено несколько верхних размерностей, то в выражении (формуле) участвует
                только самая верхняя из них. Таким образом, вложенные верхние размерности не участвуют в создании факта.
            5. В качестве разделителя параметров в методах "top" и "corr" необходимо использовать точку с запятой. При
                этом точку с запятой можно либо писать слитно, либо разделять пробелами.
                Примеры:
                    1. "top([Сумма];100)"
                    2. "corr([Март, Payment] ; [Апрель, Commission])"
                    3. "top([Декабрь,Сумма] ; 100)"
            6. Все использующиеся операнды, круглые скобки, числа, факты и функции должны быть разделены пробелами.
                Примеры:
                    1. "100 + [Сумма]",
                    2. "corr([Сумма];[Выручка]) - top([Сумма];100)",
                    3. "20 + total([Выручка]) * ( [Май & Сумма] + [Май & Выручка] ) / 3"
            7. Необходимо соблюдать баланс скобочек: открывающих и закрывающих должно быть поровну.
        Примеры корректных формул:
            1. top([Сумма долга] ; 1000) + total([Остаток])
            2. ( 100 + [Больницы] ) / ( [Количество вызовов врача] * 2 ) + corr([Количество вызовов врача];[Больницы])
        :param new_name: (str) название создаваемого вычислимого факта; обязательны буквы, допустимы символы;
            нельзя использовать слова "top", "total", "corr", "not", "and", "or", "if"; название не может быть пустым.
        :param formula: (str) формула, соответствующая описанным выше правилам, не может быть пустой.
        :return: (dict) результат команды ("fact", "create_calc").
        """
        # проверки
        try:
            self.checks(self.func_name, new_name, formula)
        except Exception as e:
            return self._raise_exception(ValueError, str(e), with_traceback=False)

        # проверяем баланс открывающих и закрывающих скобок
        brackets = (("(", ")", "круглых"), ("[", "]", "квадратных"))
        for bracket_pair in brackets:
            opening_count, closing_count = formula.count(
                bracket_pair[0]
            ), formula.count(bracket_pair[1])
            if opening_count != closing_count:
                error_msg = (
                    "Incorrect balance of {} brackets in formula! "
                    "Opening brackets: {}, closing brackets: {}".format(
                        bracket_pair[2], opening_count, closing_count
                    )
                )
                raise ValueError(error_msg)

        output, top_dim_delimiter = "", "&"

        # получить данные мультисферы
        self.get_multisphere_data()

        # анонимная функция, возвращающая имя факта по его первичному представлению
        get_measure_name = lambda measure: measure[1:-1].strip()  # noqa: E731

        # анонимная функция, возвращающая идентификатор факта по имени факта
        get_measure_id = lambda measure: self.h.get_measure_or_dim_id(  # noqa: E731
            self.multisphere_data, "facts", measure
        )

        def get_measure_form(measure_content: str) -> str:
            """
            Парсинг факта с учётом верхней размерности.
            :param measure_content: (str) факт, отсылающий к верхней размерности.
            :return: (str) реализация указанного факта в формуле.
            """
            # возможны 2 кейса:
            # 1. формат факта [А&Б] (А - элемент верхней размерности, Б - название факта);
            # 2. формат факта [measure] (measure - название факта) - этот кейс без учёта верхней размерности
            # отличаем эти два кейса по амперсанду внутри квадратной скобки
            if top_dim_delimiter in measure_content:
                measure_content_part = get_measure_name(measure_content).split(
                    top_dim_delimiter
                )
                content_len = len(measure_content_part)
                if content_len != 2:
                    error_msg = f"Wrong format for specifying the top dimension! Expected 2 items, found {content_len}."
                    return self._raise_exception(
                        ValueError, error_msg, with_traceback=False
                    )
                top_dim_name = measure_content_part[0].strip()
                measure_name = measure_content_part[1].strip()

                # получаем идентификаторы верхних размерностей
                result = self.execute_olap_command(
                    command_name="view",
                    state="get",
                    from_row=0,
                    from_col=0,
                    num_row=1,
                    num_col=1,
                )
                top_dims = self.h.parse_result(result=result, key="top_dims")

                # сформировать словарь {"элемент верхней размерности": индекс_элемента}
                filter_pattern_result = self.filter_pattern_change(top_dims[0], 30, [])
                top_dim_values = self.h.parse_result(
                    result=filter_pattern_result, key="data"
                )
                top_dim_indexes = self.h.parse_result(
                    result=filter_pattern_result, key="indexes"
                )
                top_dim_map = dict(zip(top_dim_values, top_dim_indexes))

                # Проверяем, что наша размерность есть в списке верхних размерностей
                if top_dim_name not in top_dim_map:
                    return self._raise_exception(
                        ValueError,
                        f'Top dimension "{top_dim_name}" not found!',
                        with_traceback=False,
                    )

                measure_id = get_measure_id(measure_name)
                return f" fact({measure_id}; {top_dim_map[top_dim_name]}) "
            else:
                measure_id = get_measure_id(get_measure_name(measure_content))
                return f" fact({measure_id}) "

        # разбиваем исходную формулу на составляющие
        formula_lst = self.h.parse_formula(formula)

        try:
            for i in formula_lst:
                if (
                    (i in OPERANDS)
                    or (i in LOGIC_FUNCS)
                    or (i in ("(", ")"))
                    or self._is_numeric(i)
                ):
                    output += i
                elif "total(" in i:
                    # total([факт])
                    # эта функция не поддерживает верхние размерности, поэтому,
                    # если передан факт с верхней размерностью, то извлекаем из этой конструкции только имя факта
                    reg = re.search(r"\[(.*?)\]", i)
                    measure = reg.group(0).strip()
                    if top_dim_delimiter in measure:
                        measure = f"[{measure.split(top_dim_delimiter)[1]}"
                    measure_id = get_measure_id(get_measure_name(measure))
                    output += f"total({measure_id})"
                    continue
                elif "top(" in i:
                    # top([факт];сколько)
                    reg = re.search(r"\[(.*?)\]", i)
                    measure = reg.group(0).strip()
                    measure_template = get_measure_form(measure)
                    reg = re.search(r"\d+", i)
                    count_value = reg.group(0).strip()
                    output += f"top({measure_template}; {count_value} )"
                    continue
                elif "if(" in i:
                    raise ValueError("if(;;) not yet implemented!")
                elif "corr(" in i:
                    # corr([факт1];[факт2])
                    m = re.search(r"\((.*?)\)", i)
                    measures = m.group(1).split(";")
                    measure1 = measures[0].strip()
                    measure2 = measures[1].strip()
                    measure1_template = get_measure_form(measure1)
                    measure2_template = get_measure_form(measure2)
                    output += f"corr({measure1_template};{measure2_template})"
                    continue
                elif i[0] == "[":
                    # текущий элемент - факт
                    output += get_measure_form(i)
                    continue
                else:
                    raise ValueError(f"Unknown element in formula: {i}")
        except Exception as e:
            return self._raise_exception(
                ValueError, f"Failed to create calculated measure: {e}"
            )

        # непосредственно создание вычислимого факта
        result = self.execute_olap_command(
            command_name="fact",
            state="create_calc",
            name=new_name,
            formula=output,
            uformula=formula,
        )
        return result

    def get_scripts_description_list(self) -> List:
        """
        Получить описание всех сценариев.
        :return: (json) информация по каждому сценарию в формате JSON (список словарей).
        """

        def _rec_get_scripts_in_dir(
            curr_path: str = None, parent_id: str = self.ROOT_PARENT
        ) -> list:
            results = self.exec_request.execute_request(
                params=urljoin(
                    self.base_url,
                    f"api/{self.API_VERSION}/script_folders?parent={parent_id}",
                ),
                method="GET",
            )
            folders: list = results.json()["results"]

            results = self.exec_request.execute_request(
                params=urljoin(
                    self.base_url, f"api/{self.API_VERSION}/scripts?parent={parent_id}"
                ),
                method="GET",
            )
            scripts: list = results.json()["results"]
            for script in scripts:
                script["path"] = curr_path

            for folder in folders:
                folder_id, folder_name = folder["id"], folder["name"]
                scripts += _rec_get_scripts_in_dir(
                    curr_path=f"{curr_path}/{folder_name}"
                    if curr_path
                    else folder_name,
                    parent_id=folder_id,
                )

            return scripts

        scripts = _rec_get_scripts_in_dir()

        return scripts

    @timing
    def get_scripts_list(self) -> List:
        """
        Возвращает список сценариев с их описанием.
        Для обратной совместимости сохранены дублирующие друга друга
        и get_scripts_list, и get_scripts_description_list().
        :return: (json) информация по каждому сценарию в формате JSON (список словарей).
        """
        return self.get_scripts_description_list() or list()

    def get_scenario_cube_ids(self, scenario_id: str) -> set:
        """
        Возвращает идентификаторы всех мультисфер, входящих в заданный сценарий.
        :param scenario_id: (str) идентификатор сценария.
        :return: (set) идентфикаторы мультисфер, входящих в заданный сценарий.
        """
        result = self.execute_manager_command(
            command_name="scripts",
            state="get_script_description",
            script_id=scenario_id,
        )
        script_info = self.h.parse_result(result, "script")
        used_cubes = script_info.get("used_cubes", [])
        return {cube.get("id") for cube in used_cubes}

    def _check_scenario_cubes_permission(self, scenario_id: str):
        """
        Проверка, обладает ли текущий пользователь админскими правами на все мультисферы, входящие в заданный сценарий.
        Если не обладает, то генерируется ошибка.
        :param scenario_id: (str) идентификатор сценария.
        """
        # получаем идентификаторы всех мультисфер, входящих в заданный сценарий
        script_cube_ids = self.get_scenario_cube_ids(scenario_id=scenario_id)

        # получаем идентификаторы мультисфер, на которые текущий пользователь имеет админские права
        ms_permission_data = self.get_cube_permissions()
        ms_permission_ids = {
            item.get("cube_id") for item in ms_permission_data if item.get("accessible")
        }

        # собственно, сама проверка
        if script_cube_ids <= ms_permission_ids:
            return
        return self._raise_exception(
            RightsError,
            "Not all multisphere used in a scenario are available",
            with_traceback=False,
        )

    def _check_scenario_data(
        self, scenario_id: str, scenario_name: str, scenario_path: str = None
    ) -> Tuple[str, str]:
        """
        Проверка данных сценария:
        1. Если задан идентификатор, но не задано имя - проверяем, что такой идентификатор реально есть и находим имя.
        2. Если задано имя, но не задан идентификатор - находим идентификатор.
        3. Если задано и имя, и идентификатор - проверяем соответствие имени и идентификатора сценария.
        Если какая-то проверка не пройдёт - сгенерируется ошибка ScenarioError.
        :return: (str) идентификатор сценария.
        :return: (str) название сценария.
        """
        # получаем данные по всем сценариям
        script_desc = self.get_scripts_list()

        # eсли задан идентификатор, но не задано имя - проверяем, что такой реально действительно есть и находим имя
        if (scenario_id is not None) and (scenario_name is None):
            scenario_name = self.h.get_scenario_name_by_id(script_desc, scenario_id)

        # eсли задано имя, но не задан идентификатор - находим идентификатор
        elif (scenario_id is None) and (scenario_name is not None):
            scenario_id = self.h.get_scenario_id_by_name(
                script_desc, scenario_name, scenario_path
            )

        # eсли задано и имя, и идентификатор - проверяем соответствие имени и идентификатора сценария
        elif (scenario_id is not None) and (scenario_name is not None):
            find_scenario_id = self.h.get_scenario_id_by_name(
                script_desc, scenario_name, scenario_path
            )
            if find_scenario_id != scenario_id:
                return self._raise_exception(
                    ScenarioError,
                    "Scenario id or name is incorrect!",
                    with_traceback=False,
                )

        return scenario_id, scenario_name

    def check_scenarios_dims_facts_permission(self, scenario_id: str) -> bool:
        """
        Проверка, обладает ли текущий пользователь правами на все факты и размерности,
        используемые в заданном сценарии.
        Если не обладает, то генерируется ошибка.
        :param scenario_id: (str) идентификатор сценария.
        """

        successful_check = True

        # Получение используемых в сценарии мультисфер
        script_description = self.execute_manager_command(
            command_name="scripts",
            state="get_script_description",
            script_id=scenario_id,
        )
        used_cubes = self.h.parse_result(
            result=script_description, key="script", nested_key="used_cubes"
        )

        # Создание и наполнение списков с используемыми в сценарии
        # идентификаторами кубов, размерностей и фактов
        all_used_dimensions = []
        all_used_facts = []
        used_cubes_ids = []
        for cube in used_cubes:
            used_dimensions = cube.get("used_dimensions")
            used_facts = cube.get("used_facts")
            # Если сервер не возвращает список используемых размерностей или список используемых фактов,
            # то проверку считаем успешно завершенной. Если возвращает пустые списки, проверка продолжается.
            if not isinstance(used_dimensions, list) or not isinstance(
                used_facts, list
            ):
                return successful_check
            all_used_dimensions.extend(used_dimensions)
            all_used_facts.extend(used_facts)
            used_cubes_ids.append(cube["id"])

        # Получение списка доступных пользователю размерностей
        available_dims = []
        available_measures = []
        for cube_id in used_cubes_ids:
            dims_rp = self.execute_manager_command(
                command_name="user_cube", state="get_dimensions", cube_id=cube_id
            )
            dims = self.h.parse_result(result=dims_rp, key="dimensions")
            dims_ids = [dim.get("id") for dim in dims]
            available_dims.extend(dims_ids)

            # Получение списка доступных пользователю фактов
            # Если на сервере нет команды "get_measures", проверку считаем успешно завершенной
            if not self.server_codes["manager"]["command"]["user_cube"]["state"].get(
                "get_measures"
            ):
                return successful_check
            measures_rp = self.execute_manager_command(
                command_name="user_cube", state="get_measures", cube_id=cube_id
            )
            measures = self.h.parse_result(result=measures_rp, key="measures")
            measures_ids = [measure.get("id") for measure in measures]
            available_measures.extend(measures_ids)

        # Проверка, входит ли множество используемых в сценарии размерностей
        # в множество доступных пользователю размерностей
        if not set(all_used_dimensions).issubset(set(available_dims)):
            self._raise_exception(
                RightsError,
                "Not all dimensions used in a scenario are available",
                with_traceback=False,
            )

        # Проверка, входит ли множество используемых в сценарии фактов
        # в множество доступных пользователю фактов
        if not set(all_used_facts).issubset(set(available_measures)):
            self._raise_exception(
                RightsError,
                "Not all facts used in a scenario are available",
                with_traceback=False,
            )

        return successful_check

    def _get_session_layers(self) -> list:
        """
        Возвращает список слоёв сессии.
        :return: (list) список идентификаторов слоёв.
        """

        layers = self.execute_manager_command(
            command_name="user_layer", state="get_session_layers"
        )
        return self.h.parse_result(result=layers, key="layers")

    def run_scenario_impl(self, scenario_id: str, scenario_name: str):
        """
        Запуск сценария.
        """
        # Получаем идентификаторы существующих слоёв
        exists_layers = self._get_session_layers()
        exists_layer_ids = [layer.get("uuid") for layer in exists_layers]

        # Создаём новый слой, на котором будет запущен наш сценарий, и добавляем его в список существующих слоёв
        layer_uuid = self.create_layer(set_active=True)
        if not layer_uuid:
            return self._raise_exception(
                ScenarioError, "New layer hasn't been created!"
            )
        exists_layer_ids.append(layer_uuid)

        # Переименовываем слой - он будет называться также, как запускаемый сценарий
        self.execute_manager_command(
            command_name="user_layer",
            state="rename_layer",
            layer_id=layer_uuid,
            name=scenario_name,
        )

        # Запуск сценария на слое
        self.run_scenario_on_layer_impl(layer_id=layer_uuid, scenario_id=scenario_id)

        # Инициализация слоя, содержащего сценарий
        self.execute_manager_command(
            command_name="user_layer", state="init_layer", layer_id=layer_uuid
        )

        # Сохранение интерфейсных настроек
        settings = {"wm_layers2": {"lids": exists_layer_ids, "active": layer_uuid}}
        self.execute_manager_command(
            command_name="user_iface",
            state="save_settings",
            module_id=self.authorization_uuid,
            settings=settings,
        )

        # Сохранение переменных окружения
        self.layers_list = exists_layer_ids
        self.active_layer_id = layer_uuid
        layer_settings = self.execute_manager_command(
            command_name="user_layer", state="get_layer", layer_id=layer_uuid
        )
        module_descs = (
            self.h.parse_result(
                result=layer_settings, key="layer", nested_key="module_descs"
            )
            or list()
        )
        if not module_descs:
            self.set_multisphere_module_id("")
            self.cube_id = ""
        else:
            for module in module_descs:
                # берём первую по счёту мультисферу
                if module.get("type_id") == MULTISPHERE_ID:
                    self.set_multisphere_module_id(module.get("uuid", ""))
                    self.cube_id = module.get("cube_id", "")
                    break

        # Обновление числа строк активной мультисферы
        if self.multisphere_module_id:
            self.update_total_row()
        self.func_name = "run_scenario"

    @timing
    def run_scenario(
        self,
        scenario_id: str = None,
        scenario_name: str = None,
        scenario_path: str = None,
        timeout: int = None,
    ):
        """
        Запустить сценарий и дождаться его загрузки. В параметрах метода обязательно нужно указать либо идентификатор
        сценария, либо его название. И то, и то указывать не обязательно. Ничего не возвращает.
        Если по каким-то причинам невозможно дождаться загрузки выбранного сценария (не отвечает сервер Полиматики или
        сервер вернул невалидный статус), то будет сгенерирована ошибка.
        :param scenario_id: (str) идентификатор (uuid) сценария (необязательное значение, если задано название).
        :param scenario_name: (str) название сценария (необязательное значение, если задан идентификатор).
        :param scenario_path: (str) путь до сценария (необязательное значение, если задан идентификатор,
            используется только с scenario_name).
        :call_example:
            1. Инициализируем класс БЛ: bl_test = BusinessLogic(login="login", password="password", url="url")
            2. Вызов метода:
                scenario_id, scenario_name = "scenario_id or None", "scenario_name or None"
                bl_test.run_scenario(scenario_id=scenario_id, scenario_name=scenario_name)
        """
        # проверки
        try:
            self.checks(self.func_name, scenario_id, scenario_name, scenario_path)
        except Exception as e:
            return self._raise_exception(ScenarioError, str(e), with_traceback=False)

        # если пользователь прокинул тайм-аут - отобразим это в логах в виде warning
        if timeout is not None:
            self.logger.warning('Using deprecated param "timeout" in "run_scenario" method!')

        # проверка данных сценария
        scenario_id, scenario_name = self._check_scenario_data(
            scenario_id, scenario_name, scenario_path
        )

        # проверка прав на сценарий (на все ли мультисферы, участвующие в сценарии, пользователь имеет права)
        self._check_scenario_cubes_permission(scenario_id)

        # запуск сценария
        self.run_scenario_impl(scenario_id=scenario_id, scenario_name=scenario_name)

    @timing
    def run_scenario_on_layer(self, scenario_id: str, layer_id: str) -> None:
        """
        Запустить сценарий на слое. Ничего не возвращает.
        :param scenario_id: (str) Идентификатор (uuid) сценария.
        :param layer_id: (str) Идентификатор (uuid) слоя.
        """
        # проверка прав на сценарий (на все ли мультисферы, участвующие в сценарии, пользователь имеет права)
        self._check_scenario_cubes_permission(scenario_id)

        # запуск сценария
        self.run_scenario_on_layer_impl(scenario_id=scenario_id, layer_id=layer_id)

    def run_scenario_on_layer_impl(self, scenario_id: str, layer_id: str):
        """
        Запуск сценария на заданном слое
        """
        # Получаем информацию о запускаемом сценарии
        script_data = self.execute_manager_command(
            command_name="scripts",
            state="get_script_description",
            script_id=scenario_id,
        )
        script_info = self.h.parse_result(script_data, "script")

        self.execute_manager_command(
            command_name="scripts",
            state="load_on_layer",
            script_id=scenario_id,
            runtime_id=layer_id,
            on_load_action=0,
        )
        self.execute_manager_command(
            command_name="scripts",
            state="play_to_position",
            script_id=scenario_id,
            runtime_id=layer_id,
            play_to_position=script_info.get("steps_count") - 1,
            clear_workspace=True,
        )

        self._wait_scenario_loaded(layer_id)

        # сохраняем текущий слой как активный
        self.active_layer_id = layer_id

        self.func_name = "run_scenario_on_layer"

    def _wait_scenario_loaded(self, layer_id: str):
        """
        Дождаться полной загрузки сценария на слое.
        """

        def _raise(message, with_traceback=False):
            """
            Генерация исключения ScenarioError с заданным сообщением.
            """
            return self._raise_exception(
                ScenarioError, message, with_traceback=with_traceback
            )

        status_codes = {
            "Loaded": 1,
            "Running": 2,
            "Finished": 3,
            "Paused": 4,
            "Interrupted": 5,
            "Failure": 6,
        }
        need_check_progress = True
        while need_check_progress:
            # периодичностью раз в полсекунды запрашиваем результат с сервера и проверяем статус загрузки слоя
            # если не удаётся получить статус - скорее всего нет ответа от сервера - сгенерируем ошибку
            # в таком случае считаем, что сервер не ответил и генерируем ошибку
            time.sleep(0.5)
            try:
                progress = self.execute_manager_command(
                    command_name="scripts",
                    state="get_script_status",
                    runtime_id=layer_id,
                )
                status = self.h.parse_result(result=progress, key="script_status") or {}
                status_code = status.get("status", -1)
            except Exception as e:
                # если упала ошибка - не удалось получить ответ от сервера, возможно сервер недоступен
                # или отсутствует целевой слой
                return _raise(
                    f"Failed to load script! {e}", True
                )

            # проверяем код статуса
            if status_code in [status_codes.get("Loaded"), status_codes.get("Running")]:
                # сценарий в процессе воспроизведения
                need_check_progress = True
            elif status_code == status_codes.get("Finished"):
                # сценарий полностью выполнен
                need_check_progress = False
            elif status_code in [
                status_codes.get("Interrupted"),
                status_codes.get("Paused"),
            ]:
                # ошибка: сценарий прерван либо был поставлен на паузу
                return _raise("Script loading was interrupted!")
            elif status_code == status_codes.get("Failure"):
                # ошибка выполнения
                err_details = status.get("error", "Unknown error!")
                return _raise(f"Script loading was failured! Details: {err_details}")
            elif status_code == -1:
                # ошибка: не удалось получить код текущего статуса
                return _raise("Unable to get status code!")
            else:
                # прочие ошибки
                return _raise("Unknown error!")

    def _check_user_exists(self, user_name: str, users_data: list = None):
        """
        Проверка на существование пользователя с заданным именем (логином).
        Если пользователь не найден - генерируется ошибка.
        :param user_name: (str) имя (логин) пользователя.
        :param users_data: (list) список пользователей Полиматики; может быть не задан.
        """
        # получаем список пользователей
        if not users_data:
            users = self.execute_manager_command(
                command_name="user", state="list_request"
            )
            users_data = self.h.parse_result(result=users, key="users")

        # поиск соответствия заданному логину
        users_data = users_data or []
        for user in users_data:
            if user.get("login") == user_name:
                return

        # если такого пользователя нет - генерируем ошибку
        return self._raise_exception(
            UserNotFoundError,
            f'User with login "{user_name}" not found!',
            with_traceback=False,
        )

    @timing
    def run_scenario_by_user(
        self,
        scenario_name: str,
        user_name: str,
        user_password: str = None,
        units: int = UNITS_LOAD_DATA_CHUNK,
        timeout: int = None,
    ) -> Tuple:
        """
        Запустить сценарий от имени заданного пользователя и дождаться его загрузки. Если по каким-то причинам
        невозможно дождаться загрузки выбранного сценария (не отвечает сервер Полиматики или сервер вернул невалидный
        статус), то будет сгенерирована ошибка.
        :param scenario_name: (str) название сценария.
        :param user_name: (str) имя пользователя, под которым запускается сценарий.
        :param user_password: (str) пароль пользователя, под которым запускается сценарий;
            не нужно указывать, если требуется запустить сценарий под пользователем, по-умолчанию не имеющим пароля,
            например, временный пользователь.
        :param units: (int) число выгружаемых строк мультисферы (по-умолчанию 500).
        :return: (tuple) данные мультисферы и данные о колонках мультсферы (аналогично методу "get_data_frame").
        :call_example:
            1. Инициализируем класс БЛ: bl_test = BusinessLogic(login="login", password="password", url="url")
            2. Вызов метода:
                df, df_cols = bl_test.run_scenario_by_user(
                    scenario_name="scenario_name", user_name="user_name", user_password="user_password")
        """
        # создаём новую сессию под указанным пользователем, если до этого работали с другим пользователем
        sc = self.h.sc
        if self.login != user_name:
            self._check_user_exists(user_name)
            sc = BusinessLogic(
                login=user_name, url=self.base_url, password=user_password
            )

        # если пользователь прокинул тайм-аут - отобразим это в логах в виде warning
        if timeout is not None:
            self.logger.warning(
                'Using deprecated param "timeout" in "run_scenario_by_user" method!'
            )

        # получить идентификатор запускаемого сценария
        script_desc = self.get_scripts_list()
        scenario_id = sc.h.get_scenario_id_by_name(script_desc, scenario_name)

        # запуск сценария
        sc.run_scenario_impl(scenario_id=scenario_id, scenario_name=scenario_name)

        # получаем генератор, возвращающий данные по мультисфере, убиваем сессию пользователя и возвращаем результат
        gen = sc.get_data_frame(units=units)
        self.df, self.df_cols = next(gen)
        sc.logout()
        self.func_name = "run_scenario_by_user"
        return self.df, self.df_cols

    def _get_active_measure_ids(self, total_column: int = 1000) -> set:
        """
        Получение идентификаторов активных фактов (т.е. фактов, отображаемых в таблице мультисферы).
        :param total_column: общее количество колонок в мультисфере.
        :return: (set) идентификаторы активных фактов.
        """
        data = self.execute_olap_command(
            command_name="view",
            state="get",
            from_row=0,
            from_col=0,
            num_row=1,
            num_col=total_column,
        )
        top, measure_data = self.h.parse_result(data, "top"), dict()
        for item in top:
            if "fact_id" in str(item):
                measure_data = item
                break
        return {measure.get("fact_id") for measure in measure_data}

    def _prepare_data(self) -> Tuple[List[Any], int, int]:
        """
        Подготовка данных для дальнейшего получения датафрейма:
        1. Формирование колонок мультисферы с учётом вынесенных верхних размерностей.
        2. Подготовка дополнительных данных (общее число колонок, число левых/верхних размерностей, число фактов).
        :return: (List) список, содержащий список колонок: [[column_1, ..., column_N], [column_1, ..., column_N], ... ];
            количество вложенных списов зависит от наличия верхних размерностей:
            1. Если верхних размерностей нет, то будет один вложенный список: [[column_1, ..., column_N]].
            2. Если вынесено K верхних размерностей, то будет (K + 1) вложенных списков.
        :return: (int) количество верхних размерностей.
        :return: (int) количество левых размерностей.
        """
        # получаем количество колонок
        _, total_cols = self.get_row_and_col_num(
            with_total_cols=False, with_total_rows=False, with_column_names=True
        )

        # получаем количество левых и верхних размерностей
        left_dims_count, top_dims_count = self._get_left_and_top_dims_count()

        # получаем названия колонок (включая верхние размерности)
        columns_data_result = self.execute_olap_command(
            command_name="view",
            state="get_2",
            from_row=0,
            from_col=0,
            num_row=1,
            num_col=total_cols,
        )
        columns_data = self.h.parse_result(columns_data_result, "data")[
            : top_dims_count + 1
        ]

        # если нет левых размерностей - чутка корректируем данные:
        # В последней записи в columns_data содержатся названия левых размерностей и фактов;
        # Если нет левых размерностей, то данные содержат только названия фактов, что в данном случае неверно -
        # теряется очерёдность данных; поэтому добавим пустое поле (фактически это означает, что нет размерности)
        if not left_dims_count:
            columns_data[-1].insert(0, "")

        # если нет верхних размерностей - дальше делать нечего, возвращаем все данные
        if top_dims_count == 0:
            return [columns_data[0]], top_dims_count, left_dims_count

        # преобразовываем колонки к нужному виду
        columns_result = [columns_data.pop()]
        for top_columns in reversed(columns_data):
            for i, column in enumerate(top_columns):
                if not column:
                    top_columns[i] = top_columns[i - 1]
            columns_result.insert(0, top_columns)
        return columns_result, top_dims_count, left_dims_count

    @timing
    def get_data_frame(
        self,
        units: int = UNITS_LOAD_DATA_CHUNK,
        show_all_columns: bool = False,
        show_all_rows: bool = False,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Генератор, подгружающий мультисферу постранично (порциями строк).
        Подразумевается, что перед вызовом метода вся иерархия данных в мультисфере будет раскрыта,
        иначе будут возвращаться неполные данные.
        ВАЖНО: генерация строк не учитывает промежуточные и общие итоги (тоталы) по строкам и колонкам.
        :param units: (int) количество подгружаемых строк; ожидается целое положительное число больше 0;
            по-умолчанию 100.
        :param show_all_columns: (bool) установка показа всех колонок датафрейма.
        :param show_all_rows: (bool) установка показа всех строк датафрейма.
        :return: (DataFrame, DataFrame) данные мультисферы и колонки мультисферы в формате DataFrame.
        :call_example:
            1. Инициализируем класс БЛ: bl_test = BusinessLogic(login="login", password="password", url="url", **args)
            2. Этап подготовки: открываем мультисферу, выносим размерности и др. операции
            3. Раскрываем всю иерархию данных: bl_test.expand_all_dims()
            4. Собственно, сам вызов метода:
                I вариант:
                    gen = bl_test.get_data_frame(units="units")
                    df, df_cols = next(gen)
                II вариант:
                    gen = bl_test.get_data_frame(units="units")
                    for df, df_cols in gen:
                        # do something
        """
        # формируем колонки мультисферы, получаем вспомогательные данные
        columns, top_dims_count, left_dims_count = self._prepare_data()
        df_cols = pd.DataFrame(columns)

        # получаем число вызываемых строк и столбцов
        _, num_col = self.get_row_and_col_num(
            with_total_cols=False, with_total_rows=False, with_column_names=True
        )
        exec_row = units
        exec_col = num_col

        # настройки датафрейма
        if show_all_columns:
            pd.set_option("display.max_columns", None)
        if show_all_rows:
            pd.set_option("display.max_rows", None)

        row_info_result = self.execute_olap_command(
            command_name="view",
            state="get",
            from_row=0,
            from_col=0,
            num_row=exec_row,
            num_col=exec_col,
        )
        total_row = self.h.parse_result(row_info_result, "total_row") - 1

        start = 0
        while total_row >= 0:
            # если нет левых размерностей или нет данных в мультисфере, то вернём пустой датафрейм
            if left_dims_count == 0 or total_row == 0:
                yield pd.DataFrame([], columns=columns), df_cols
                total_row = -1

            total_row = total_row - units

            result = self.execute_olap_command(
                command_name="view",
                state="get_2",
                from_row=start,
                from_col=0,
                num_row=exec_row,
                num_col=exec_col,
            )
            data = self.h.parse_result(result=result, key="data")

            # реально данные (без колонок) начинаются с индекса, который учитывает наличие верхних размерностей
            df_data = data[top_dims_count + 1 :]
            if df_data:
                df = pd.DataFrame(df_data, columns=columns)
                yield df, df_cols
                start += units
            else:
                return
        return

    @timing
    def set_measure_level(self, measure_name: str, level: int) -> dict:
        """
        Установить уровень расчета сложного факта. Актуально при
        наличии трех и более левых или верхних размерностей,
        т.е. когда для основной размерности есть как минимум две вложенных.
        По-умолчанию расчёт осуществляется по первому уровню вложенности.
        :param measure_name: (str) имя факта.
        :param level: (int) уровень расчета факта (1 - по-умолчанию, 2, 3, ...).
        :return: (dict) результат выполнения команды ("fact", "set_level").
        """
        # получить словарь с размерностями, фактами и данными
        self.get_multisphere_data()

        # получить id факта
        measure_id = self.h.get_measure_or_dim_id(
            self.multisphere_data, "facts", measure_name
        )

        # получить параметр horizontal (направление расчёта) для факта
        horizontal = next(
            fact.get("horizontal")
            for fact in self.multisphere_data.get("facts")
            if fact["id"] == measure_id
        )

        # провека значения уровня и количества вынесенных размерностей
        left_dims_count, top_dims_count = self._get_left_and_top_dims_count()
        try:
            self.checks(
                self.func_name, level, left_dims_count, top_dims_count, horizontal
            )
        except Exception as e:
            return self._raise_exception(ValueError, str(e), with_traceback=False)

        # выполнить команду: fact, state: set_level
        result = self.execute_olap_command(
            command_name="fact",
            state="set_level",
            fact=measure_id,
            level=level,
        )
        return result

    @timing
    def set_measure_precision(
        self, measure_names: List[str], precision: List[int]
    ) -> dict:
        """
        Установить точность отображения факта (фактов) (количество знаков после разделителя).
        :param measure_names: (List[str]) список с именами фактов в формате строки.
        :param precision: (List[int]) список с точностями фактов в формате int
                                (значения должны соответствовать значениям списка measure_names).
        :return: (dict) результат выполнения команды: user_iface, state: save_settings
        :call_example:
            1. Инициализируем класс бизнес-логики: client = BusinessLogic(login="login", password="password", url="url")
            2. Вызов метода:
                client.set_measure_precision(measure_names=["Сумма", "Количество товара"], precision=[1, 3])
                или client.set_measure_precision(measure_names=["Сумма"], precision=[0])
        """
        # проверки

        try:
            self.checks(self.func_name, measure_names, precision)
        except Exception as e:
            return self._raise_exception(ValueError, str(e), with_traceback=False)

        # получить словарь с размерностями, фактами и данными
        self.get_multisphere_data()

        # получить id фактов
        measure_ids = []
        for measure_name in measure_names:
            measure_id = self.h.get_measure_or_dim_id(
                self.multisphere_data, "facts", measure_name
            )
            measure_ids.append(measure_id)

        # загрузить настройки отображения фактов
        loaded_settings = self.execute_manager_command(
            command_name="user_iface",
            state="load_settings",
            module_id=self.multisphere_module_id,
        )
        settings = self.h.parse_result(result=loaded_settings, key="settings")

        # заполнить настройки отображения фактов
        if "factsPrecision" not in settings:
            settings["factsPrecision"] = {}
        if "config_storage" not in settings:
            settings["config_storage"] = {"facts-format": {"__suffixes": {}}}
        if "facts-format" not in settings["config_storage"]:
            settings["config_storage"]["facts-format"] = {"__suffixes": {}}
        if "__suffixes" not in settings["config_storage"]["facts-format"]:
            settings["config_storage"]["facts-format"]["__suffixes"] = {}

        for idx, f_id in enumerate(measure_ids):
            settings["factsPrecision"][f_id] = str(precision[idx])
            settings["config_storage"]["facts-format"]["__suffixes"][f_id] = {
                "precision": str(precision[idx])
            }

        # выполнить команду: user_iface, state: save_settings
        save_settings_rp = self.execute_manager_command(
            command_name="user_iface",
            state="save_settings",
            module_id=self.multisphere_module_id,
            settings=settings,
        )
        return save_settings_rp

    @timing
    def set_measure_format(
        self,
        measure_names: List[str],
        measure_formats: List[dict],
        set_to_default: bool = False,
    ) -> dict:
        """
        Установить настройки формата для факта.
        :param measure_names: (List[str]) - список с именами фактов в формате строки.
        :param measure_formats: (List[dict]) - список словарей с настройками формата для каждого факта.
                        Пример формата:
                        [
                            {"precision": 2,
                             "delim": ",",
                             "prefix": "a",
                             "suffix": "@@@",
                             "split": True,
                             "measureUnit": "thousand",
                             "color": "#FF0000"},
                            {"precision": 3,
                             "delim": "."}
                        ], где
                        precision (int) - точность факта (количество знаков после разделителя), число от 0 до 9,
                        delim (str) - разделитель целой и дробной части, допустимы точка, запятая, пробел,
                        prefix (str) - префикс перед значением факта, добавляет указанное
                                значение перед значением факта, например, «₽ <значение факта>»
                        suffix (str) - суффикс после значения факта, добавляет указанное
                                значение после значения факта, например, «<значение факта> руб.»
                        split (bool) - разделять ли на разряды, в случае True факт будет представлен
                                как 100 000 000, в случае False как 100000000,
                        measureUnit (str) - разрядность отображения факта (тысячи, миллионы, миллиарды). Если этот
                                параметр применен, то значение факта при этом автоматически пересчитывается, чтобы
                                удовлетворять выбранной разрядности (так, 5 000 000 будет отображаться как «5»
                                при выборе группы разрядов «Миллионы»), а также отображается рядом с названием
                                факта в мультисфере (например, «Заявка млн.»)
                                Допустимые значения: "", "thousand", "million", "billion", то есть соответственно
                                отображать факт "как есть", в тысячах, в миллионах, в миллиардах.
                        color (str) - цвет факта в формате "#RRGGBB",
                        Ни один параметр не является обязательным.
                        Если параметр set_to_default = True, то measure_formats не учитывается,
                        необходимо передать measure_formats=[]
        :param set_to_default: (bool) - параметр для применения стандартных настроек формата. По дефолту False.
                        Если True, то применяются стандартные настройки формата:
                        {"precision": 2,
                         "delim": ".",
                         "prefix": "",
                         "suffix": "",
                         "split": True,
                         "measureUnit": "",
                         "color": "#141414"}
        :return: (dict) результат выполнения команды: user_iface, state: save_settings.
        :call_example:
            1. Инициализируем класс бизнес-логики: client = BusinessLogic(login="login", password="password", url="url")
            2. Вызов метода:
                        client.set_measure_format(measure_names=["Сумма", "Количество товара"],
                                                  measure_formats=[{"precision": 3, "suffix": "q", "color": "#FF0000"},
                                                                   {"prefix": "мин", "color": "#FFFFFF"}])
                        или
                        client.set_measure_format(measure_names=["Сумма"],
                                                  measure_formats=[],
                                                  set_to_default=True)
        """
        default_settings = {
            "precision": 2,
            "delim": ".",
            "prefix": "",
            "suffix": "",
            "split": True,
            "measureUnit": "",
            "color": "#141414",
        }

        # Проверки
        params = validate_params(
            SetMeasuresParams,
            self._raise_exception,
            measure_names=measure_names,
            measure_formats=measure_formats,
            set_to_default=set_to_default,
        )
        measure_names, measure_formats, set_to_default = (
            params.measure_names,
            params.measure_formats,
            params.set_to_default,
        )

        try:
            if not set_to_default:
                extracted_settings = {key: [] for key in FORMAT_SETTINGS_KEYS}
                for format_settings in measure_formats:
                    for key in FORMAT_SETTINGS_KEYS:
                        if key in format_settings:
                            extracted_settings[key].append(format_settings[key])
                self.checks(
                    self.func_name,
                    measure_names,
                    measure_formats,
                    extracted_settings,
                )
        except Exception as e:
            return self._raise_exception(ValueError, str(e), with_traceback=False)

        # Получить словарь с размерностями, фактами и данными
        self.get_multisphere_data()

        # Получить id фактов
        measure_ids = []
        for measure_name in measure_names:
            measure_id = self.h.get_measure_or_dim_id(
                self.multisphere_data, "facts", measure_name
            )
            measure_ids.append(measure_id)

        # Загрузить текущие настройки
        loaded_settings = self.execute_manager_command(
            command_name="user_iface",
            state="load_settings",
            module_id=self.multisphere_module_id,
        )
        settings = self.h.parse_result(result=loaded_settings, key="settings")

        # заполнить настройки отображения фактов
        if "factsPrecision" not in settings:
            settings["factsPrecision"] = {}
        if "config_storage" not in settings:
            settings["config_storage"] = {"facts-format": {"__suffixes": {}}}
        if "facts-format" not in settings["config_storage"]:
            settings["config_storage"]["facts-format"] = {"__suffixes": {}}
        if "__suffixes" not in settings["config_storage"]["facts-format"]:
            settings["config_storage"]["facts-format"]["__suffixes"] = {}

        # Заполнить настройки для каждого факта
        for idx, f_id in enumerate(measure_ids):
            if set_to_default:
                measure_input_settings = default_settings
            else:
                measure_input_settings = measure_formats[idx]

            measure_loaded_settings = settings["config_storage"]["facts-format"][
                "__suffixes"
            ].get(f_id, {})

            # Обновить настройки формата
            for key, value in measure_input_settings.items():
                if key == "precision":
                    measure_loaded_settings[key] = str(value)
                    settings["factsPrecision"][f_id] = str(value)
                else:
                    measure_loaded_settings[key] = value

            settings["config_storage"]["facts-format"]["__suffixes"][
                f_id
            ] = measure_loaded_settings
        # Сохранить настройки
        save_settings_rp = self.execute_manager_command(
            command_name="user_iface",
            state="save_settings",
            module_id=self.multisphere_module_id,
            settings=settings,
        )
        return save_settings_rp

    @timing
    def get_measure_format(
        self, measure_names: List[str] = None, return_id: bool = False
    ) -> Dict[str, dict]:
        """
        Возвращает настройки формата для фактов.
        :param measure_names: (List[str]) - список с именами фактов в формате строки. Если не задан,
            то вернутся настройки для всех фактов в текущей (активной) мультисфере.
        :param return_id: (bool), по умолчанию False - возвращать ли в ответе id факта вместо имени факта
            (см. пример ответа)
        :return: словарь с настройками формата для каждого факта, где ключ - имя факта (или id факта,
            если return_id = True, а значение - словарь с настройками формата.
                        Пример ответа:
                        {
                         "Сумма":
                                 {"precision": 2,
                                  "delim": ",",
                                  "prefix": "a",
                                  "suffix": "@@@",
                                  "split": True,
                                  "measureUnit": "thousand",
                                  "color": "#FF0000"},
                         "Количество товара":
                                 {"precision": 3,
                                  "delim": ",",
                                  "prefix": "",
                                  "suffix": "",
                                  "split": True,
                                  "measureUnit": "thousand",
                                  "color": "#FF0000"}
                         }, где
                        precision (int) - точность факта (количество знаков после разделителя), число от 0 до 9,
                        delim (str) - разделитель целой и дробной части, допустимы точка, запятая, пробел,
                        prefix (str) - префикс перед значением факта, добавляет указанное
                                значение перед значением факта, например, «₽ <значение факта>»
                        suffix (str) - суффикс после значения факта, добавляет указанное
                                значение после значения факта, например, «<значение факта> руб.»
                        split (bool) - разделять ли на разряды, в случае True факт будет представлен
                                как 100 000 000, в случае False как 100000000,
                        measureUnit (str) - разрядность отображения факта (тысячи, миллионы, миллиарды). Если этот
                                параметр применен, то значение факта при этом автоматически пересчитывается, чтобы
                                удовлетворять выбранной разрядности (так, 5 000 000 будет отображаться как «5»
                                при выборе группы разрядов «Миллионы»), а также отображается рядом с названием
                                факта в мультисфере (например, «Заявка млн.»)
                                Допустимые значения: "", "thousand", "million", "billion", то есть соответственно
                                отображать факт "как есть", в тысячах, в миллионах, в миллиардах.
                        color (str) - цвет факта в формате "#RRGGBB",

                        Пример ответа при return_id = True:
                        {
                         "6eb3d949":
                                 {"precision": 2,
                                  "delim": ",",
                                  "prefix": "a",
                                  "suffix": "@@@",
                                  "split": True,
                                  "measureUnit": "thousand",
                                  "color": "#FF0000"},
                         "b1cca2de":
                                 {"precision": 3,
                                  "delim": ",",
                                  "prefix": "",
                                  "suffix": "",
                                  "split": True,
                                  "measureUnit": "thousand",
                                  "color": "#FF0000"}
                         }

        :call_example:
            1. Инициализируем класс бизнес-логики: client = BusinessLogic(login="login", password="password", url="url")
            2. Вызов метода:
                        client.get_measure_format(measure_names=["Сумма", "Количество товара"])
                        или
                        client.get_measure_format(measure_names=["Сумма"],
                                                  return_id=True)
        """
        default_settings = {
            "precision": 2,
            "delim": ".",
            "prefix": "",
            "suffix": "",
            "split": True,
            "measureUnit": "",
            "color": "#141414",
        }

        # Проверки
        params = validate_params(
            GetMeasuresParams,
            self._raise_exception,
            measure_names=measure_names,
            return_id=return_id,
        )
        measure_names, return_id = params.measure_names, params.return_id

        # Получить словарь с размерностями, фактами и данными
        self.get_multisphere_data()

        # Если measure_names не задан, получить все имена фактов из мультисферы
        if not measure_names:
            measure_names = [fact["name"] for fact in self.multisphere_data["facts"]]

        # Получить id фактов
        measure_ids = {}
        for measure_name in measure_names:
            measure_id = self.h.get_measure_or_dim_id(
                self.multisphere_data, "facts", measure_name
            )
            measure_ids[measure_id] = measure_name

        # Загрузить текущие настройки
        loaded_settings = self.execute_manager_command(
            command_name="user_iface",
            state="load_settings",
            module_id=self.multisphere_module_id,
        )
        settings = self.h.parse_result(result=loaded_settings, key="settings")
        measures_formats = (
            settings.get("config_storage", {})
            .get("facts-format", {})
            .get("__suffixes", {})
        )

        # Заполнить настройки фактов (если какие-то настройки не загружены, то взять их из дефолтных настроек)
        result = {}
        for measure_id in measure_ids:
            measure_loaded_settings = measures_formats.get(measure_id, {})
            measure_settings = {
                k: measure_loaded_settings.get(k, default_settings[k])
                for k in default_settings
            }

            result[
                measure_id if return_id else measure_ids[measure_id]
            ] = measure_settings

        return result

    def _get_olap_module_id(
        self, module: str = "", set_active_layer: bool = True
    ) -> str:
        """
        Возвращает идентификатор OLAP-модуля.
        Если идентификатор модуля задан пользователем, то пытаемся найти его;
            в случае, если не найден - бросаем исключение.
        Если пользователем не задан идентификатор модуля, то возвращаем идентификатор текущего (активного) модуля;
            в случае, если его нет - бросаем исключение.
        :param module: название/идентификатор искомого модуля; если не задан пользователем, то None.
        :param set_active_layer: нужно ли обновлять идентификатор активного слоя (по-умолчанию нужно).
        :return: (str) uuid найденного OLAP-модуля.
        """
        if module:
            # ищем указанный пользователем модуль и сохраняем его идентификатор
            module_ids = self._find_olap_module(module)
            if not module_ids:
                error_msg = f'OLAP-module "{module}" not found!'
                return self._raise_exception(
                    OLAPModuleNotFoundError, error_msg, with_traceback=False
                )
            layer_id, result_module_id = module_ids[0]
        else:
            # пользователем не задан конкретный модуль - возвращаем текущий активный идентификатор OLAP-модуля
            if not self.multisphere_module_id:
                error_msg = "No active OLAP-modules!"
                return self._raise_exception(
                    OLAPModuleNotFoundError, error_msg, with_traceback=False
                )
            result_module_id, set_active_layer, layer_id = (
                self.multisphere_module_id,
                False,
                "",
            )

        # обновляем идентификатор активного слоя
        if layer_id and set_active_layer:
            self.active_layer_id = layer_id

        return result_module_id

    @timing
    def clone_olap_module(
        self,
        module: str = "",
        set_focus_on_copied_module: bool = False,
        copied_module_name: str = "",
    ) -> Tuple[str, str]:
        """
        Создать копию указанного OLAP-модуля. Если модуль явно не задан - копируется текущий OLAP-модуль.
        :param module: (str) название/идентификатор клонируемого OLAP-модуля;
            если модуль указан, но такого нет - сгенерируется исключение;
            если модуль не указан, то берётся текущий (активный) модуль (если его нет - сгенерируется исключение).
        :param set_focus_on_copied_module: (bool) нужно ли устанавливать фокус на новый (скопированный) OLAP-модуль;
            по-умолчанию фокус остаётся на исходном OLAP-модуле.
        :param copied_module_name: (str) название скопированного OLAP-модуля; если не задано, то скопированному модулю
            будет присвоено название по-умолчанию: "название_основного_модуля Копия #N", где N - порядковый номер копии;
            задаваемое название должно быть уникальным для всех клонов определённого OLAP-модуля.
        :return: (str) идентификатор нового (скопированного) OLAP-модуля.
        :return: (str) название нового (скопированного) OLAP-модуля.
        :call_example:
            1. Инициализируем класс:
                sc = business_scenarios.BusinessLogic(login="login", password="password", url="url")
            2. Открываем произвольный куб:
                sc.get_cube("cube_name")
            3. Копирование текущего (активного) OLAP-модуля:
                new_module_uuid, new_module_name = sc.clone_olap_module()
            4. Копирование модуля с заданным идентификатором/названием:
                new_module_uuid, new_module_name = sc.clone_olap_module(module="module_id_or_name")
            5. Копирование модуля с передачей флага "set_focus_on_copied_module":
                new_module_uuid, new_module_name = sc.clone_olap_module(set_focus_on_copied_module=True)
            6. Копирование модуля с передачей имени скопированного окна:
                new_module_uuid, new_module_name = sc.clone_olap_module(copied_module_name="new_name")
        """
        # проверки
        try:
            self.checks(
                self.func_name,
                module,
                set_focus_on_copied_module,
                copied_module_name,
            )
        except Exception as e:
            return self._raise_exception(ValueError, str(e), with_traceback=False)

        # получаем идентификатор клонируемого модуля
        cloned_module_id = self._get_olap_module_id(module)

        # если параметр copied_module_name не задан, то получаем имя клонируемого OLAP-модуля,
        # т.к. на основе этого имени будет составляться имя копии OLAP-модуля
        # а если задан - проверяем на уникальность
        cloned_module_name = ""
        if not copied_module_name:
            layer_settings = self.execute_manager_command(
                command_name="user_layer",
                state="get_layer",
                layer_id=self.active_layer_id,
            )
            layer_info = (
                self.h.parse_result(result=layer_settings, key="layer") or dict()
            )

            for module in layer_info.get("module_descs"):
                if module.get("uuid") != cloned_module_id:
                    continue

                module_setting = self.execute_manager_command(
                    command_name="user_iface",
                    state="load_settings",
                    module_id=cloned_module_id,
                )
                module_info = (
                    self.h.parse_result(result=module_setting, key="settings") or dict()
                )
                module_title = module_info.get("title", "")

                if module_title:
                    cloned_module_name = module_title
                else:
                    cubes = self.get_cubes_list()
                    for cube in cubes:
                        if cube.get("uuid") == module.get("cube_id"):
                            cloned_module_name = self._form_olap_module_name(
                                cube.get("name")
                            )
                            break
        else:
            copied_names = self.copied_names.get(cloned_module_id, set())
            if copied_module_name in copied_names:
                error_msg = f'Copy named "{copied_module_name}" already exists for module with ID "{cloned_module_id}"!'
                return self._raise_exception(ValueError, error_msg)
            self.set_copied_names = (cloned_module_id, copied_module_name)

        # клонирование OLAP-модуля
        result = self.execute_manager_command(
            command_name="user_iface",
            state="clone_module",
            module_id=cloned_module_id,
            layer_id=self.active_layer_id,
        )
        copied_module_id = self.h.parse_result(
            result=result, key="module_desc", nested_key="uuid"
        )
        self.set_counter = cloned_module_id

        # составляем имя копии и устанавливаем его
        copied_module_name = (
            copied_module_name
            if copied_module_name
            else f"{cloned_module_name} Копия #{self.copied_counter.get(cloned_module_id)}"
        )
        self.set_olap_module_name(copied_module_id, copied_module_name)

        # переключиться на созданную копию OLAP-модуля, если это нужно
        if set_focus_on_copied_module:
            self.set_multisphere_module_id(copied_module_id)

        # возвращаем идентификатор нового OLAP-модуля и его название
        self.func_name = "clone_olap_module"
        return copied_module_id, copied_module_name

    def _form_olap_module_name(self, cube_name: str) -> str:
        """
        Формирование названия OLAP-модуля по названию куба. При формировании учитывается заданная локализация.
        :param cube_name: (str) название куба.
        :return: (str) название OLAP-модуля с учётом заданной локализации.
        """
        return "{} - {}".format(
            "Мультисфера" if self.language == "ru" else "Multisphere", cube_name
        )

    def _form_graph_module_name(self, cube_name: str) -> str:
        """
        Формирование названия модуля графиков по названию куба. При формировании учитывается заданная локализация.
        :param cube_name: (str) название куба.
        :return: (str) название модуля графиков с учётом заданной локализации.
        """
        return f"{'График' if self.language == 'ru' else 'Graph'} - {cube_name}"

    @timing
    def set_olap_module_name(self, olap_module_id: str, new_module_name: str):
        """
        Изменение названия OLAP-модуля. Ничего не возвращает, но может сгенерировать исключение.
        :param olap_module_id: (str) идентификатор OLAP-модуля;
            если такого модуля не существует, будет сгенерирована ошибка.
        :param new_module_name: (str) новое название OLAP-модуля.
        """
        # проверяем, существует ли такой модуль
        module_ids = self._find_olap_module(olap_module_id)
        if not module_ids:
            error_msg = f'OLAP-module with ID "{olap_module_id}" not found!'
            return self._raise_exception(ValueError, error_msg, with_traceback=False)

        _, module_id = module_ids[0]
        # создаём запрос на переименование и исполняем его
        commands = [
            self.manager_command.collect_command(
                module="manager",
                command_name="user_iface",
                state="save_settings",
                module_id=module_id,
                settings={"title": new_module_name},
            ),
            self.manager_command.collect_command(
                module="manager",
                command_name="user_iface",
                state="rename_module",
                module_id=module_id,
                module_name=new_module_name,
            ),
        ]
        query = self.olap_command.collect_request(*commands)
        self.exec_request.execute_request(query)

    @timing
    def set_measure_visibility(
        self, measure_names: Union[str, List], is_visible: bool = False
    ) -> List:
        """
        Изменение видимости факта (скрыть/показать факт). Можно изменять видимость одного факта или списка фактов.
        :param measure_names: (Union[str, List]) название факта либо список фактов.
        :param is_visible: (bool) скрыть (False) либо показать (True) факт. По-умолчанию факт скрывается.
        :return: (List) список идентификаторов фактов с изменной видимостью.
        """
        # проверки
        params = validate_params(
            SetMeasureVisibilityParams,
            self._raise_exception,
            measure_names=measure_names,
            is_visible=is_visible,
        )
        measure_names, is_visible = params.measure_names, params.is_visible

        # список фактов с измененной видимостью
        measure_ids = []

        if isinstance(measure_names, str):
            # если передан один факт (строка)
            m_id = self.get_measure_id(measure_name=measure_names)
            self.execute_olap_command(
                command_name="fact",
                state="set_visible",
                fact=m_id,
                is_visible=is_visible,
            )
            measure_ids.append(m_id)
        elif isinstance(measure_names, list):
            # если передан список фактов
            all_measures = self._get_measures_list()
            all_measure_names = {measure.get("name") for measure in all_measures}
            measure_names_set = set(measure_names)
            missing_measures = measure_names_set - all_measure_names
            if missing_measures:
                self.logger.warning(f"{len(missing_measures)} measure(s) not found: {', '.join(missing_measures)}")
            measure_ids = [measure.get("id") for measure in all_measures if measure.get("name") in measure_names]
            self.execute_olap_command(
                command_name="fact",
                state="set_visible_multi",
                fact_ids=measure_ids,
                is_visible=is_visible,
            )
        else:
            return self._raise_exception(
                ValueError, 'Param "measure_names" must be "str" or "list" type!'
            )
        self.func_name = "set_measure_visibility"
        return measure_ids

    @timing
    def set_all_measure_visibility(
        self, is_visible: bool = True, multisphere_module_id: str = ""
    ) -> List:
        """
        Показать/скрыть все факты мультисферы.
        ВАЖНО: скрыть вообще все факты мультисферы нельзя, поэтому, если пользователем была передана команда
        скрыть все факты мультисферы, то будут скрыты все факты, кроме самого первого.
        :param is_visible: скрыть (False) либо показать (True) факты. По-умолчанию факты показываются.
        :param multisphere_module_id: идентификатор OLAP-модуля;
            если модуль указан, но такого нет - сгенерируется исключение;
            если модуль не указан, то берётся текущий (активный) модуль (если его нет - сгенерируется исключение).
        :return: идентификаторы показанных/скрытых фактов (в зависимости от команды).
        """
        # проверка
        try:
            self.checks(self.func_name, is_visible)
        except Exception as e:
            return self._raise_exception(ValueError, str(e), with_traceback=False)

        # получаем идентификатор OLAP-модуля
        module_id = self._get_olap_module_id(multisphere_module_id)
        self.set_multisphere_module_id(module_id)

        # получаем данные мультисферы (в т.ч. список фактов)
        m_data = self.get_multisphere_data()
        ids = list()
        for i, measure in enumerate(m_data.get("facts", list())):
            # если выполняется скрытие фактов, то самый первый факт не трогаем,
            # т.к. в мультисфере должен остаться хотя бы один нескрытый факт
            if not is_visible and i == 0:
                continue
            m_id = measure.get("id")
            self.execute_olap_command(
                command_name="fact",
                state="set_visible",
                fact=m_id,
                is_visible=is_visible,
            )
            ids.append(m_id)
        return ids

    @timing
    def sort_measure(
        self, measure_name: str, sort_type: str, path: List[str] = None
    ) -> dict:
        """
        Сортировка значений указанного факта по возрастанию/убыванию.
        Необходимым условием сортировки является наличие хотя бы одной вынесенной влево размерности.
        Если задан параметр path, то сортировка будет производиться по столбцу,
        путь до которого указан в этом параметре. Верхние размерности должны быть развернуты,
        это можно сделать командой "expand_all_up_dims".
        Если параметр path не задан, то сортировка будет производиться по столбцу "Всего", и вынесенные
        вверх размерности необходимо свернуть перед вызовом метода.
        Это можно сделать командой "collap_all_up_dims".
        :param measure_name: название факта.
        :param sort_type: "ascending"/"descending"/"off" (по возрастанию/по убыванию/выключить сортировку).
        :param path: путь до столбца, содержит имена элементов верхних размерностей,
            пример ['Простуда и грипп', 'Гастрацид'] - для двух верхних размерностей, также возможно указать
            колонку "Всего" в пути, то есть ["Простуда и грипп", "Всего"]
        :return: (dict) результат команды ("view", "set_sort").
        """
        # проверки
        int_sort_type = self.checks(self.func_name, sort_type)

        # получаем данные о расположении колонки "Всего". Если top_total_transfer = False - то в конце таблицы,
        # если True, то первым столбцом
        module_configuration = self.execute_olap_command(
            command_name="view", state="get_module_configuration"
        )
        top_total_transfer = self.h.parse_result(
            module_configuration, "top_total_transfer"
        )
        # получаем данные по фактам, а также количество левых размерностей
        result = self.execute_olap_command(
            command_name="view", state="get", from_row=0, from_col=0, num_row=1
        )

        # проверяем количество левых размерностей
        left_dims_count = len(self.h.parse_result(result, "left_dims") or [])
        if left_dims_count == 0:
            return self._raise_exception(PolymaticaException, "No left dimensions!")

        # извлекаем все колонки с фактами
        top = self.h.parse_result(result, "top")

        measure_id = self.get_measure_id(measure_name)

        # находим номер колонки
        try:
            if not path:
                measures = []
                for i in top:
                    for elem in i:
                        if "fact_id" in elem:
                            measures.append(elem["fact_id"])
                line = (
                    measures.index(measure_id)
                    if top_total_transfer
                    else len(measures) - 1 - measures[::-1].index(measure_id)
                )
            else:
                line = self._find_column_index(top, path, measure_id)
        except ValueError:
            return self._raise_exception(
                ValueError, f'Measure "{measure_name}" must be visible!'
            )

        if path and line is None:
            return self._raise_exception(
                ValueError, f"Path {path} is invalid! All top dims must be expanded!"
            )

        self.func_name = "sort_measure"
        return self.execute_olap_command(
            command_name="view", state="set_sort", line=line, sort_type=int_sort_type
        )

    @staticmethod
    def _find_column_index(
        top: Dict, path: List[str], measure_id: str
    ) -> Optional[int]:
        acceptable_indieces = set(range(len(top[0])))
        value_index = len(top[0]) + 1
        for depth, expected_value in enumerate(path):
            row = top[depth]
            acceptable_indieces_row = set()

            for index_cell, cell in enumerate(row):
                if (
                    expected_value == "Всего"
                    and cell.get("type") == 5
                    and index_cell in acceptable_indieces
                ):
                    acceptable_indieces_row.add(index_cell)
                    value_index = index_cell
                elif cell.get("value") == expected_value:
                    if index_cell in acceptable_indieces:
                        value_index = index_cell
                        acceptable_indieces_row.add(index_cell)
                elif cell.get("type") in (1, 5) and index_cell >= value_index:
                    if index_cell in acceptable_indieces:
                        acceptable_indieces_row.add(index_cell)
                elif (
                    cell.get("value") != expected_value
                    and cell.get("type") in (2, 3)
                    and acceptable_indieces_row
                ):
                    break
            acceptable_indieces = acceptable_indieces_row
            value_index = len(top[0]) + 1

        # находим факт в ряду фактов и возвращаем его индекс
        for index in sorted(acceptable_indieces):
            measure_cell = top[-1][index]
            if (
                measure_cell.get("type") == 4
                and measure_cell.get("fact_id") == measure_id
            ):
                return index
        return None

    def _get_left_and_top_dims_count(
        self, level: int = None, position: int = None
    ) -> Tuple[int, int]:
        """
        Возвращает количество левых и верхних размерностей мультисферы.
        Если передан параметр level, то также осуществляется проверка уровня левых/верхних размерностей:
        если level больше, чем количество раскрываемых (т.е. иерархических) размерностей - сгенерируется ошибка.
        Если передан параметр level, то должен быть передан и параметр position, и наоборот.
        :param level: (int) уровень размерности.
        :param position: (int) 1 - левые размерности, 2 - верхние размерности.
        :return: (int) число левых размерностей.
        :return: (int) число верхних размерностей.
        """
        # получаем данные
        dims_data_result = self.execute_olap_command(
            command_name="view",
            state="get",
            from_row=0,
            from_col=0,
            num_row=1,
            num_col=1,
        )
        left_dims_count = len(self.h.parse_result(dims_data_result, "left_dims") or [])
        top_dims_count = len(self.h.parse_result(dims_data_result, "top_dims") or [])

        # проверки
        if level is not None and position is not None:
            # проверка на то, что есть хотя бы одна вынесенная размерность
            if left_dims_count == 0 and top_dims_count == 0:
                return self._raise_exception(ValueError, "No left/up dims!")

            # проверка на уровень
            checked_level = left_dims_count if position == 1 else top_dims_count
            # т.к. последняя размерность мультисферы не имеет возможности расширяться
            checked_level -= 1
            # а в проверке указано (checked_level - 1) т.к. индексацию ведём с нуля
            if level > checked_level - 1:
                if checked_level == 0:
                    error_msg = "No dimensions available for expand!"
                else:
                    error_msg = f"{checked_level} dimensions available for expand!"
                return self._raise_exception(ValueError, f"Invalid level! {error_msg}")

        # вернём число левых и верхних размерностей
        return left_dims_count, top_dims_count

    @timing
    def unfold_all_dims(self, position: str, level: int, **kwargs) -> dict:
        """
        Развернуть все элементы размерности до заданного уровня иерархии.
        :param position: (str) "left" / "up" (левые / верхние размерности).
        :param level: (int) 0, 1, 2, ... (считается слева-направо для левой размерности, сверху - вниз для верхней).
        :param num_row: (int) Количество строк, которые будут отображаться в мультисфере.
        :param num_col: (int) Количество колонок, которые будут отображаться в мультисфере.
        :return: (dict) after request view get_hints
        """
        # проверки
        try:
            position = self.checks(self.func_name, position, level)
            left_dims_count, top_dims_count = self._get_left_and_top_dims_count(
                level, position
            )
        except Exception as e:
            return self._raise_exception(ValueError, str(e), with_traceback=False)

        # формируем запрос на раскрытие узлов ...
        arrays_dict = []
        # для того, чтобы развернуть все узлы заданного уровня, нужно развернуть все узлы до заданного уровня
        # для этого цикл и нужен
        for i in range(0, level + 1):
            arrays_dict.append(
                self.olap_command.collect_command(
                    module="olap",
                    command_name="view",
                    state="fold_all_at_level",
                    position=position,
                    level=i,
                )
            )
        query = self.olap_command.collect_request(*arrays_dict)

        # ... и исполняем его
        try:
            self.exec_request.execute_request(query)
        except Exception as e:
            return self._raise_exception(PolymaticaException, str(e))

        # формируем запрос на показ хинтов ...
        hints_command = []
        if left_dims_count:
            hints_command.append(
                self.olap_command.collect_command(
                    module="olap",
                    command_name="view",
                    state="get_hints",
                    position=1,
                    hints_num=100,
                )
            )
        if top_dims_count:
            hints_command.append(
                self.olap_command.collect_command(
                    module="olap",
                    command_name="view",
                    state="get_hints",
                    position=2,
                    hints_num=100,
                )
            )
        query = self.olap_command.collect_request(*hints_command)

        # ... и исполняем его
        try:
            result = self.exec_request.execute_request(query)
        except Exception as e:
            return self._raise_exception(PolymaticaException, str(e))

        # обновляем число строк мультисферы;
        # без этой операции не обойтись, т.к. при разворачивании иерархии число строк меняется
        self.update_total_row()
        return result

    @timing
    def move_measures(self, new_order: List):
        """
        Упорядочивание фактов в заданной последовательности.
        Пример вызова: sc.move_measures(new_order=["факт1", "факт2", "факт3", "факт4"]).
        :param new_order: (List) список упорядоченных фактов.
        """

        measures_data = self._get_measures_list()
        measure_name_id_dict = {
            measure["name"]: measure["id"] for measure in measures_data
        }

        new_measure_ids_list = []
        for new_measure_name in new_order:
            new_measure_id = measure_name_id_dict[new_measure_name]
            new_measure_ids_list += [new_measure_id]

        try:
            self.execute_olap_command(
                command_name="fact",
                state="set_calculation_order_request",
                measures=new_measure_ids_list,
            )
        except Exception as ex:
            return self._raise_exception(PolymaticaException, str(ex))

        self.func_name = "move_measures"

    @timing
    def set_width_columns(
        self, measures: List, left_dims: List, width: int = 890, height: int = 540
    ) -> dict:
        """
        Установить ширину колонок в текущем (активном) модуле. Под колонками подразумеваются как левые размерности,
        так и факты.
        :param measures: (List) список новых значений ширины фактов.
            ВАЖНО! Длина списка должна совпадать с количеством нескрытых фактов в мультисфере без учёта верхних
            размерностей. То есть:
                1. Если в мультисфере нет вынесенных вверх размерностей, то длина списка должна совпадать с
                количеством нескрытых фактов в мультисфере.
                2. Если в мультисфере есть вынесенные вверх размерности, то длина списка должна совпадать с
                количеством уникальных (не дублирующихся из-за верхних размерностей) нескрытых фактов в мультисфере.
        :param left_dims: (List) список новых значений ширины вынесенных влево размерностей.
            ВАЖНО! Длина списка должна совпадать с количеством реально вынесенных влево размерностей мультисферы!
        :param width: (int) ширина мультисферы.
        :param height: (int) высота мультисферы.
        :return: Команда ("user_iface", "save_settings").
        """
        result = self.execute_olap_command(
            command_name="view",
            state="get",
            from_row=0,
            from_col=0,
            num_row=20,
            num_col=20,
        )

        # получить список левых размерностей
        left_dims_data = self.h.parse_result(result=result, key="left_dims")

        # получить список нескрытых фактов (без учёта верхних размерностей)
        measures_data = self.h.parse_result(result=result, key="top")
        measures_ids = set()
        for i in measures_data:
            for elem in i:
                if "fact_id" in elem:
                    measures_ids.add(elem["fact_id"].rstrip())

        # проверки
        try:
            self.checks(
                self.func_name, measures, measures_ids, left_dims, left_dims_data
            )
        except Exception as e:
            return self._raise_exception(
                PolymaticaException, str(e), with_traceback=False
            )

        # сохраняем новые настройки
        settings = {
            "dimAndFactShow": True,
            "itemWidth": measures,
            "geometry": {"width": width, "height": height},
            "workWidths": left_dims,
        }
        return self.execute_manager_command(
            command_name="user_iface",
            state="save_settings",
            module_id=self.multisphere_module_id,
            settings=settings,
        )

    def _get_profiles(self) -> dict:
        """
        Получение списка профилей.
        :return: (dict) список профилей, полученный командой ("user_layer", "get_saved_layers").
        """
        profiles_data = self.execute_manager_command(
            command_name="user_layer", state="get_saved_layers"
        )
        return self.h.parse_result(result=profiles_data, key="layers_descriptions")

    @timing
    def load_profile(self, name: str) -> dict:
        """
        Загрузить профиль по его названию.
        :param name: (str) название нужного профиля
        :return: (dict) user_iface, save_settings
        """
        # получаем начальные слои (т.е. те, которые уже были до загрузки профиля)
        layers_data = self._get_session_layers()
        layers = {layer.get("uuid") for layer in layers_data}

        # получаем сохранённые профили
        layers_descriptions = self._get_profiles()

        # получаем uuid профиля по интерфейсному названию; если такого нет - генерируем ошибку
        profile_layer_id = ""
        for item in layers_descriptions:
            if item.get("name") == name:
                profile_layer_id = item.get("uuid")
                break
        if profile_layer_id == "":
            return self._raise_exception(
                PolymaticaException,
                f"No such profile: {name}",
                with_traceback=False,
            )

        # загружаем сохраненный профиль
        self.execute_manager_command(
            command_name="user_layer",
            state="load_saved_layer",
            layer_id=profile_layer_id,
        )

        # получаем новое множество слоев сессии
        session_layers = self._get_session_layers()
        new_layers = {layer.get("uuid") for layer in session_layers}

        # получить id слоя, на котором запущен загруженный сценарий; такой слой всегда будет один
        target_layer = new_layers - layers
        profile_layer_id = next(iter(target_layer))

        # дождаться загрузки нового слоя, инициализировать его, сделать активным и сохранить все настройки
        for layer in session_layers:
            current_uuid = layer.get("uuid")
            if current_uuid != profile_layer_id:
                continue

            # поиск OLAP-модуля на этом слое; если их несколько, то возьмём первый из них
            try:
                layer_module_descs = layer["module_descs"]
            except IndexError:
                error_msg = f'No module_descs for layer with id "{current_uuid}"! Layer data: "{layer}"'
                return self._raise_exception(PolymaticaException, error_msg)
            multisphere_module_id = ""
            for module in layer_module_descs:
                if module.get("type_id") == MULTISPHERE_ID:
                    multisphere_module_id = module.get("uuid")
                    break

            # выбрать слой с запущенным профилем
            self.active_layer_id = current_uuid
            self.execute_manager_command(
                command_name="user_layer",
                state="set_active_layer",
                layer_id=current_uuid,
            )
            self.execute_manager_command(
                command_name="user_layer", state="init_layer", layer_id=current_uuid
            )

            # ожидание загрузки слоя
            progress = 0
            while progress < 100:
                time.sleep(0.5)
                result = self.execute_manager_command(
                    command_name="user_layer",
                    state="get_load_progress",
                    layer_id=current_uuid,
                )
                progress = self.h.parse_result(result, "progress")

            # сохраняем настройки
            settings = {
                "wm_layers2": {"lids": list(new_layers), "active": current_uuid}
            }
            result = self.execute_manager_command(
                command_name="user_iface",
                state="save_settings",
                module_id=self.authorization_uuid,
                settings=settings,
            )

            # обновляем общее число строк мультисферы и сохраняем идентификаторы всех слоёв
            if multisphere_module_id:
                self.set_multisphere_module_id(multisphere_module_id)
                self.layers_list = list(new_layers)
                self.update_total_row()
            return result

    def _convert_schedule_item(self, time_zones: dict, user_schedule: dict):
        """
        Подготовка пользовательского планировщика.
        """
        if not user_schedule:
            return

        # установить значение периода для запроса
        user_period = user_schedule["type"]
        user_schedule["type"] = UPDATE_PERIOD[user_period]

        # установить значение часовой зоны для запроса
        h_timezone = user_schedule["time_zone"]
        user_schedule["time_zone"] = time_zones[h_timezone]

        # преобразование времени в UNIX time
        hours, minutes = user_schedule["time"].split(":")
        t = datetime.timedelta(hours=int(hours), minutes=int(minutes))
        user_schedule["time"] = int(t.total_seconds())

    def _get_interval_borders(
        self, user_interval: str, interval_borders: list
    ) -> tuple:
        """
        Служебный метод для получения временных границ обновлений для определённых интервалов для
        методов create_sphere и update_cube.
        """
        if user_interval == "с указанной даты":
            left_border, right_border = f"{interval_borders[0]}, 00:00:00", ""
        elif user_interval == "с и по указанную дату":
            left_border, right_border = (
                f"{interval_borders[0]}, 00:00:00",
                f"{interval_borders[1]}, 00:00:00",
            )
        else:
            left_border, right_border = "", ""
        return left_border, right_border

    @timing
    def create_sphere(
        self,
        cube_name: str,
        source_name: str,
        file_type: str,
        update_params: dict = None,
        sql_params: dict = None,
        user_interval: str = "с текущего дня",
        filepath: str = "",
        separator: str = "",
        increment_dim: str = "",
        interval_dim: str = "",
        interval_borders: list = None,
        encoding: str = "",
        delayed: bool = False,
        modified_records_params: dict = None,
        relevance_date: dict = None,
        indirect_cpu_load_parameter: dict = None,
    ) -> dict:
        """
        Создать новую мультисферу (куб).
        :param cube_name: (str) название создаваемой мультисферы (куба), оно должно состоять из 5 и более символов,
            допустимы буквы, цифры, специальные символы (кроме: % ^ & = ; ± § ` ~ ] [ } { < >).
            Если мультисфера с таким названием присутствует на сервере, то к названию будет добавлено число в скобках,
            начиная с единицы, например "cube(1)", "cube(2)".
        :param source_name: (str) название источника данных, оно должно содержать от 5 до 100 символов, допустимы
            русские и английские буквы, цифры, пробел, '_' , '-').
        :param file_type: (str) тип источника данных (см. значения в "server-codes.json" в поле "data_source_type").
            Примеры основных источников данных: "excel", "csv", "mssql", "mysql", "psql", "jdbc", "odbc".
        :param update_params: (dict) параметры обновления мультисферы. Не используется для мультисфер,
            созданных из файловых источников ("excel", "csv").
            Имеет структуру:
            {
                'type': <value>,
                'schedule': <dict>
            }, где:
                type - тип обновления, возможны значения:
                ["полное" (ранее было "ручное" и "по расписанию" (при наличии расписания в schedule),
                эти значения тоже доступны для обратной совместимости),
                "интервальное", "инкрементальное", "обновление измененных записей"];

                schedule - планировщик, позволяющий задать расписание для обновления. Если расписание
                задавать не надо, то необходимо передать 'schedule': {}.
                Имеет структуру:
                    {
                        'type': <value>,
                        'time': <value>,
                        'time_zone': <value>,
                        'week_day': <value>,
                        'day': <value>
                    }, где:
                        type - период обновления, возможны значения: ["Ежедневно", "Еженедельно", "Ежемесячно"].
                        time - время в формате "18:30", актуально для любого периода обновления.
                        time_zone - часовой пояс (например, "UTC+3:00" - должен записываться, как в server-codes.json),
                            актуально для любого периода обновления.
                        week_day - день недели, возможны значения: ["понедельник", "вторник", "среда", "четверг",
                            "пятница", "суббота", "воскресенье"] (регистр важен);
                            актуально только для периода обновления "Еженедельно".
                        day - число месяца (целое число меньше 31);
                            актуально только для периода обновления "Ежемесячно".
                    Также может быть списком, содержащим словари указанной выше структуры.
            Пример:
                {
                    "type": "полное",
                    "schedule": {
                        "type": "Ежедневно",
                        "time": "18:30",
                        "time_zone": "UTC+3:00"
                    }
                }
        :param sql_params: (dict) параметры для источника данных SQL.
            Поля, передаваемые в словарь:
                "server" - хост, который может быть задан в виде IP-адреса сервера (например, "10.18.0.132"),
                    либо в виде имени сервера (например, "polymatica.database1.ru");
                    опционально также может быть задан порт подключения, в таком случае он должен идти после указания
                    хоста через двоеточие (например, "10.18.0.132:5433", "polymatica.database1.ru:5433");
                    в случае, если порт явно не указан, подразумевается порт по-умолчанию 5432.
                "login" - логин пользователя.
                "passwd" - пароль пользователя.
                "database" - имя базы данных.
                "sql_query" - запрос, который необходимо выполнить на сервере.
            Пример задания параметра:
                {
                    "server": "10.8.0.115:5433",
                    "login": "your_user",
                    "passwd": "your_password",
                    "database": "database_name",
                    "sql_query": "SELECT * FROM table"
                }
        :param user_interval: (str) интервал обновлений; возможны значения:
            ["с текущего дня", "с предыдущего дня", "с текущей недели", "с предыдущей недели", "с текущего месяца",
            "с предыдущего месяца", "с текущего квартала", "с предыдущего квартала", "с текущего года",
            "с предыдущего года", "с указанной даты", "с и по указанную дату"];
            актуально только для интервального обновления.
        :param filepath: (str) путь к файлу, либо название файла, если он лежит в той же директории.
        :param separator: (str) разделитель столбцов; обязателен для csv-источника.
        :param increment_dim: (str) название размерности для инкрементального обновления; размерность должна иметь
            один из следующих типов: uint8, uint16, uint32, uint64, double, date, time, datetime.
        :param interval_dim: (str) название размерности для интервального обновления; размерность должна иметь
            один из следующих типов: date, datetime.
        :param interval_borders: (list) временные границы для интервалов обновлений
            "с указанной даты" и "с и по указанную дату", причём для обновления "с указанной даты" достаточно передать
            в список только одно значение времени, а для обновления "с и по указанную дату" - два значения времени,
            при этом второе значение должно быть больше первого. Формат значений времени: "DD.MM.YYYY". Все остальные
            значения, если они будут переданы, будут игнорироваться. Актуально только для интервального обновления.
        :param encoding: (str) кодировка, например UTF-8; обязательна для csv-источника.
        :param delayed: (bool) создать мультисферу при первом обновлении (как аналогичный чек-бокс на интерфейсе).
        :param modified_records_params: (dict) параметры обновления для типа "обновление измененных записей".
            Поля, передаваемые в словарь:
                "modified_records_key" - поле, которому осуществляется сопоставление данных (имя размерности).
                    Должно быть уникальным на уровне источника. Тип данных - любой.
                "modified_records_date" - дата изменения записи (имя размерности). При использовании
                    этого параметра обновления будут обновлены существующие и добавлены новые записи,
                    для которых дата изменения записи в источнике больше чем в мультисфере.
                    Размерность должна иметь один из следующих типов: date, datetime.
                "version" - версия алгоритма, 0 - старый алгоритм, 1 - новый алгоритм (дефолтное значение).
                    Необязательный аргумент.
            "modified_records_key" и "modified_records_date" должны иметь разные значения.
            Пример задания параметров:
                {
                    "modified_records_key": "id",
                    "modified_records_date": "date",
                    "version": 1
                }
        :param relevance_date: (dict) словарь, содержащий параметры отображения даты актуальности данных
            в окне мультисферы. Необязательный аргумент.
            Поля, передаваемые в словарь:
                "relevance_date_dimension" (str) - имя размерности, максимальное значение которой будет
                    датой актуальности данных, отображаемой в окне мультисферы.
                    Размерность должна быть с типом "Дата" или "Дата Время".
                "format" (str) - формат отображения даты актуальности. Доступные опции — "datetime" и "date"
                    ("Дата и время" и "Дата") соответственно.
                "consider_filter" (bool) - параметр «Учитывать фильтр». Если true, то в окне мультисферы максимальное
                    значение элемента выбранной размерности будет отображаться с учетом всех примененных фильтров, а если
                    false, то без фильтров.
            Пример задания relevance_date:
                {
                    "relevance_date_dimension": "Дата",
                    "format": "date",
                    "consider_filter": True
                }
        :param indirect_cpu_load_parameter: (dict) словарь, содержащий параметры предельного процента использования
            CPU для обновления мультисферы. Необязательный аргумент.
            Поля, передаваемые в словарь:
                "use_default_value" (bool) - Параметр "Использование ограничений CPU по умолчанию". Если True,
                    то используется параметр предельного % использования CPU из конфига. Если False, то
                    то используется параметр "percent", передаваемый пользователем.
                    По умолчанию True.
                "percent" (int) - процентное ограничение CPU, должен быть в диапазоне от 1 до 100. Если этот
                    параметр больше значения параметра предельного % использования CPU из конфига, то используется
                    параметр из конфига.
            Пример задания indirect_cpu_load_parameter:
                {
                    "use_default_value": True,
                }
                или
                {
                    "use_default_value": False,
                    "percent": 70,
                }

        :return: (dict) Результат команды ("user_cube", "save_ext_info_several_sources_request").
        """
        sql_params = dict() if sql_params is None else copy.deepcopy(sql_params)
        interval_borders = (
            list() if interval_borders is None else copy.deepcopy(interval_borders)
        )
        default_update_params = {"type": "ручное", "schedule": {}}
        current_update_params = (
            default_update_params
            if update_params is None
            else copy.deepcopy(update_params)
        )
        if update_params is not None and update_params.get("type") in ("ручное", "по расписанию"):
            self.logger.warning('Params "ручное" and "по расписанию" from update_params["type"] will be deprecated '
                                'in future version. Use "полное" with or without schedule instead.')
        # отправляем на сервер старые названия типов обновления
        if current_update_params.get("type") == "полное":
            if not current_update_params.get("schedule"):
                current_update_params["type"] = "ручное"
            else:
                current_update_params["type"] = "по расписанию"

        time_zones = self.server_codes["manager"]["timezone"]
        if modified_records_params is None:
            modified_records_params = dict()
        else:
            copy.deepcopy(modified_records_params)
            if modified_records_params.get("version") != 0:
                modified_records_params["version"] = 1

        # проверки
        params = validate_params(
            CreateSphereParams,
            self._raise_exception,
            cube_name=cube_name,
            source_name=source_name,
            file_type=file_type,
            update_params=update_params,
            sql_params=sql_params,
            user_interval=user_interval,
            filepath=filepath,
            separator=separator,
            increment_dim=increment_dim,
            interval_dim=interval_dim,
            interval_borders=interval_borders,
            encoding=encoding,
            delayed=delayed,
            modified_records_params=modified_records_params,
            relevance_date=relevance_date,
            indirect_cpu_load_parameter=indirect_cpu_load_parameter,
        )
        (
            cube_name,
            source_name,
            file_type,
            update_params,
            sql_params,
            user_interval,
            filepath,
            separator,
            increment_dim,
            interval_dim,
            interval_borders,
            encoding,
            delayed,
            modified_records_params,
            relevance_date,
            indirect_cpu_load_parameter,
        ) = (
            params.cube_name,
            params.source_name,
            params.file_type,
            params.update_params,
            params.sql_params,
            params.user_interval,
            params.filepath,
            params.separator,
            params.increment_dim,
            params.interval_dim,
            params.interval_borders,
            params.encoding,
            params.delayed,
            params.modified_records_params,
            params.relevance_date,
            params.indirect_cpu_load_parameter,
        )

        try:
            cube_name, indirect_cpu_load_parameter = self.checks(
                self.func_name,
                current_update_params,
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
            )
        except Exception as e:
            return self._raise_exception(ValueError, str(e), with_traceback=False)

        # определяем пользовательский планировщик
        update_type = current_update_params["type"]
        user_schedule = current_update_params.get("schedule")
        schedule_items_tmp = (
            user_schedule if isinstance(user_schedule, list) else [user_schedule]
        )
        if update_type != "ручное":
            for schedule_item in schedule_items_tmp:
                self._convert_schedule_item(time_zones, schedule_item)
        schedule_items = [item for item in schedule_items_tmp if item]

        # параметр source_type для различных форматов данных
        source_type = self.h.get_source_type(file_type)

        # создать мультисферу, получить id куба
        res = self.execute_manager_command(
            command_name="user_cube", state="create_cube_request", cube_name=cube_name
        )
        self.cube_id = self.h.parse_result(result=res, key="cube_id")

        # загрузка csv/excel файла
        encoded_file_name = ""
        if (file_type == "excel") or (file_type == "csv"):
            encoded_file_name = self.h.upload_file_to_server(filepath)

        # превью-данные
        preview_data = {
            "name": source_name,
            "server": "",
            "server_type": source_type,
            "login": "",
            "passwd": "",
            "database": "",
            "sql_query": separator,
            "skip": -1,
        }

        # для бд выставить параметры server, login, passwd и sql_query
        if (file_type != "csv") and (file_type != "excel"):
            preview_data.update(sql_params)

        # для формата данных csv выставить кодировку
        if file_type == "csv":
            preview_data.update({"encoding": encoding, "server": encoded_file_name})

        # для формата данных excel указать параметр server
        if file_type == "excel":
            preview_data.update({"server": encoded_file_name})

        # соединиться с бд в тестовом режиме, проверить соединение
        conn_result = self.execute_manager_command(
            command_name="user_cube",
            state="test_source_connection_request",
            datasource=preview_data,
        )
        conn_status = self.h.parse_result(conn_result, "status")
        if conn_status.get("code") != 0:
            error_msg = "Unable to connect to database: {}".format(
                conn_status.get("message", "description not found!")
            )
            return self._raise_exception(
                DBConnectionError, error_msg, with_traceback=False
            )

        # из структуры данных получаем словари с данными о размерностях и фактах
        self.execute_manager_command(
            command_name="user_cube",
            state="get_fields_request",
            cube_id=self.cube_id,
            datasources=[preview_data],
        )
        result = self.execute_manager_command(
            command_name="user_cube",
            state="structure_preview_request",
            cube_id=self.cube_id,
            links=[],
        )

        try:
            # получаем и обрабатываем информацию о фактах и размерностях куба
            dims, measures = self.h.get_and_process_dims_and_measures(result, file_type)
        except Exception as e:
            return self._raise_exception(
                PolymaticaException, str(e), with_traceback=False
            )

        # подготавливаем параметры для создания сферы
        command_params = {
            "cube_id": self.cube_id,
            "cube_name": cube_name,
            "dims": dims,
            "facts": measures,
            "schedule": {"delayed": delayed, "items": schedule_items},
        }
        if update_type == "ручное":
            command_params["schedule"]["items"] = list()
        elif update_type == "по расписанию":
            pass
        elif update_type == "инкрементальное":
            # получаем идентификатор размерности инкремента
            increment_dim_id = ""
            for dim in dims:
                if dim.get("name") == increment_dim:
                    current_type = POLYMATICA_INT_TYPES_MAP.get(dim.get("type"))
                    if current_type not in (
                        "uint8",
                        "uint16",
                        "uint32",
                        "uint64",
                        "double",
                        "date",
                        "time",
                        "datetime",
                    ):
                        error_msg = (
                            f'Dimension "{interval_dim}" has type "{current_type}", '
                            f'one of types is expected: ["uint8", "uint16", "uint32", '
                            f'"uint64", "double", "date", "time", "datetime"]!'
                        )
                        return self._raise_exception(
                            PolymaticaException, error_msg, with_traceback=False
                        )
                    increment_dim_id = dim.get("field_id")
                    break
            else:
                message = (
                    f'No such increment field "{increment_dim}" in importing sphere'
                )
                return self._raise_exception(ValueError, message, with_traceback=False)
            command_params.update({"increment_field": increment_dim_id})
        elif update_type == "интервальное":
            # получаем идентификатор размерности
            interval_dim_id = ""
            for dim in dims:
                if dim.get("name") == interval_dim:
                    current_type = POLYMATICA_INT_TYPES_MAP.get(dim.get("type"))
                    if current_type not in ("date", "datetime"):
                        error_msg = (
                            f'Dimension "{interval_dim}" has type "{current_type}",'
                            f' expected "date" or "datetime"!'
                        )
                        return self._raise_exception(
                            PolymaticaException, error_msg, with_traceback=False
                        )
                    interval_dim_id = dim.get("id")
                    break
            else:
                message = f'No such dimension "{interval_dim}" in importing sphere'
                return self._raise_exception(ValueError, message, with_traceback=False)

            # получаем временные границы обновлений для определённых интервалов
            left_border, right_border = self._get_interval_borders(
                user_interval, interval_borders
            )

            command_params.update(
                {
                    "interval": {
                        "type": INTERVAL_MAP[user_interval],
                        "left_border": left_border,
                        "right_border": right_border,
                        "dimension_id": interval_dim_id,
                    }
                }
            )
        elif update_type == "обновление измененных записей":
            modified_records_key = modified_records_params.get("modified_records_key")
            modified_records_date = modified_records_params.get("modified_records_date")
            if modified_records_key == modified_records_date:
                message = (
                    f'Modified_records_key and modified_records_date '
                    f'must have different values!'
                )
                return self._raise_exception(ValueError, message, with_traceback=False)

            modified_records_algo_version = modified_records_params.get("version")
            modified_records_key_id = ""
            modified_records_date_id = ""
            for dim in dims:
                if dim.get("name") == modified_records_key:
                    modified_records_key_id = dim.get("id")
                if dim.get("name") == modified_records_date:
                    current_type = POLYMATICA_INT_TYPES_MAP.get(dim.get("type"))
                    if current_type not in ("date", "datetime"):
                        error_msg = (
                            f'Dimension "{modified_records_date}" has type "{current_type}", '
                            f'expected "date" or "datetime"!'
                        )
                        return self._raise_exception(
                            PolymaticaException, error_msg, with_traceback=False
                        )
                    modified_records_date_id = dim.get("id")

            if not modified_records_key_id:
                message = (
                    f'No such dimension "{modified_records_key}" in importing sphere!'
                )
                return self._raise_exception(ValueError, message, with_traceback=False)

            if not modified_records_date_id:
                message = (
                    f'No such dimension "{modified_records_date}" in importing sphere!'
                )
                return self._raise_exception(ValueError, message, with_traceback=False)

            command_params.update(
                {
                    "delta": {
                        "primary_key_dim": modified_records_key_id,
                        "timestamp_dim": modified_records_date_id,
                        "version": modified_records_algo_version,
                    }
                }
            )

        # обрабатываем и добавляем параметры даты актуальности данных
        relevance_date_dict = self._process_relevance_date(relevance_date, dims)

        command_params.update({"relevance_date": relevance_date_dict})

        # добавляем параметры предельного процента использования CPU
        # (валидация и обработка происходят в error_handler.py)
        command_params.update({"indirect_cpu_load_parameter": indirect_cpu_load_parameter})

        # создаём мультисферу с нужными параметрами
        self.func_name = "create_sphere"
        return self.execute_manager_command(
            command_name="user_cube",
            state="save_ext_info_several_sources_request",
            **command_params,
        )

    @timing
    def update_cube(
        self,
        cube_name: str,
        new_cube_name: str = None,
        update_params: dict = None,
        user_interval: str = "с текущего дня",
        filepath: str = "",
        separator: str = "",
        delayed: bool = False,
        increment_dim: str = "",
        interval_dim: str = "",
        interval_borders: list = None,
        encoding: str = "",
        modified_records_params: dict = None,
        relevance_date: dict = None,
        indirect_cpu_load_parameter: dict = None,
    ) -> dict:
        """
        Обновить существующую мультисферу.
        :param cube_name: (str) название обновляемой мультисферы (куба).
        :param new_cube_name: (str) новое название мультисферы (куба)
            (необязательный параметр, используется, если необходимо переименование).
            Если мультисфера с таким названием присутствует на сервере, то к названию будет
            добавлено число в скобках, начиная с единицы, например "cube(1)", "cube(2)".
        :param update_params: (dict) параметры обновления мультисферы. Не используется для мультисфер,
            созданных из файловых источников ("excel", "csv").
            Имеет структуру:
            {
                'type': <value>,
                'schedule': <dict>
            }, где:
                type - тип обновления, возможны значения:
                ["полное" (ранее было "ручное" и "по расписанию" (при наличии расписания в schedule),
                эти значения тоже доступны для обратной совместимости),
                "интервальное", "инкрементальное", "обновление измененных записей"];

                schedule - планировщик, позволяющий задать расписание для обновления. Если расписание
                задавать не надо, то необходимо передать 'schedule': {}.
                Имеет структуру:
                    {
                        'type': <value>,
                        'time': <value>,
                        'time_zone': <value>,
                        'week_day': <value>,
                        'day': <value>
                    }, где:
                        type - период обновления, возможны значения: ["Ежедневно", "Еженедельно", "Ежемесячно"].
                        time - время в формате "18:30", актуально для любого периода обновления.
                        time_zone - часовой пояс (например, "UTC+3:00" - должен записываться, как в server-codes.json),
                            актуально для любого периода обновления.
                        week_day - день недели, возможны значения: ["понедельник", "вторник", "среда", "четверг",
                            "пятница", "суббота", "воскресенье"] (регистр важен);
                            актуально только для периода обновления "Еженедельно".
                        day - число месяца (целое число меньше 31);
                            актуально только для периода обновления "Ежемесячно".
                    Также может быть списком, содержащим словари указанной выше структуры.
            Пример:
                [{
                    "type": "полное",
                    "schedule": {
                        "type": "Ежедневно",
                        "time": "18:30",
                        "time_zone": "UTC+3:00"
                    }
                }]
        :param user_interval: (str) интервал обновлений; возможны значения:
            ["с текущего дня", "с предыдущего дня", "с текущей недели", "с предыдущей недели", "с текущего месяца",
            "с предыдущего месяца", "с текущего квартала", "с предыдущего квартала", "с текущего года",
            "с предыдущего года", "с указанной даты", "с и по указанную дату"];
            актуально только для интервального обновления.
        :param filepath: (str) путь к файлу, либо название файла, если он лежит в той же директории. Параметр
            используется для замены файла в источнике. Можно заменять на файл того же типа, что и был,
            например "csv" на "csv". В пути файла обязательно должно быть расширение, например, ".csv".
        :param separator: (str) разделитель столбцов. Обязателен для csv-источника (при замене источника).
        :param delayed: (bool) создать мультисферу при первом обновлении (как аналогичный чек-бокс на интерфейсе).
        :param increment_dim: (str) название размерности, необходимой для инкрементального обновления.
        :param interval_dim: (str) название размерности для интервального обновления; размерность должна иметь
            один из следующих типов: date, datetime.
        :param interval_borders: (list) временные границы для интервалов обновлений
            "с указанной даты" и "с и по указанную дату", причём для обновления "с указанной даты" достаточно передать
            в список только одно значение времени, а для обновления "с и по указанную дату" - два значения времени,
            при этом второе значение должно быть больше первого. Формат значений времени: "DD.MM.YYYY". Все остальные
            значения, если они будут переданы, будут игнорироваться. Актуально только для интервального обновления.
        :param encoding: (str) кодировка, например UTF-8; обязательна для csv-источника (при замене источника).
        :param modified_records_params: (dict) параметры обновления для типа "обновление измененных записей".
            Поля, передаваемые в словарь:
                "modified_records_key" - поле, которому осуществляется сопоставление данных (имя размерности).
                    Должно быть уникальным на уровне источника. Тип данных - любой.
                "modified_records_date" - дата изменения записи (имя размерности). При использовании
                    этого параметра обновления будут обновлены существующие и добавлены новые записи,
                    для которых дата изменения записи в источнике больше чем в мультисфере.
                    Размерность должна иметь один из следующих типов: date, datetime.
                "version" - версия алгоритма, 0 - старый алгоритм, 1 - новый алгоритм (дефолтное значение).
                    Необязательный аргумент.
            "modified_records_key" и "modified_records_date" должны иметь разные значения.
            Пример задания параметров:
                {
                    "modified_records_key": "id",
                    "modified_records_date": "date",
                    "version": 1
                }
        :param relevance_date: (dict) словарь, содержащий параметры отображения даты актуальности данных
            в окне мультисферы. Необязательный аргумент.
            Поля, передаваемые в словарь:
                "relevance_date_dimension" (str) - имя размерности, максимальное значение которой будет
                    датой актуальности данных, отображаемой в окне мультисферы.
                    Размерность должна быть с типом "Дата" или "Дата Время".
                "format" (str) - формат отображения даты актуальности. Доступные опции — "datetime" и "date"
                    ("Дата и время" и "Дата") соответственно.
                "consider_filter" (bool) - параметр «Учитывать фильтр». Если True, то в окне мультисферы максимальное
                    значение элемента выбранной размерности будет отображаться с учетом всех примененных фильтров,
                    а если False, то без фильтров.
            Пример задания relevance_date:
                {
                    "relevance_date_dimension": "Дата",
                    "format": "date",
                    "consider_filter": True
                }
            Для сброса параметров даты актуальности данных необходимо передать relevance_date = {} (пустой словарь).

        :param indirect_cpu_load_parameter: (dict) словарь, содержащий параметры предельного процента использования
            CPU для обновления мультисферы. Необязательный аргумент.
            Поля, передаваемые в словарь:
                "use_default_value" (bool) - Параметр "Использование ограничений CPU по умолчанию". Если True,
                    то используется параметр предельного % использования CPU из конфига. Если False, то
                    то используется параметр "percent", передаваемый пользователем.
                    По умолчанию True.
                "percent" (int) - процентное ограничение CPU, должен быть в диапазоне от 1 до 100. Если этот
                    параметр больше значения параметра предельного % использования CPU из конфига, то используется
                    параметр из конфига.
            Пример задания indirect_cpu_load_parameter:
                {
                    "use_default_value": True,
                }
                или
                {
                    "use_default_value": False,
                    "percent": 70,
                }

        :return: (dict) Результат команды ("user_cube", "save_ext_info_several_sources_request").
        """
        default_update_params = {"type": "ручное", "schedule": {}}
        current_update_params = (
            default_update_params
            if update_params is None
            else copy.deepcopy(update_params)
        )
        if update_params is not None and update_params.get("type") in ("ручное", "по расписанию"):
            self.logger.warning('Params "ручное" and "по расписанию" from update_params["type"] will be deprecated '
                                'in future version. Use "полное" with or without schedule instead.')
        # отправляем на сервер старые названия типов обновления
        if current_update_params.get("type") == "полное":
            if not current_update_params.get("schedule"):
                current_update_params["type"] = "ручное"
            else:
                current_update_params["type"] = "по расписанию"

        time_zones = self.server_codes["manager"]["timezone"]
        if modified_records_params is None:
            modified_records_params = dict()
        else:
            copy.deepcopy(modified_records_params)
            if modified_records_params.get("version") != 0:
                modified_records_params["version"] = 1
        cubes_list = self.get_cubes_list()
        self.func_name = "update_cube"

        # проверки
        params = validate_params(
            UpdateCubeParams,
            self._raise_exception,
            cube_name=cube_name,
            new_cube_name=new_cube_name,
            update_params=update_params,
            user_interval=user_interval,
            filepath=filepath,
            separator=separator,
            delayed=delayed,
            increment_dim=increment_dim,
            interval_dim=interval_dim,
            interval_borders=interval_borders,
            encoding=encoding,
            modified_records_params=modified_records_params,
            relevance_date=relevance_date,
            indirect_cpu_load_parameter=indirect_cpu_load_parameter,
        )
        (
            cube_name,
            new_cube_name,
            update_params,
            user_interval,
            filepath,
            separator,
            increment_dim,
            interval_dim,
            interval_borders,
            encoding,
            delayed,
            modified_records_params,
            relevance_date,
            indirect_cpu_load_parameter,
        ) = (
            params.cube_name,
            params.new_cube_name,
            params.update_params,
            params.user_interval,
            params.filepath,
            params.separator,
            params.increment_dim,
            params.interval_dim,
            params.interval_borders,
            params.encoding,
            params.delayed,
            params.modified_records_params,
            params.relevance_date,
            params.indirect_cpu_load_parameter,
        )
        try:
            (cube_id,
             new_cube_name,
             validated_indirect_cpu_load_parameter,
             new_file_type) = self.checks(
                self.func_name,
                cube_name,
                new_cube_name,
                cubes_list,
                current_update_params,
                user_interval,
                increment_dim,
                interval_dim,
                interval_borders,
                time_zones,
                relevance_date,
                indirect_cpu_load_parameter,
                filepath,
                encoding,
            )
        except Exception as e:
            return self._raise_exception(ValueError, str(e), with_traceback=False)
        self.cube_name = new_cube_name if new_cube_name else cube_name
        self.cube_id = cube_id

        # получаем полную информацию о мультисфере
        result = self.execute_manager_command(
            command_name="user_cube",
            state="ext_info_several_sources_request",
            cube_id=self.cube_id,
        )
        # получаем информацию о текущем типе обновления
        current_delta_primary_key_dim = self.h.parse_result(result=result, key="delta", nested_key="primary_key_dim")
        current_increment_field = self.h.parse_result(result=result, key="increment_field")
        current_interval_dim_id = self.h.parse_result(result=result, key="interval", nested_key="dimension_id")
        if current_increment_field != EMPTY_ID:
            current_update_type = "инкрементальное"
        elif current_interval_dim_id != EMPTY_ID:
            current_update_type = "интервальное"
        elif current_delta_primary_key_dim != EMPTY_ID:
            current_update_type = "обновление измененных записей"
        else:
            current_update_type = "ручное"

        # получаем информацию о расписании и о дате актуальности данных
        current_schedule_items = self.h.parse_result(result=result, key="schedule", nested_key="items")
        current_relevance_date = self.h.parse_result(result=result, key="relevance_date")

        # получаем информацию о текущем источнике
        current_datasource = self.h.parse_result(result=result, key="datasources")[0]
        current_source_type = current_datasource.get("server_type", 0)
        current_source_name = current_datasource.get("name")

        # если задан путь к файлу filepath, и текущий источник типа "csv" или "excel",
        # то заменяем файл в источнике на новый
        if filepath:
            current_file_type = self.h.get_file_type(current_source_type)
            if current_file_type == new_file_type:
                encoded_file_name = self.h.upload_file_to_server(filepath)
                preview_data = {
                    "name": current_source_name,
                    "server": encoded_file_name,
                    "server_type": current_source_type,
                    "login": "",
                    "passwd": "",
                    "database": "",
                    "sql_query": separator,
                    "skip": -1,
                }

                # для формата данных csv выставляем кодировку
                if current_file_type == "csv":
                    preview_data.update({"encoding": encoding})

                # из структуры данных получаем словари с данными о размерностях и фактах
                self.execute_manager_command(
                    command_name="user_cube",
                    state="get_fields_request",
                    cube_id=self.cube_id,
                    datasources=[preview_data],
                )
                structure_preview_result = self.execute_manager_command(
                    command_name="user_cube",
                    state="structure_preview_request",
                    cube_id=self.cube_id,
                    links=[],
                )
                # получаем и обрабатываем информацию о фактах и размерностях куба
                dims, measures = self.h.get_and_process_dims_and_measures(structure_preview_result, current_file_type)

            else:
                error_msg = (f"To replace the source, the uploaded file must be of the same format "
                             f"as the current source. Current source type is '{current_file_type}'.")
                return self._raise_exception(
                    ValueError, error_msg, with_traceback=False
                )

        else:
            # получаем и обрабатываем информацию о фактах и размерностях куба
            dims, measures = self.h.get_and_process_dims_and_measures(result)

        # определяем пользовательский планировщик
        update_type = current_update_params.get("type")
        user_schedule = current_update_params.get("schedule")
        schedule_items_tmp = (
            user_schedule if isinstance(user_schedule, list) else [user_schedule]
        )
        if update_type != "ручное":
            for schedule_item in schedule_items_tmp:
                self._convert_schedule_item(time_zones, schedule_item)
        schedule_items = [item for item in schedule_items_tmp if item]
        # если новый тип обновления такой же, как и был, и новое расписание не задано, то сохраняем имеющееся
        # расписание.
        if not schedule_items and current_update_type == update_type:
            schedule_items = current_schedule_items

        # обрабатываем и добавляем параметры даты актуальности данных, иначе отправляем имеющиеся.
        # если relevance_date = {}, то отправятся дефолтные параметры (произойдет сброс параметров).
        if relevance_date is not None:
            relevance_date_dict = self._process_relevance_date(relevance_date, dims)
        else:
            relevance_date_dict = current_relevance_date

        # добавляем параметры предельного процента использования CPU. Если их не передали, отправляем имеющиеся.
        if indirect_cpu_load_parameter is not None:
            indirect_cpu_load_parameter_dict = validated_indirect_cpu_load_parameter
        else:
            current_indirect_cpu_load_parameter = self.h.parse_result(result=result, key="indirect_cpu_load_parameter")
            indirect_cpu_load_parameter_dict = current_indirect_cpu_load_parameter

        # подготавливаем параметры для обновления сферы
        command_params = {
            "cube_id": self.cube_id,
            "cube_name": self.cube_name,
            "dims": dims,
            "facts": measures,
            "schedule": {"delayed": delayed, "items": schedule_items},
            "relevance_date": relevance_date_dict,
            "indirect_cpu_load_parameter": indirect_cpu_load_parameter_dict
        }
        if update_type == "инкрементальное":
            # получаем идентификатор размерности инкремента
            increment_dim_id = ""
            for dim in dims:
                if dim.get("name") == increment_dim:
                    current_type = POLYMATICA_INT_TYPES_MAP.get(dim.get("type"))
                    if current_type not in (
                        "uint8",
                        "uint16",
                        "uint32",
                        "uint64",
                        "double",
                        "date",
                        "time",
                        "datetime",
                    ):
                        error_msg = (
                            f'Dimension "{interval_dim}" has type "{current_type}", '
                            f'one of types is expected: ["uint8", "uint16", "uint32", '
                            f'"uint64", "double", "date", "time", "datetime"]!'
                        )
                        return self._raise_exception(
                            PolymaticaException, error_msg, with_traceback=False
                        )
                    increment_dim_id = dim.get("field_id")
                    break
            else:
                message = (
                    f'No such increment field "{increment_dim}" in importing sphere'
                )
                return self._raise_exception(ValueError, message, with_traceback=False)
            command_params.update({"increment_field": increment_dim_id})
        elif update_type == "интервальное":
            # получаем идентификатор размерности
            interval_dim_id = ""
            for dim in dims:
                if dim.get("name") == interval_dim:
                    current_type = POLYMATICA_INT_TYPES_MAP.get(dim.get("type"))
                    if current_type not in ("date", "datetime"):
                        error_msg = (
                            f'Dimension "{interval_dim}" has type "{current_type}", '
                            f'expected "date" or "datetime"!'
                        )
                        return self._raise_exception(
                            PolymaticaException, error_msg, with_traceback=False
                        )
                    interval_dim_id = dim.get("id")
                    break
            else:
                message = f'No such dimension "{interval_dim}" in importing sphere'
                return self._raise_exception(ValueError, message, with_traceback=False)

            # получаем временные границы обновлений для определённых интервалов
            left_border, right_border = self._get_interval_borders(
                user_interval, interval_borders
            )

            command_params.update(
                {
                    "interval": {
                        "type": INTERVAL_MAP[user_interval],
                        "left_border": left_border,
                        "right_border": right_border,
                        "dimension_id": interval_dim_id,
                    }
                }
            )
        elif update_type == "обновление измененных записей":
            modified_records_key = modified_records_params.get("modified_records_key")
            modified_records_date = modified_records_params.get("modified_records_date")
            if modified_records_key == modified_records_date:
                message = (
                    f'Modified_records_key and modified_records_date '
                    f'must have different values!'
                )
                return self._raise_exception(ValueError, message, with_traceback=False)

            modified_records_algo_version = modified_records_params.get("version")
            modified_records_key_id = ""
            modified_records_date_id = ""
            for dim in dims:
                if dim.get("name") == modified_records_key:
                    modified_records_key_id = dim.get("id")
                if dim.get("name") == modified_records_date:
                    current_type = POLYMATICA_INT_TYPES_MAP.get(dim.get("type"))
                    if current_type not in ("date", "datetime"):
                        error_msg = (
                            f'Dimension "{modified_records_date}" has type "{current_type}", '
                            f'expected "date" or "datetime"!'
                        )
                        return self._raise_exception(
                            PolymaticaException, error_msg, with_traceback=False
                        )
                    modified_records_date_id = dim.get("id")

            if not modified_records_key_id:
                message = (
                    f'No such dimension "{modified_records_key}" in importing sphere!'
                )
                return self._raise_exception(ValueError, message, with_traceback=False)

            if not modified_records_date_id:
                message = (
                    f'No such dimension "{modified_records_date}" in importing sphere!'
                )
                return self._raise_exception(ValueError, message, with_traceback=False)

            command_params.update(
                {
                    "delta": {
                        "primary_key_dim": modified_records_key_id,
                        "timestamp_dim": modified_records_date_id,
                        "version": modified_records_algo_version,
                    }
                }
            )
        # и, наконец, обновляем куб
        self.func_name = "update_cube"
        return self.execute_manager_command(
            command_name="user_cube",
            state="save_ext_info_several_sources_request",
            **command_params,
        )

    def _process_relevance_date(self, relevance_date, dims) -> dict:
        """
        Вспомогательный метод для обработки параметра relevance_date в create_sphere и update_cube
        """

        if relevance_date:
            dimension_name = relevance_date.get("relevance_date_dimension")
            found_dim = next((dim for dim in dims if dim.get("name") == dimension_name), None)
            if found_dim is None:
                return self._raise_exception(
                    PolymaticaException, f'Dimension with name "{dimension_name}" for relevance date '
                                         f'not found!', with_traceback=False
                )
            dimension_id = found_dim.get("id")
            dimension_type = found_dim.get("type")
            if POLYMATICA_INT_TYPES_MAP.get(dimension_type) not in ("date", "datetime"):
                error_msg = (
                    f'Dimension "{dimension_name}" for relevance date must be of type "date" or "datetime"!'
                )
                return self._raise_exception(
                    PolymaticaException, error_msg, with_traceback=False
                )
            data_type = POLYMATICA_TYPES_INT_MAP.get(relevance_date.get("format"))
            consider_filter = relevance_date.get("consider_filter")
            relevance_date_dict = {
                "dimension_id": dimension_id,
                "data_type": data_type,
                "consider_filter": consider_filter
            }
        else:
            default_relevance_date = {
                "dimension_id": "00000000",
                "data_type": 19,
                "consider_filter": False
            }
            relevance_date_dict = default_relevance_date
        return relevance_date_dict

    @timing
    def manual_update_cube(self, cube_name: str) -> dict:
        """
        Запуск обновления мультисферы вручную.
        :param cube_name: (str) название обновляемого куба.
        :return: Результат команды ("user_cube", "manual_update")
        """
        self.cube_name = cube_name

        # получение списка описаний мультисфер
        cubes_list = self.get_cubes_list()

        # получить cube_id из списка мультисфер
        try:
            self.cube_id = self.h.get_cube_id(cubes_list, cube_name)
        except ValueError as e:
            return self._raise_exception(ValueError, str(e))

        self.func_name = "manual_update_cube"

        # запуск обновления мультисферы вручную
        return self.execute_manager_command(
            command_name="user_cube", state="manual_update", cube_id=self.cube_id
        )

    @timing
    def wait_cube_loading(
        self, cube_name: str, time_sleep: int = 5, max_attempt: Union[None, int] = None
    ) -> bool:
        """
        Ожидание загрузки мультисферы с заданным именем. Актуально только после создания мультисферы.
        :param cube_name: (str) название мультисферы.
        :param time_sleep: (int) время задержки запросов к серверу Полиматики в секундах;
            значение должно быть больше 0, по-умолчанию 5 секунд.
        :param max_attempt: (None/int) максимальное число попыток обращения к серверу Полиматики;
            если значение - None, то число попыток не ограничено; если значение - число, то оно должно быть больше 0;
            по-умолчанию None.
        :return: (bool) True, если удалось дождаться завершения загрузки мультисферы, False в противном случае.
        """
        # проверки
        try:
            self.checks(self.func_name, cube_name, time_sleep, max_attempt)
        except Exception as exn:
            return self._raise_exception(ValueError, str(exn), with_traceback=False)

        count = 0
        while True:
            if max_attempt is not None and count == max_attempt:
                break
            cubes_list = self.get_cubes_list()
            for cube in cubes_list:
                if cube.get("name") == cube_name:
                    if cube.get("available"):
                        self.func_name = "wait_cube_loading"
                        return True
                    else:
                        break
            else:
                self._raise_exception(
                    ValueError,
                    f'Cube with name "{cube_name}" not found!',
                    with_traceback=False,
                )
            time.sleep(time_sleep)
            count += 1
        return False

    @timing
    def rename_grouped_elems(
        self, name: str, new_name: str, position: str = "left"
    ) -> dict:
        """
        Переименовать сгруппированные элементы самой левой/верхней размерности.
        :param name: (str) старое название группы элементов.
        :param new_name: (str) новое название группы элементов.
        :param position: (str) не обязательный параметр, возможны значения:
            'left' - переименование для левой размерности (значение по-умолчанию), 'top' - для верхней размерности.
        :return: (dict) результат команды ("group", "set_name").
        """
        if position not in ["left", "top"]:
            return self._raise_exception(
                ValueError, 'Param "position" must be either "left" or "top"!'
            )

        group_id = ""
        if position == "left":
            dim_ids_key, dim_items_key, error_msg = "left_dims", "left", "No left dims!"
        else:
            dim_ids_key, dim_items_key, error_msg = "top_dims", "top", "No top dims!"

        # получаем идентификатор самой левой/верхней размерности, а также элементы этой размерности
        res = self.execute_olap_command(
            command_name="view",
            state="get",
            from_row=0,
            from_col=0,
            num_row=1000,
            num_col=1000,
        )
        all_dims_ids = self.h.parse_result(res, dim_ids_key)
        if not len(all_dims_ids):
            return self._raise_exception(
                PolymaticaException, error_msg, with_traceback=False
            )
        dim_id = all_dims_ids[0]
        dim_elems = self.h.parse_result(res, dim_items_key)

        # вытащить идентификатор группировки размерности (если он есть у этого элемента)
        try:
            for elem in dim_elems:
                current_elem = elem[0]
                if "value" in current_elem and current_elem["value"] == name:
                    group_id = current_elem["group_id"]
                    break
        except KeyError:
            msg = f'No grouped dimensions with name "{name}"!'
            return self._raise_exception(ValueError, msg)

        if not group_id:
            return self._raise_exception(
                ValueError,
                f"For the dim no such elem: {name}",
                with_traceback=False,
            )
        return self.execute_olap_command(
            command_name="group",
            state="set_name",
            dim_id=dim_id,
            group_id=group_id,
            name=new_name,
        )

    @timing
    def group_dimensions(
        self,
        *,
        group_name: str,
        dim_items: Union[list, set, tuple] = None,
        position: str = "left",
    ) -> dict:
        """
        Группировка заданных либо отмеченных элементов размерности.
        Вызвать метод можно только передав аргументы по именам (keyword-only аргументы) - см. примеры вызовов ниже.
        Ограничения на группировку:
            1. Группируются только элементы самой левой либо самой верхней размерности.
            2. Для корректности группировки элементы самой левой (самой верхней) размерности должны быть свёрнуты.
        :param group_name: (str) название новой сгруппированной размерности; обязательный параметр, ожидается строка.
        :param dim_items: (list/set/tuple) список элементов самой левой/верхней размерности, которые
            нужно сгруппировать;
            не обязательный параметр, ожидается один из итерируемых объектов - список, множество или кортеж.
            Возможные кейсы:
            1. Если параметр не задан, будут сгруппированы все выделенные элементы
                самой левой (самой верхней) размерности.
            2. Если параметр не задан и нет выделенных элементов самой левой (самой верхней) размерности
                - сгенерируется ошибка.
            3. Если параметр задан, но одного или нескольких указанных элементов нет в размерности -
                также будет сгенерирована ошибка.
            4. Если параметр задан, но при этом также отмечены элементы размерности - значения, заданные в параметре,
                будут в приоритете над отмеченными.
                При этом, после группировки значений параметра, существующие отметки элементов размерности обнулятся.
            Все элементы итерируемого объекта должны быть строками.
        :param position: (str) не обязательный параметр, возможны значения:
            'left' - группировка левой размерности (значение по-умолчанию), 'top' - группировка верхней размерности.
        :return: (dict) результат команды ("view", "group").
        :call_example:
            # импорт и инициализация класса:
            from polyapi import business_scenarios
            sc = business_scenarios.BusinessLogic(login="login", password="password", url="url")
            # открытие куба и вынос размерностей
            sc.get_cube("cube_name")
            sc.move_dimension("dim1", "left", 0)
            sc.move_dimension("dim2", "left", 1)
            sc.move_dimension("dim3", "up", 0)
            sc.move_dimension("dim4", "up", 1)
            # группируем элементы ["item1", "item2"] самой левой размерности ("dim1")
            result = sc.group_dimensions(group_name="groupped_dim_1", dim_items=["item1", "item2"])
            # тоже самое действие, что на примере выше, только с явным указанием параметра position
            result = sc.group_dimensions(group_name="groupped_dim_2", dim_items=["item1", "item2"], position="left")
            # группируем элементы ["item3", "item4"] самой верхней размерности ("dim3")
            result = sc.group_dimensions(group_name="groupped_dim_3", dim_items=["item3", "item4"], position="top")
            # группируем все выделенные элементы самой верхней размерности ("dim3")
            result = sc.group_dimensions(group_name="groupped_dim_4", position="top")
        Генерируемые ошибки:
            'Param "group_name" must be "str" type!' - если параметр "group_name" имеет тип, отличный от "str".
            'Group name cannot be empty (param "group_name")!' - если в параметр "group_name" передана пустая строка.
            'Param "dim_items" must be "list", "set" or "tuple" type!' - если параметр "dim_items" имеет тип,
                отличный от "list", "set" или "tuple".
            'Param "position" must be either "left" or "top"!' - если параметр "position" имеет значение,
                отличное от left" или "top".
            'Expected "str" type in "dim_items" param!' - если хотя бы один элемент из параметра "dim_items" имеет тип,
                отличный от "str".
            'Left dimension not found!' - если в рабочую область не вынесена ни одна левая размерность
                в группировке по левым размерностям.
            'Top dimension not found!' - если в рабочую область не вынесена ни одна верхняя размерность
                в группировке по верхним размерностям.
            'Items <> not found!' - если в параметре "dim_items" указан один или несколько элементов,
                отсутствующих в размерности, в которой осуществляется группировка.
            'Error while selecting elements: <>' - возникла какая-либо ошибка во время выделения элементов размерности.
            'Selected dimension elements not found!' - если отсутствуют выделенные элементы размерности в случае,
                когда параметр "dim_items" не указан.
            'Left/Top dimension items expanded!' - если самая левая (самая верхняя) размерность оказалась развёрнута.
        """
        # проверки параметров
        try:
            if dim_items is None:
                dim_items = list()
            self.checks(self.func_name, group_name, dim_items, position)
        except Exception as exn:
            return self._raise_exception(ValueError, str(exn), with_traceback=False)

        # удаляем все пробельные символы в dim_items и проверяем, что все элементы имеют тип str
        def check_and_strip_item(item: Any) -> str:
            if isinstance(item, str):
                return item.strip()
            return self._raise_exception(
                ValueError,
                'Expected "str" type in "dim_items" param!',
                with_traceback=False,
            )

        dim_items = list(map(check_and_strip_item, dim_items))

        # получаем количество левых и верхних размерностей
        left_dims_count, top_dims_count = self._get_left_and_top_dims_count()
        if position == "left" and left_dims_count == 0:
            return self._raise_exception(
                PolymaticaException, "Left dimension not found!", with_traceback=False
            )
        if position == "top" and top_dims_count == 0:
            return self._raise_exception(
                PolymaticaException, "Top dimension not found!", with_traceback=False
            )

        new_group_name, num_pos = "", 1 if position == "left" else 2

        # если пользователь задал конкретные элементы размерности для группировки - ищем их
        # в противном случае определяем, есть ли отмеченные элементы размерности, и если есть - группируем их
        if dim_items:
            # получаем информацию о том, свёрнута или нет необходимая размерность;
            # размерности должны быть свёрнуты, чтобы группировка произошла корректно,
            # в противном случае придётся извлекать данные по левым/верхним размерностям из ("view", "get")
            # и анализировать флаги
            collapse_info = self.execute_olap_command(
                command_name="view",
                state="get",
                from_row=0,
                from_col=0,
                num_row=1,
                num_col=1,
            )
            collapse_flags = self.h.parse_result(collapse_info, f"{position}_flags")
            # 0 - размерность свёрнута, 1 - развёрнута
            if collapse_flags[0] == 1:
                error_msg = f"{position.capitalize()} dimension items expanded!"
                return self._raise_exception(
                    PolymaticaException, error_msg, with_traceback=False
                )

            # получение всех элементов размерности для дальнейшей группировки:
            # либо самая левая вынесенная размерность, либо сама верхняя (в зависимости от параметра position)
            result = self.execute_olap_command(
                command_name="view",
                state="get_2",
                from_row=0,
                from_col=0,
                num_row=1000,
                num_col=100,
            )
            data = self.h.parse_result(result, "data")
            if position == "left":
                total_dim_items = [lst[0].strip() for lst in data[1 + top_dims_count :]]
            else:
                total_dim_items = [item.strip() for item in data[0][left_dims_count:-1]]

            # проверяем, все ли элементы размерности, указанные пользователем, есть в общем списке элементов
            # если текущий элемент есть - сохраняем его индекс, в противном случае - генерируем ошибку
            selected_indexes, not_found_items = set(), list()
            for current_dim_value in dim_items:
                if current_dim_value in total_dim_items:
                    selected_indexes.add(total_dim_items.index(current_dim_value))
                else:
                    not_found_items.append(current_dim_value)
            if not_found_items:
                return self._raise_exception(
                    PolymaticaException,
                    f"Items {not_found_items} not found!",
                    with_traceback=False,
                )

            # снимаем все существующие отметки, если они есть
            self.unselect_all_dims(position)

            # отмечаем выбранные элементы
            commands, sorted_indexes = list(), sorted(selected_indexes)
            for index in sorted_indexes:
                commands.append(
                    self.olap_command.collect_command(
                        "olap",
                        "view",
                        "select_change",
                        position=num_pos,
                        line=index,
                        level=0,
                    )
                )
            query = self.olap_command.collect_request(*commands)
            try:
                self.exec_request.execute_request(query)
            except Exception as exn:
                return self._raise_exception(
                    PolymaticaException,
                    f"Error while selecting elements: {exn}",
                )

            # непосредственно, группировка выделенных элементов
            result = self.execute_olap_command(
                command_name="view",
                state="group",
                position=num_pos,
                line=sorted_indexes[0],
                level=0,
            )
            new_group_name = self.h.parse_result(result, "name")
        else:
            # получаем информацию об отмеченных элементах крайней левой/верхней размерности
            flags_data = self.execute_olap_command(
                command_name="view",
                state="get",
                from_row=0,
                from_col=0,
                num_row=1000,
                num_col=1000,
            )
            items = self.h.parse_result(flags_data, position)
            positions = set()
            flags_value = [
                1,
                3,
            ]  # TODO: уточнить у сервера точные значения, ибо документации нигде не нашёл
            for i, row_items in enumerate(items):
                first_item = row_items[0]
                if "value" in first_item and first_item["flags"] in flags_value:
                    positions.add(i)
            if not positions:
                return self._raise_exception(
                    PolymaticaException,
                    "Selected dimension elements not found!",
                    with_traceback=False,
                )

            # т.к. выделенные элементы обнаружены, то группируем их
            positions = sorted(positions)
            result = self.execute_olap_command(
                command_name="view",
                state="group",
                position=num_pos,
                line=positions[0],
                level=0,
            )
            new_group_name = self.h.parse_result(result, "name")

        # переименовываем созданную группу
        self.rename_grouped_elems(
            name=new_group_name, new_name=group_name, position=position
        )

        # обновляем общее количество строк и возвращаем результат
        self.update_total_row()
        return result

    @timing
    def group_measures(self, measures_list: List, group_name: str) -> dict:
        """
        Группировка фактов в (левой) панели фактов
        :param measures_list: (List) список выбранных значений
        :param group_name: (str) новое название созданной группы
        :return: (dict) command_name="fact", state="unselect_all"
        """
        for measure in measures_list:
            # выделить факты
            measure_id = self.get_measure_id(measure)
            self.execute_olap_command(
                command_name="fact",
                state="set_selection",
                fact=measure_id,
                is_seleceted=True,
            )

        # сгруппировать выбранные факты
        self.execute_olap_command(
            command_name="fact", state="create_group", name=group_name
        )

        self.func_name = "group_measures"

        # снять выделение
        return self.execute_olap_command(command_name="fact", state="unselect_all")

    @timing
    def close_layer(self, layer_id: str) -> dict:
        """
        Закрыть указанный слой.
        :param layer_id: идентификатор закрываемого слоя.
        :return: (dict) результат команды ("user_layer", "close_layer").
        """
        # проверка, что указанный слой вообще существует
        if layer_id not in self.layers_list:
            return self._raise_exception(
                PolymaticaException,
                f'Layer with ID "{layer_id}" not exists!',
                with_traceback=False,
            )

        # cформировать список из всех неактивных слоев
        unactive_layers_list = set(self.layers_list) - {layer_id}

        # если указанный слой - единственный в списке слоев, то нужно создать и активировать новый слой
        if len(unactive_layers_list) == 0:
            new_layer = self.create_layer(set_active=True)
            unactive_layers_list.add(new_layer)

        # активировать первый неактивный слой
        non_active_layer = next(iter(unactive_layers_list))
        self.execute_manager_command(
            command_name="user_layer",
            state="set_active_layer",
            layer_id=non_active_layer,
        )

        # закрыть слой
        result = self.execute_manager_command(
            command_name="user_layer", state="close_layer", layer_id=layer_id
        )

        # удалить из переменных класса закрытый слой
        self.active_layer_id = non_active_layer
        self.layers_list.remove(layer_id)
        return result

    @timing
    def create_layer(self, set_active: bool = True) -> str:
        """
        Создать слой (с помощью команды "user_layer", "create_layer").
        :param set_active: (bool) сделать слой активным, по умолчанию True.
        :return: (str) id слоя.
        """
        # Проверка типа параметра
        params = validate_params(
            CreateLayerParams, self._raise_exception, set_active=set_active
        )
        set_active = params.set_active

        # Создание слоя
        result = self.execute_manager_command(
            command_name="user_layer", state="create_layer"
        )
        new_layer_id = self.h.parse_result(
            result=result, key="layer", nested_key="uuid"
        )

        # Сделать слой активным, обновив переменную с id актвного слоя
        if set_active:
            self.set_layer_focus(new_layer_id)

        # Получить данные о слоях сессии
        session_layers_lst = self._get_session_layers()

        # Генерируем уникальное имя слоя и присваиваем это имя текущему слою
        session_layers_names_without_current_layer = [
            layer.get("name")
            for layer in session_layers_lst
            if layer["uuid"] != new_layer_id
        ]
        new_layer_name = generate_unique_layer_name(
            session_layers_names_without_current_layer
        )
        self.execute_manager_command(
            command_name="user_layer",
            state="rename_layer",
            layer_id=new_layer_id,
            name=new_layer_name,
        )
        # Обновить список слоев сессии
        self.layers_list = [layer.get("uuid") for layer in session_layers_lst]

        return new_layer_id

    def _expand_dims(self, dims: list, position: int):
        """
        Развернуть все размерности OLAP-модуля (верхние или левые).
        :param dims: (list) список размерностей (верхних или левых).
        :param position: (int) позиция: 1 - левые размерности, 2 - верхние размерности.
        """
        if position not in [1, 2]:
            return self._raise_exception(
                ValueError, 'Param "position" must be 1 or 2!', with_traceback=False
            )

        # если нет размерностей или вынесена только одна размерность, то нечего разворачивать (иначе упадёт ошибка)
        dims = dims or []
        if len(dims) < 2:
            return

        # сбор команд на разворот размерностей
        commands = []
        for i in range(0, len(dims) - 1):
            command = self.olap_command.collect_command(
                "olap", "view", "fold_all_at_level", position=position, level=i
            )
            commands.append(command)

        # выполняем собранные команды и обновляем число строк мультисферы
        if commands:
            query = self.olap_command.collect_request(*commands)
            try:
                self.exec_request.execute_request(query)
            except Exception as e:
                return self._raise_exception(ValueError, str(e))
        self.update_total_row()

    def _collap_dims(self, dims: list, position: int):
        """
        Свернуть все размерности OLAP-модуля (верхние или левые).
        :param dims: (list) список размерностей (верхних или левых).
        :param position: (int) позиция: 1 - левые размерности, 2 - верхние размерности.
        """
        if position not in [1, 2]:
            return self._raise_exception(
                ValueError, 'Param "position" must be 1 or 2!', with_traceback=False
            )

        # если нет размерностей или вынесена только одна размерность, то нечего сворачивать (иначе упадёт ошибка)
        dims = dims or []
        if len(dims) < 2:
            return

        self.execute_olap_command(
            command_name="view", state="unfold_all_at_level", position=position, level=0
        )
        self.update_total_row()

    @timing
    def expand_all_left_dims(self):
        """
        Развернуть все левые размерности OLAP-модуля. Метод ничего не принимает и ничего не возвращает.
        :call_example:
            1. Инициализируем класс и OLAP-модуль:
                bl_test = sc.BusinessLogic(login="login", password="password", url="url")
                # открываем куб и выносим все необходимые размерности влево
            2. Вызываем непосредственно метод:
                bl_test.expand_all_left_dims()
        """
        # получаем все левые размерности
        view_data = self.execute_olap_command(
            command_name="view",
            state="get",
            from_row=0,
            from_col=0,
            num_row=1,
            num_col=1,
        )
        left_dims = self.h.parse_result(result=view_data, key="left_dims")
        # разворачиваем их
        self._expand_dims(left_dims, 1)

    @timing
    def expand_all_up_dims(self):
        """
        Развернуть все верхние размерности OLAP-модуля. Метод ничего не принимает и ничего не возвращает.
        :call_example:
            1. Инициализируем класс и OLAP-модуль:
                bl_test = sc.BusinessLogic(login="login", password="password", url="url")
                # открываем куб и выносим все необходимые размерности вверх
            2. Вызываем непосредственно метод:
                bl_test.expand_all_up_dims()
        """
        # получаем все верхние размерности
        view_data = self.execute_olap_command(
            command_name="view",
            state="get",
            from_row=0,
            from_col=0,
            num_row=1,
            num_col=1,
        )
        top_dims = self.h.parse_result(result=view_data, key="top_dims")
        # разворачиваем их
        self._expand_dims(top_dims, 2)

    @timing
    def collap_all_left_dims(self):
        """
        Свернуть все левые размерности OLAP-модуля. Метод ничего не принимает и ничего не возвращает.
        :call_example:
            1. Инициализируем класс и OLAP-модуль:
                bl_test = sc.BusinessLogic(login="login", password="password", url="url")
                # открываем куб, выносим все необходимые размерности влево и раскрываем их
            2. Вызываем непосредственно метод:
                bl_test.collap_all_left_dims()
        """
        # получаем все левые размерности
        view_data = self.execute_olap_command(
            command_name="view",
            state="get",
            from_row=0,
            from_col=0,
            num_row=1,
            num_col=1,
        )
        left_dims = self.h.parse_result(result=view_data, key="left_dims")
        # сворачиваем их
        self._collap_dims(left_dims, 1)

    @timing
    def collap_all_up_dims(self):
        """
        Свернуть все верхние размерности OLAP-модуля. Метод ничего не принимает и ничего не возвращает.
        :call_example:
            1. Инициализируем класс и OLAP-модуль:
                bl_test = sc.BusinessLogic(login="login", password="password", url="url")
                # открываем куб, выносим все необходимые размерности вверх и раскрываем их
            2. Вызываем непосредственно метод:
                bl_test.collap_all_up_dims()
        """
        # получаем все верхние размерности
        view_data = self.execute_olap_command(
            command_name="view",
            state="get",
            from_row=0,
            from_col=0,
            num_row=1,
            num_col=1,
        )
        top_dims = self.h.parse_result(result=view_data, key="top_dims")
        # сворачиваем их
        self._collap_dims(top_dims, 2)

    @timing
    def expand_all_dims(self):
        """
        Развернуть все размерности OLAP-модуля (и верхние, и левые). Метод ничего не принимает и ничего не возвращает.
        :call_example:
            1. Инициализируем класс и OLAP-модуль:
                bl_test = sc.BusinessLogic(login="login", password="password", url="url")
                # открываем куб и выносим все необходимые размерности вверх/влево
            2. Вызываем непосредственно метод:
                bl_test.expand_all_dims()
        """
        # получаем все размерности
        view_data = self.execute_olap_command(
            command_name="view",
            state="get",
            from_row=0,
            from_col=0,
            num_row=1,
            num_col=1,
        )
        # разворачиваем левые размерности
        left_dims = self.h.parse_result(result=view_data, key="left_dims")
        self._expand_dims(left_dims, 1)
        # разворачиваем верхние размерности
        top_dims = self.h.parse_result(result=view_data, key="top_dims")
        self._expand_dims(top_dims, 2)

    @timing
    def collap_all_dims(self):
        """
        Свернуть все размерности OLAP-модуля (и верхние, и левые). Метод ничего не принимает и ничего не возвращает.
        :call_example:
            1. Инициализируем класс и OLAP-модуль:
                bl_test = sc.BusinessLogic(login="login", password="password", url="url")
                # открываем куб, выносим все необходимые размерности вверх/влево и раскрываем их
            2. Вызываем непосредственно метод:
                bl_test.collap_all_dims()
        """
        # получаем все размерности
        view_data = self.execute_olap_command(
            command_name="view",
            state="get",
            from_row=0,
            from_col=0,
            num_row=1,
            num_col=1,
        )
        # сворачиваем левые размерности
        left_dims = self.h.parse_result(result=view_data, key="left_dims")
        self._collap_dims(left_dims, 1)
        # сворачиваем верхние размерности
        top_dims = self.h.parse_result(result=view_data, key="top_dims")
        self._collap_dims(top_dims, 2)

    @timing
    def move_up_dims_to_left(self) -> List:
        """
        Переместить верхние размерности влево, после чего развернуть их.
        :return: (List) преобразованный список идентификаторов левых размерностей.
        """
        self.get_multisphere_data()

        # выгрузить данные только из первой строчки мультисферы
        result = self.execute_olap_command(
            command_name="view",
            state="get",
            from_row=0,
            from_col=0,
            num_row=1,
            num_col=1,
        )
        left_dims = self.h.parse_result(result=result, key="left_dims")
        top_dims = self.h.parse_result(result=result, key="top_dims")

        # если в мультисфере нет ни одной верхней размерности, то дальше делать нечего - вернём пустой список
        if len(top_dims) == 0:
            return list()

        # вынести размерности влево, начиная с последней размерности списка
        for top_dim_id in top_dims[::-1]:
            self.move_dimension(
                dim_name=self.get_dim_name(top_dim_id), position="left", level=0
            )

        # на данный момент в мультисфере нет верхних размерностей;
        # учитывая этот факт, получаем информацию о том, есть ли данные в мультисфере
        # если же данные имеются, то разворачиваем их
        view_data = self.execute_olap_command(command_name="view", state="get_2")
        if len(self.h.parse_result(view_data, "data")) > 1:
            commands = []

            # для каждой верхней размерности делаем разворот аналогичной левой размерности
            for i in range(0, len(top_dims)):
                command = self.olap_command.collect_command(
                    module="olap",
                    command_name="view",
                    state="fold_all_at_level",
                    level=i,
                )
                commands.append(command)

            # если в мультисфере нет ни одной левой размерности,
            # то необходимо удалить последнюю команду fold_all_at_level, т.к. ее нельзя развернуть
            if len(left_dims) == 0:
                del commands[-1]

            # если команды были собраны - исполняем их
            if len(commands) > 0:
                query = self.olap_command.collect_request(*commands)
                try:
                    self.exec_request.execute_request(query)
                except Exception as e:
                    return self._raise_exception(PolymaticaException, str(e))

        output = top_dims + left_dims
        self.update_total_row()
        self.func_name = "move_up_dims_to_left"
        return output

    @timing
    def grant_permissions(
        self, user_name: str, clone_user: Union[str, bool] = False
    ) -> dict:
        """
        Предоставить пользователю роли и права доступа.
        :param user_name: (str) имя пользователя.
        :param clone_user: (str) имя пользователя, у которого будут скопированы роли и права доступа;
            если не указывать этот параметр, то пользователю будут выставлены ВСЕ роли и права.
        :return: (dict) результат команд ("user", "info") и ("user_cube", "change_user_permissions").
        """
        # получаем список пользователей
        result = self.execute_manager_command(command_name="user", state="list_request")
        users_data = self.h.parse_result(result=result, key="users")

        # проверяем, существуют ли указанные пользователи
        self._check_user_exists(user_name, users_data)
        if clone_user:
            self._check_user_exists(clone_user, users_data)

        # склонировать права пользователя
        if clone_user:
            clone_user_permissions = {
                k: v
                for data in users_data
                for k, v in data.items()
                if data["login"] == clone_user
            }
            user_permissions = {
                k: v
                for data in users_data
                for k, v in data.items()
                if data["login"] == user_name
            }
            requested_uuid = clone_user_permissions["uuid"]
            clone_user_permissions["login"], clone_user_permissions["uuid"] = (
                user_permissions["login"],
                user_permissions["uuid"],
            )
            user_permissions = clone_user_permissions
        # или предоставить все права
        else:
            user_permissions = {
                k: v
                for data in users_data
                for k, v in data.items()
                if data["login"] == user_name
            }
            user_permissions["roles"] = ALL_PERMISSIONS
            requested_uuid = user_permissions["uuid"]
        # cubes permissions for user
        result = self.execute_manager_command(
            command_name="user_cube",
            state="user_permissions_request",
            user_id=requested_uuid,
        )
        cube_permissions = self.h.parse_result(result=result, key="permissions")

        # для всех кубов проставить "accessible": True (если проставляете все права),
        # 'dimensions_denied': [], 'facts_denied': []
        if clone_user:
            cube_permissions = [
                dict(item, **{"dimensions_denied": [], "facts_denied": []})
                for item in cube_permissions
            ]
        else:
            cube_permissions = [
                dict(
                    item,
                    **{"dimensions_denied": [], "facts_denied": [], "accessible": True},
                )
                for item in cube_permissions
            ]
        # для всех кубов удалить cube_name
        for cube in cube_permissions:
            del cube["cube_name"]

        # предоставить пользователю роли и права доступа
        command1 = self.manager_command.collect_command(
            "manager", command_name="user", state="info", user=user_permissions
        )
        command2 = self.manager_command.collect_command(
            "manager",
            command_name="user_cube",
            state="change_user_permissions",
            user_id=user_permissions["uuid"],
            permissions_set=cube_permissions,
        )
        query = self.manager_command.collect_request(command1, command2)
        try:
            result = self.exec_request.execute_request(query)
        except Exception as e:
            return self._raise_exception(RightsError, str(e))
        return result

    def _set_measure_select(
        self, is_seleceted: bool, measure_name: str = "", measure_id: str = ""
    ) -> dict:
        """
        Выделить факт/отменить выделение факта с заданным названием или идентификатором.
        При вызове нужно обязательно указать либо название факта, либо его идентификатор.
        И то, и другое указывать не нужно: в таком случае название факта будет проигнорировано.
        :param is_seleceted: показывает, какая операция выполняется: выделение факта (True) или снятие отметки (False).
        :param measure_name: название факта.
        :param measure_id: идентификатор факта.
        :return: результат работы команды ("fact", "set_selection").
        """
        # проверка на заданность имени/идентификатора
        try:
            self.checks("set_measure_select", measure_name, measure_id)
        except Exception as ex:
            return self._raise_exception(ValueError, str(ex), with_traceback=False)

        # если идентификатор не задан - получаем его по имени, а если задан - проверяем, что такой действительно есть
        self.get_multisphere_data()
        if not measure_id:
            measure_id = self.get_measure_id(measure_name, False)
        else:
            measure_id = measure_id.strip()
            measure_exists = False
            for item in self.multisphere_data.get("facts"):
                if item.get("id").strip() == measure_id:
                    measure_exists = True
                    break
            if not measure_exists:
                error_msg = f'Measure with id "{measure_id}" is not valid for Multisphere "{self.cube_name}"'
                return self._raise_exception(
                    ValueError, error_msg, with_traceback=False
                )

        # а теперь, зная идентификатор, выделяем факт (либо снимаем с него выделение - смотря что передано)
        return self.execute_olap_command(
            command_name="fact",
            state="set_selection",
            fact=measure_id,
            is_seleceted=is_seleceted,
        )

    @timing
    def select_measure(self, measure_name: str = "", measure_id: str = "") -> dict:
        """
        Выделить факт с заданным названием или идентификатором.
        При вызове нужно обязательно указать либо название факта, либо его идентификатор.
        И то, и другое указывать не нужно: в таком случае название факта будет проигнорировано.
        :param measure_name: название факта.
        :param measure_id: идентификатор факта.
        :return: результат работы команды ("fact", "set_selection").
        """
        result = self._set_measure_select(True, measure_name, measure_id)
        self.func_name = "select_measure"
        return result

    @timing
    def unselect_measure(self, measure_name: str = "", measure_id: str = "") -> dict:
        """
        Отменить выделение факта с заданным названием или идентификатором.
        При вызове нужно обязательно указать либо название факта, либо его идентификатор.
        И то, и другое указывать не нужно: в таком случае название факта будет проигнорировано.
        :param measure_name: название факта.
        :param measure_id: идентификатор факта.
        :return: результат работы команды ("fact", "set_selection").
        """
        result = self._set_measure_select(False, measure_name, measure_id)
        self.func_name = "unselect_measure"
        return result

    def _select_unselect_impl(self, position: str, state: str) -> dict:
        """
        Обобщённая реализация методов select_all_dims и unselect_all_dims.
        :param position: (str) позиция:
            'left' - выделение элементов левой размерности,
            'top' - выделение элементов верхней размерности.
        :param state: (str) исполняемое состояние команды "view".
        :return: (dict) результат команды ("view", <state>).
        """
        # получение списка элементов левой/верхней размерности (чтобы проверить, что список не пуст)
        result = self.execute_olap_command(
            command_name="view",
            state="get",
            from_row=0,
            from_col=0,
            num_row=1,
            num_col=1,
        )
        left_dims, top_dims = self.h.parse_result(
            result, "left_dims"
        ), self.h.parse_result(result, "top_dims")

        # проверки параметров, метод проверки вернёт числовой аналог позиции
        try:
            num_position = self.checks(
                "select_unselect_impl", left_dims, top_dims, position
            )
        except Exception as e:
            return self._raise_exception(
                PolymaticaException, str(e), with_traceback=False
            )

        # выделить все элементы/снять выделение со всех элементов
        return self.execute_olap_command(
            command_name="view", state=state, position=num_position, line=0, level=0
        )

    @timing
    def select_all_dims(self, position: str = "left") -> dict:
        """
        Выделение всех элементов самой левой/верхней размерности.
        :param position: (str) не обязательный параметр, возможны значения:
            'left' - выделение элементов левой размерности (значение по-умолчанию),
            'top' - выделение элементов верхней размерности.
        :return: (dict) результат команды ("view", "sel_all").
        :call_example:
            # импорт и инициализация класса:
            from polyapi import business_scenarios
            sc = business_scenarios.BusinessLogic(login="login", password="password", url="url", **params)
            # открытие куба и вынос размерностей
            sc.get_cube("cube_name")
            sc.move_dimension("dim1", "left", 0)
            sc.move_dimension("dim2", "left", 1)
            sc.move_dimension("dim3", "up", 0)
            sc.move_dimension("dim4", "up", 1)
            # выделяем элементы самой левой размерности ("dim1")
            res1 = sc.select_all_dims('left')
            # выделяем элементы самой верхней размерности ("dim3")
            res2 = sc.select_all_dims('top')
        """
        return self._select_unselect_impl(position, "sel_all")

    @timing
    def unselect_all_dims(self, position: str = "left") -> dict:
        """
        Снятие выделения со всех элементов самой левой/верхней размерности.
        :param position: (str) не обязательный параметр, возможны значения:
            'left' - выделение элементов левой размерности (значение по-умолчанию),
            'top' - выделение элементов верхней размерности.
        :return: (dict) результат команды ("view", "unsel_all").
        :call_example:
            # импорт и инициализация класса:
            from polyapi import business_scenarios
            sc = business_scenarios.BusinessLogic(login="login", password="password", url="url", **params)
            # открытие куба и вынос размерностей
            sc.get_cube("cube_name")
            sc.move_dimension("dim1", "left", 0)
            sc.move_dimension("dim2", "left", 1)
            sc.move_dimension("dim3", "up", 0)
            sc.move_dimension("dim4", "up", 1)
            # предположим, что некоторые (или все) элементы размерностей "dim1" и "dim3" отмечены
            # снимаем выделение элементов самой левой размерности ("dim1")
            res1 = sc.unselect_all_dims('left')
            # снимаем выделение элементов самой верхней размерности ("dim3")
            res2 = sc.unselect_all_dims('top')
        """
        return self._select_unselect_impl(position, "unsel_all")

    @timing
    def select_custom_dim_elements(self, dim_path: str) -> dict:
        """
        Инверсия выделения элементов размерности: если до вызова метода заданный элемент был выделен,
        то произойдёт снятие выделения, и наоборот.
        ВАЖНО:
        1. Работает только с левыми размерностями.
        2. Чтобы выделить указанный элемент, необходимо, чтобы до него были раскрыты все узлы дерева размерностей.
        В противном случае заданный элемент найден не будет.
        3. В случае, если заданный элемент не найден (не раскрыты узлы до него или же такого элемента нет в принципе),
        то будет сгенерирована ошибка.
        4. Элементы "Всего" выделить нельзя (ни промежуточные, ни итоговые)!
        :param dim_path: (str) элементы размерностей в формате "dimension_value_0.dimension_value_1. ...",
            где "dimension_value_N" - элемент размерности N-го уровня;
            перечисление элементов размерностей должно происходить через точку;
            количество элементов (глубина значений) не должно быть больше числа вынесенных левых размерностей;
        :return: (dict) результат команды ("view", "select_change").
        """
        dim_values = [path.strip() for path in dim_path.split(".")]

        # скрываем промежуточные тоталы, если они есть
        need_change_total_mode = False
        if self.get_total_mode() is True:
            self.change_total_mode()
            need_change_total_mode = True

        # получаем число размерностей (левых/верхних)
        left_dims_count, _ = self._get_left_and_top_dims_count()

        # проверка на глубину значений
        if len(dim_values) > left_dims_count:
            return self._raise_exception(
                ValueError,
                'Depth of "dim_path" parameter values is greater than number of left dimensions!',
            )

        # получаем генератор данных
        self.update_total_row()
        gdf_gen = self.get_data_frame(
            units=self.total_row, show_all_columns=True, show_all_rows=True
        )
        dataset = list()
        for df, _ in gdf_gen:
            dataset.extend([list(item)[0:left_dims_count] for item in df.values])

        # определяем нужный номер строки
        line = -1
        for ind, datarow in enumerate(dataset):
            is_match = True
            # на данном этапе гарантируется, что длина списка dim_values не превосходит число левых/верхних размерностей
            for i in range(0, len(dim_values)):
                if dim_values[i] != datarow[i]:
                    is_match = False
                    break
            if is_match:
                line = ind
                break

        # если элемент не найден - вернём ошибку, иначе исполним команду на выделение элемента
        if line == -1:
            return self._raise_exception(
                PolymaticaException, f'Element "{dim_path}" not found!'
            )

        result = self.execute_olap_command(
            command_name="view",
            state="select",
            position=1,
            level=len(dim_values) - 1,
            line=line,
        )

        # если режим отображения тоталов был изменён, то возвращаем исходный режим, и возвращаем результат
        if need_change_total_mode:
            self.change_total_mode()
        return result

    @timing
    def load_sphere_chunk(
        self,
        units: int = UNITS_LOAD_DATA_CHUNK,
        convert_type: bool = False,
        default_value: Any = None,
        convert_empty_values: bool = True,
    ) -> dict:
        """
        Генератор, подгружающий мультисферу постранично (порциями строк).
        Особенности использования метода:
            1. В мультисфере не должно быть вынесенных вверх размерностей, иначе будет сгенерировано исключение.
            2. Для корректного получения данных необходимо,
                чтобы перед вызовом метода были развёрнуты все узлы мультисферы.
            3. Все тоталы (как промежуточные, так и итоговые) генератором выведены не будут вне зависимости от того,
                включены они или нет.
        :param units: (int) количество подгружаемых строк; по-умолчанию 100.
        :param convert_type: (bool) нужно ли преобразовывать данные из типов, определённых Полиматикой, к Python-типам;
            по-умолчанию False (т.е. не нужно).
        :param default_value: (Any) актуален только при convert_type = True;
            дефолтное значение, использующееся в случае, если не удалось преобразовать исходные данные к нужному типу;
            по-умолчанию None.
        :param convert_empty_values: (bool) актуален только при convert_type = True;
            нужно ли преобразовывать строки формата "(Пустой)"/"(Empty)" к дефолтному значению (см. default_value);
            по-умолчанию True (т.е. нужно).
        :return: (dict) словарь {имя колонки: значение колонки}.
        :call_example:
            # импорт модуля из библиотеки
            from polyapi import business_scenarios

            # инициализация класса BusinessLogic
            bs = business_scenarios.BusinessLogic(login="login", password="password", url="url", **args)

            # делаем все необходимые действия (открытие мультисферы, раскрытие всех узлов и тд)
            bs.get_cube('cube_name')
            bs.expand_all_dims()

            # получение генератора данных
            gen = bs.load_sphere_chunk(
                units="units",
                convert_type="convert_type",
                default_value="default_value",
                convert_empty_values="convert_empty_values"
            )

            # получение данных мультисферы чанками
            for row_data in gen:
                print(row_data)
        """
        warn_msg = 'Необходимо перейти на аналогичный метод класса "GetDataChunc"!'
        self.logger.warning(warn_msg)
        return GetDataChunk(self).load_sphere_chunk(
            units, convert_type, default_value, convert_empty_values
        )

    @timing
    def logout(self) -> dict:
        """
        Выйти из системы
        :return: command_name="user", state="logout"
        """
        self.logger.info("BusinessLogic session out")
        return self.execute_manager_command(command_name="user", state="logout")

    @timing
    def close_current_cube(self) -> dict:
        """
        Закрыть текущую мультисферу, если она есть.
        :return: (dict) результат команды ("user_iface", "close_module"), если мультисфера есть, иначе пустой словарь.
        """
        if not self.multisphere_module_id:
            return dict()

        # закрываем мультисферу
        result = self.close_module(self.multisphere_module_id)

        # если закрытие модуля отработало без ошибок, то переопределяем multisphere_module_id и возвращаем результат
        self.set_multisphere_module_id("")
        self.func_name = "close_current_cube"
        return result

    @timing
    def rename_group(self, group_name: str, new_name: str) -> dict:
        """
        Переименовать группу пользователей.
        :param group_name: (str) Название группы пользователей.
        :param new_name: (str) Новое название группы пользователей.
        :return: (dict) Команда ("group", "edit_group").
        """
        # all groups data
        result = self.execute_manager_command(
            command_name="group", state="list_request"
        )
        groups = self.h.parse_result(result, "groups")

        # empty group_data
        roles, group_uuid, group_members, description = "", "", "", ""

        # search for group_name
        for group in groups:
            # if group exists: saving group_data
            if group.get("name") == group_name:
                roles = group.get("roles")
                group_uuid = group.get("uuid")
                group_members = group.get("members")
                description = group.get("description")
                break

        # check is group exist
        try:
            self.checks(self.func_name, group_uuid, group_name, new_name)
        except Exception as e:
            return self._raise_exception(
                PolymaticaException, str(e), with_traceback=False
            )

        # group_data for request
        group_data = {
            "uuid": group_uuid,
            "name": new_name,
            "description": description,
            "members": group_members,
            "roles": roles,
        }
        return self.execute_manager_command(
            command_name="group", state="edit_group", group=group_data
        )

    def _create_olap_module(self, num_row: int = 10000, num_col: int = 100) -> dict:
        """
        Создать OLAP-модуль.
        :param num_row: количество отображаемых строк
        :param num_col: количество отображаемых колонок
        :return: self.multisphere_data
        """
        # Получить список слоев сессии
        session_layers_lst = self._get_session_layers()
        self.layers_list = [layer.get("uuid") for layer in session_layers_lst]

        # получить идентификатор текущего слоя, если он не задан, или создать новый слой
        if not self.active_layer_id:
            try:
                if session_layers_lst:
                    self.active_layer_id = session_layers_lst[0].get("uuid")
                else:
                    self.active_layer_id = self.create_layer()
                    self.layers_list.append(self.active_layer_id)
            except Exception as e:
                error_msg = f"Error while parsing response: {e}"
                return self._raise_exception(PolymaticaException, error_msg)

        # Инициализировать слой и дождаться его загрузки
        self.execute_manager_command(
            command_name="user_layer", state="init_layer", layer_id=self.active_layer_id
        )
        progress = 0
        while progress < 100:
            result = self.execute_manager_command(
                command_name="user_layer",
                state="get_load_progress",
                layer_id=self.active_layer_id,
            )
            progress = self.h.parse_result(result=result, key="progress")

        # cоздать OLAP-модуль для куба <cube_id> на слое <layer_id>:
        initial_module_id = "00000000-00000000-00000000-00000000"
        result = self.create_multisphere_from_cube(
            module_id=initial_module_id,
            after_module_id=initial_module_id,
            module_type=MULTISPHERE_ID,
        )

        # получение идентификатора OLAP-модуля
        created_module_id = self.h.parse_result(
            result=result, key="module_desc", nested_key="uuid"
        )
        self.set_multisphere_module_id(created_module_id)

        # устанавливаем новое имя OLAP-модулю
        self.set_olap_module_name(
            created_module_id, self._form_olap_module_name(self.cube_name)
        )

        # рабочая область прямоугольника
        view_params = {
            "from_row": 0,
            "from_col": 0,
            "num_row": num_row,
            "num_col": num_col,
        }

        # получить список размерностей и фактов, а также текущее состояние таблицы со значениями
        # (рабочая область модуля мультисферы)
        query = self.olap_command.multisphere_data_query(
            self.multisphere_module_id, view_params
        )
        try:
            result = self.exec_request.execute_request(query)
        except Exception as e:
            return self._raise_exception(PolymaticaException, str(e))

        # multisphere data
        self.multisphere_data = {"dimensions": "", "facts": "", "data": ""}
        for item, index in [("dimensions", 0), ("facts", 1), ("data", 2)]:
            self.multisphere_data[item] = result["queries"][index]["command"][item]
        return self.multisphere_data

    def create_multisphere_from_cube(
        self, module_id: str, after_module_id: str, module_type: int
    ) -> dict:
        """
        Создать мультисферу из куба.
        :param module_id: Идентификатор модуля (str)
        :param after_module_id: Идентификатор модуля, после которого будет расположен новый модуль (str)
        :param module_type: Тип модуля (int)
        :return: (dict) Команда ("user_iface", new_module_desc")
        """
        result = self.execute_manager_command(
            command_name="user_iface",
            state="create_module",
            layer_id=self.active_layer_id,
            cube_id=self.cube_id,
            module_id=module_id,
            after_module_id=after_module_id,
            module_type=module_type,
        )
        return result

    @timing
    def get_cubes_for_scenarios_by_userid(
        self, user_name: str, user_password: str = None
    ) -> List:
        """
        Для заданного пользователя получить список с данными о сценариях и используемых в этих сценариях мультисферах.
        :param user_name: (str) имя пользователя, под которым необходимо создать подключение.
        :param user_password: (str) пароль пользователя, под которым необходимо создать подключение;
            не нужно указывать, если требуется создать подключение для пользователя, по-умолчанию не имеющего пароля,
            например, временный пользователь.
        :return: (List) данные о сценариях и использующихся в них мультисферах в формате:
            [
                {
                    "uuid": "b8ffd729",
                    "name": "savinov_test",
                    "description": "",
                    "cube_ids": ["79ca1aa5", "9ce3ba59"],
                    "cube_names": ["nvdia", "Роструд_БФТ_F_Measures_"]
                },
                ...
            ]
        """
        # создаём новую сессию под указанным пользователем
        self._check_user_exists(user_name)
        sc = BusinessLogic(login=user_name, url=self.base_url, password=user_password)

        scripts_data = []

        # получить список сценариев
        script_list = self.get_scripts_description_list() or list()

        # получить список всех мультисфер
        cubes_data = self.get_cubes_list()

        for script in script_list:
            # получаем список мультисфер в сценарии с заданным идентификатором
            cube_ids = self.get_scenario_cube_ids(scenario_id=script.get("id"))

            # поиск названий мультисфер
            cube_names = []
            for cube in cubes_data:
                for cube_id in cube_ids:
                    if cube_id == cube.get("uuid"):
                        cube_name = cube.get("name", "").rstrip()
                        cube_names.append(cube_name)

            # сохраняем данные для заданного сценария
            script_data = {
                "uuid": script.get("id"),
                "name": script.get("name"),
                "description": script.get("description"),
                "cube_ids": cube_ids,
                "cube_names": cube_names,
            }
            scripts_data.append(script_data)

        # убить сессию пользователя user_name
        sc.logout()
        self.func_name = "get_cubes_for_scenarios_by_userid"
        return scripts_data

    @timing
    def get_cubes_for_scenarios(self) -> List:
        """
        Получить список с данными о сценариях и используемых в этих сценариях мультисферах.
        :return: (List) данные о сценариях и использующихся в них мультисферах в формате:
            [
                {
                    "uuid": "b8ffd729",
                    "name": "savinov_test",
                    "description": "",
                    "cube_ids": ["79ca1aa5", "9ce3ba59"],
                    "cube_names": ["nvdia", "Роструд_БФТ_F_Measures_"]
                },
                ...
            ]
        """
        scripts_data = []

        # получить список сценариев
        script_list = self.get_scripts_description_list() or list()

        # получить список всех мультисфер
        cubes_data = self.get_cubes_list()

        for script in script_list:
            # получаем список мультисфер в сценарии с заданным идентификатором
            cube_ids = self.get_scenario_cube_ids(scenario_id=script.get("id"))

            # поиск названий мультисфер
            cube_names = []
            for cube in cubes_data:
                for cube_id in cube_ids:
                    if cube_id == cube.get("uuid"):
                        cube_name = cube.get("name", "").rstrip()
                        cube_names.append(cube_name)

            # сохраняем данные для заданного сценария
            script_data = {
                "uuid": script.get("id"),
                "name": script.get("name"),
                "description": script.get("description"),
                "cube_ids": cube_ids,
                "cube_names": cube_names,
            }
            scripts_data.append(script_data)

        self.func_name = "get_cubes_for_scenarios"
        return scripts_data

    @timing
    def polymatica_health_check_user_sessions(self) -> int:
        """
        Подсчет активных пользовательских сессий (для целей мониторинга).
        :return: (int) количество активных пользовательских сессий.
        """
        # получаем список пользователей
        res = self.execute_manager_command(command_name="admin", state="get_user_list")

        # преобразовать полученную строку к utf-8
        res = res.decode("utf-8")

        # преобразовать строку к словарю
        res = ast.literal_eval(res)

        # получаем информацию о пользователях
        users_info = self.h.parse_result(res, "users")

        # непосредственно сам подсчёт
        user_sessions = 0
        for user in users_info:
            if user["is_online"]:
                user_sessions += 1
        return user_sessions

    @timing
    def polymatica_health_check_all_multisphere_updates(self) -> dict:
        """
        Проверка ошибок обновления всех мультисфер (для целей мониторинга).
        :return: (dict) словарь со статусами обновлений мультисфер в формате {'cube_name': 'value'}, где value:
            0 - если ошибок обновления данных мультисферы не обнаружено, и мультисфера доступа пользователям
            1 - если последнее обновление мультисферы завершилось с ошибкой, но мультисфера доступна пользователям
            2 - если последнее обновление мультисферы завершилось с ошибкой, и она не доступна пользователям
            OTHER - другие значения update_error и available
        """
        cubes_list = self.get_cubes_list()

        # словарь со статусами обновлений мультисфер
        multisphere_upds = {}
        for cube in cubes_list:
            if cube["update_error"] and not cube["available"]:
                multisphere_upds.update({cube["name"]: 2})
                continue
            elif cube["update_error"] and cube["available"]:
                multisphere_upds.update({cube["name"]: 1})
                continue
            elif not cube["update_error"] and cube["available"]:
                multisphere_upds.update({cube["name"]: 0})
                continue
            else:
                multisphere_upds.update({cube["name"]: "OTHER"})

        self.func_name = "polymatica_health_check_all_multisphere_updates"
        return multisphere_upds

    @timing
    def polymatica_health_check_multisphere_updates(self, ms_name: str) -> int:
        """
        Проверка ошибок последнего обновления мультисферы (для целей мониторинга).
        :param ms_name: (str) Название мультисферы.
        :return: (int)
            0, если не обнаружено ошибок обновления данных указанной мультисферы и мультисфера доступна.
            1, если есть ошибки обновления мультисферы или она недоступна.
        """
        cubes_list = self.get_cubes_list()
        self.func_name = "polymatica_health_check_multisphere_updates"

        # проверка названия мультисферы
        try:
            self.checks(self.func_name, cubes_list, ms_name)
        except Exception as e:
            return self._raise_exception(ValueError, str(e), with_traceback=False)

        # update_error - были ли ошибки обновления (True/False)
        # available - доступна ли мультисфера
        for cube in cubes_list:
            if cube["name"] == ms_name:
                if cube["update_error"] or not cube["available"]:
                    return 1
                break
        return 0

    @timing
    def polymatica_health_check_data_updates(self) -> Union[List, int]:
        """
        Проверка целостности данных после обновления мультисфер (для целей мониторинга).
        :return: (Union[List, int]) 0, если ошибок обновления данных не обнаружено, т.е.
            последнее обновление для всех мультисфер выполнено успешно, без ошибок;
            в противном случае список мультисфер, последнее обновление которых завершилось с ошибкой.
        """
        cubes_list = self.get_cubes_list()

        # список, содержащий перечень мультисфер, последнее обновление которых завершилось с ошибкой
        multisphere_upds = [
            cube.get("name") for cube in cubes_list if cube.get("update_error")
        ]

        self.func_name = "polymatica_health_check_data_updates"

        return 0 if not multisphere_upds else multisphere_upds

    @timing
    def get_layer_list(self) -> List:
        """
        Загрузка данных о слоях.
        :return: (list) список вида [[layer_id, layer_name], [...], ...], содержащий слои в том порядке,
            в котором они отображаются на интерфейсе.
        :call_example:
            1. Инициализируем класс: bl_test = sc.BusinessLogic(login="login", password="password", url="url")
            2. Вызов метода:
                layer_list = bl_test.get_layer_list()
                output: [["id", "name"], ["id", "name"], ...] - список слоёв для текущей сессии.
        """
        # получаем список слоёв
        layers_list = self._get_session_layers()

        # сортируем список слоёв по времени создания,
        # т.к. необходимо вернуть слои в том порядке, в котором они отображаются на интерфейсе
        layers_list.sort(key=lambda item: item.get("create_timestamp", 0))

        # проходим по списку слоёв и сохраняем их идентификаторы и названия
        layers = [
            [layer.get("uuid", str()), layer.get("name", str())]
            for layer in layers_list
        ]
        self.layers_list = [layer[0] for layer in layers]
        return layers

    @timing
    def set_layer_focus(self, layer: str) -> str:
        """
        Установка активности заданного слоя.
        :param layer: идентификатор/название слоя.
        :return: (str) идентификатор установленного активного слоя.
        :call_example:
            1. Инициализируем класс: bl_test = sc.BusinessLogic(login="login", password="password", url="url")
            2. Вызов метода:
                layer = "layer_id_or_layer_name"
                layer_id = bl_test.set_layer_focus(layer=layer)
                output: layer_id - идентификатор установленного активного слоя.
            3. Вызов метода с передачей неверного идентификатора/названия слоя:
                layer = "invalid_layer_id or invalid_layer_name"
                layer_id = bl_test.set_layer_focus(layer=layer)
                output: exception "Layer cannot be found by name or ID".
        """
        # получаем все слои мультисферы
        # layers имеет вид [[layer_id, layer_name], [...], ...]
        layers = self.get_layer_list()
        self.func_name = "set_layer_focus"

        # проходя по каждому слою, ищем соответствие среди имени/идентификатора
        for current_layer_params in layers:
            if layer in current_layer_params:
                layer_id = current_layer_params[0]
                s = {
                    "wm_layers2": {
                        "lids": [item[0] for item in layers],
                        "active": layer_id,
                    }
                }
                self.execute_manager_command(
                    command_name="user_layer",
                    state="set_active_layer",
                    layer_id=layer_id,
                )
                self.execute_manager_command(
                    command_name="user_iface",
                    state="save_settings",
                    module_id=self.authorization_uuid,
                    settings=s,
                )
                self.active_layer_id = layer_id
                return layer_id

        # если дошло сюда - слой с таким именем/идентификатором не найден, бросаем ошибку
        return self._raise_exception(
            PolymaticaException,
            "Layer cannot be found by name or ID",
            with_traceback=False,
        )

    @timing
    def get_active_layer_id(self) -> str:
        """
        Возвращает идентификатор активного слоя в текущей сессии.
        :return: (str) идентификатор активного слоя.
        """
        # если идентификатор активного слоя уже есть во внутренних переменных класса, то вернём его
        if self.active_layer_id:
            return self.active_layer_id

        # в противном случае попробуем получить этот идентификатор с интерфейсных настроек
        settings = self.execute_manager_command(
            command_name="user_iface",
            state="load_settings",
            module_id=self.authorization_uuid,
        )
        active_layer_id = (
            self.h.parse_result(result=settings, key="settings")
            .get("wm_layers2", dict())
            .get("active", "")
        )
        if active_layer_id:
            return active_layer_id

        # подразумеваем, что в сессии единственный дефолтный (начальный) слой - вернём его идентификатор
        # если же по каким-то причинам и его нет, то вернём пустую строку, т.к. никаких вариантов больше нет
        layers = self.get_layer_list()
        return layers[0][0] if layers else ""

    @timing
    def get_active_layer_name(self) -> str:
        """
        Возвращает название активного слоя.
        :return: (str) название слоя.
        """
        result = self.execute_manager_command(
            command_name="user_layer",
            state="get_layer",
            layer_id=self.get_active_layer_id(),
        )
        return self.h.parse_result(result, "layer", "name")

    def _get_modules_in_layer(self, layer_id: str, is_int_type: bool = True) -> List:
        """
        Возвращает список модулей на заданном слое.
        :param layer_id: идентификатор слоя, модули которого необходимо получить.
        :param is_int_type: флаг, показывающий, в каком виде выводить тип модуля:
            в числовом (500) или строковом ('Мультисфера'). Соответствующая мапа переводов хранится в CODE_NAME_MAP.
        :return: (list) список вида [[module_id, module_name, module_type, cube_id], [...], ...],
            содержащий информацию о модулях в текущем слое.
        """
        # получаем список всех модулей, находящихся в текущем слое
        settings = self.execute_manager_command(
            command_name="user_layer", state="get_layer", layer_id=layer_id
        )
        layer_info = self.h.parse_result(result=settings, key="layer") or dict()

        # проходя по каждому модулю, извлекаем из него информацию
        result = []
        for module in layer_info.get("module_descs"):
            module_id = module.get("uuid")
            module_name = module.get("name")
            base_module_type = module.get("type_id")
            module_type = (
                base_module_type
                if is_int_type
                else CODE_NAME_MAP.get(base_module_type, base_module_type)
            )
            cube_id = module.get("cube_id")

            if self.script_mode:
                module_setting = self.execute_manager_command(
                    command_name="user_iface", state="load_settings", module_id=module_id)
                module_info = self.h.parse_result(result=module_setting, key="settings") or dict()
                facts_format = module_info.get('config_storage')['facts-format']['__suffixes']
                result.append([module_id, module_name, module_type, facts_format])
            else:
                result.append([module_id, module_name, module_type, cube_id])
        return result

    @timing
    def get_module_list(self) -> List:
        """
        Возвращает список модулей в активном слое текущей сессии.
        :return: (list) список вида [[module_id, module_name, module_type, cube_id], [...], ...],
            содержащий информацию о модулях на активном слое.
        :call_example:
            1. Инициализируем класс: bl_test = sc.BusinessLogic(login="login", password="password", url="url")
            2. Вызов метода:
                module_list = bl_test.get_module_list()
                output: [["module_id", "module_name', "module_type", "cube_id"], [...], ...] - список модулей
                    в активном слое в текущей сессии.
        """
        # получаем идентификатор активного слоя
        active_layer_id = self.get_active_layer_id()
        if not active_layer_id:
            return self._raise_exception(
                PolymaticaException, "Active layer not set!", with_traceback=False
            )

        self.func_name = "get_module_list"

        # получаем модули на активном слое
        return self._get_modules_in_layer(active_layer_id, False)

    @timing
    def set_module_focus(self, module: str):
        """
        Установка фокуса на заданный модуль. Слой, на котором находится модуль, также становится активным.
        Ничего не возвращает.
        :param module: идентификатор/название модуля.
        :call_example:
            1. Инициализируем класс: bl_test = sc.BusinessLogic(login="login", password="password", url="url")
            2. Вызов метода:
                module = "module_id_or_module_name"
                bl_test.set_module_focus(module=module)
            3. Вызов метода с передачей неверного идентификатора/названия модуля:
                module = "invalid_module_id_or_invalid_module_name"
                bl_test.set_module_focus(module=module)
                output: exception "Module cannot be found by ID or name".
        """
        # получаем все слои; layers имеет вид [[layer_id, layer_name], [...], ...]
        layers = self.get_layer_list()
        self.func_name = "set_module_focus"

        set_id_types_map = {
            MULTISPHERE_ID: self.set_multisphere_module_id,
            GRAPH_ID: self._set_graph_module_id,
        }

        # проходя по каждому слою, получаем список его модулей
        for layer in layers:
            layer_id = layer[0]
            modules_info = self._get_modules_in_layer(layer_id)

            # module_info имеет формат [module_id, module_name, module_type]
            # перебираем все модули в текущем слое
            for module_info in modules_info:
                if module in module_info:
                    # делаем активным текущий слой
                    self.set_layer_focus(layer_id)

                    # делаем активным искомый модуль
                    set_id_types_map.get(module_info[2])(module_info[0])
                    self.func_name = "set_module_focus"
                    return

        # если дошло сюда - модуль с таким именем/идентификатором не найден, бросаем ошибку
        return self._raise_exception(
            PolymaticaException,
            "Module cannot be found by ID or name",
            with_traceback=False,
        )

    @timing
    def module_fold(self, module_id: Union[str, list], minimize: bool):
        """
        Свернуть/развернуть модули с заданными идентификаторами. Применимо не только к OLAP-модулям.
        :param module_id: (str or list) id/названия модулей, которые нужно свернуть/развернуть.
            Параметр может принимать как строку, так и список строк.
            Пример 1. module_id = "id or name" - будет свёрнут/развёрнут только заданный модуль (если он есть).
            Пример 2. module_id = ["id or name", "id or name", ...] -
                    будут свёрнуты/развёрнуты все указанные идентификаторы.
        :param minimize: (bool) True - свернуть модуль / False - развернуть модуль.
        :call_example:
            1. Инициализируем класс: bl_test = sc.BusinessLogic(login="login", password="password", url="url")
            2. Вызов метода:
                module, minimize = "module_id_or_module_name", "True or False"
                bl_test.module_fold(module_id=module, minimize=minimize)
            3. Вызов метода с передачей неверного идентификатора/названия модуля:
                module, minimize = "invalid_module_id_or_invalid_module_name", "True or False"
                bl_test.module_fold(module_id=module, minimize=minimize)
                output: exception "The following modules were not found: {module}"
        """
        # в module_id может быть как идентификатор/название мультисферы, так и список идентификаторов/названий
        if isinstance(module_id, str):
            module_ids = [module_id]
        elif isinstance(module_id, (list, set)):
            module_ids = module_id
        else:
            return self._raise_exception(
                ValueError, "Arg 'module_id' must be str or list!", with_traceback=False
            )

        # проверка параметра minimize
        if minimize not in [True, False]:
            return self._raise_exception(
                ValueError,
                "Arg 'minimize' can only be True or False!",
                with_traceback=False,
            )

        # сворачиваем/разворачиваем каждый заданный модуль
        error_modules = []
        for module_id in module_ids:
            # находим модуль с заданным идентификатором
            founded_module_ids = self._find_module(module_id)
            if not founded_module_ids:
                error_modules.append(module_id)
                continue
            for _, current_module_id in founded_module_ids:
                # получаем текущие настройки заданного модуля
                settings = self.execute_manager_command(
                    command_name="user_iface",
                    state="load_settings",
                    module_id=current_module_id,
                )
                current_module_settings = self.h.parse_result(settings, "settings")
                # сохраняем новые настройки
                current_module_settings.update({"minimize": minimize})
                self.execute_manager_command(
                    command_name="user_iface",
                    state="save_settings",
                    module_id=current_module_id,
                    settings=current_module_settings,
                )

        self.func_name = "module_fold"

        # генерируем ошибки/предупреждения
        if error_modules:
            message = (
                f"The following modules were not found: {str(error_modules)[1:-1]}"
            )
            # если все заданные модули были не найдены - бросаем ошибку, иначе предупреждение
            if len(error_modules) == len(module_ids):
                return self._raise_exception(
                    PolymaticaException, message, with_traceback=False
                )
            else:
                self.logger.warning(message)

    @timing
    def graph_create(
        self,
        g_type: Union[int, str] = 1,
        settings: str = "",
        grid: int = 3,
        labels: dict = None,
        other: dict = None,
        olap_module_id: str = "",
        m_size: dict = None,
    ) -> str:
        """
        Создать график с заданными параметрами на основе активной или заданной мультисферы.
        Описание параметров:

        :param g_type: тип графика; можно задавать как целочисленное значение, так и строковое.
            Возможные значения (указаны целочисленные и строковые варианты):
                [1, "lines"] - линии
                [2, "cylinders"] - цилиндры
                [3, "cumulative_cylinders"] - цилиндры с накоплением
                [4, "areas"] - области
                [5, "cumulative_areas"] - области с накоплением
                [6, "pies"] - пироги
                [7, "radar"] - радар
                [8, "circles"] - круги
                [9, "circles_series"] - серии кругов
                [10, "balls"] - шары
                [11, "pools"] - бассейны
                [12, "3d_pools"] - 3D-бассейны
                [13, "corridors"] - коридоры
                [14, "surface"] - поверхность
                [15, "graph"] - граф
                [16, "sankey"] - санкей
                [17, "chord"] - хордовая
                [18, "point"] - точечный
                [19, "point_series"] - серии точек.
            По-умолчанию (если не задан параметр) будет построен тип [1, "lines"] - линии.
            Для версии Полиматики 5.7 и выше доступны все перечисленные типы графиков, кроме
                [9, "circles_series"], [19, "point_series"].
            Для типа графика [13, "corridors"] необходимо установить расчётный факт в вид "Процент" и
            установить по нему расчёт по горизонтали - это необходимые условия построения этого графика.

        :param settings: битмап-строка настроек графиков, значениями могут быть только 0 или 1.
            Каждый тип графика имеет свой битмап настроек:
                1. {Заголовок, Легенда, Названия осей, Подписи на осях, Вертикальная ось справа} - актуально для типов:
                    [1, "lines"], [2, "cylinders"], [3, "cumulative_cylinders"], [4, "areas"], [5, "cumulative_areas"],
                    [8, "circles"], [9, "circles_series"], [11, "pools"], [13, "corridors"],
                    [18, "point"], [19, "point_series"].
                    По-умолчанию имеет значение "11110".
                2. {Заголовок, Легенда, Показывать подписи} - актуально для типов: [6, "pies"].
                    По-умолчанию имеет значение "111".
                3. {Заголовок, Легенда, Названия осей, Отображать метки на осях} - актуально для типов: [7, "radar"].
                    По-умолчанию имеет значение "1111".
                4. {Заголовок, Легенда, Названия осей, Подписи на осях} - актуально для типов:
                    [10, "balls"], [12, "3d_pools"].
                    По-умолчанию имеет значение "1111".
                5. {Заголовок, Названия осей, Подписи на осях} - актуально для типов: [14, "surface"].
                    По-умолчанию имеет значение "111".
                6. {Заголовок, Подсвечивать узлы} - актуально для типов: [15, "graph"].
                    По-умолчанию имеет значение "11".
                7. {Заголовок} - актуально для типов: [16, "sankey"].
                    По-умолчанию имеет значение "1".
                8. {Заголовок, Легенда} - актуально для типов: [17, "chord"].
                    По-умолчанию имеет значение "11".

        :param grid: настройка сетки.
            Типы графиков, не имеющие данной настройки (если для перечисленных типов данный параметр будет задан,
            то он будет проигнорирован):
                [6, "pies"], [7, "radar"], [10, "balls"], [12, "3d_pools"],
                [14, "surface"], [15, "graph"], [16, "sankey"], [17, "chord"]
            Все остальные типы графиков имеют одно из следующих значений:
                0 - Все линии, 1 - Горизонтальные линии, 2 - Вертикальные линии, 3 - Без сетки.
            Значение по-умолчанию (если не задан параметр) - 3.

        :param labels: настройка подписей на графиках.
            Типы графиков, не имеющие данной настройки (если для перечисленных типов данный параметр будет задан,
            то он будет проигнорирован):
                [6, "pies"], [7, "radar"], [14, "surface"], [15, "graph"], [16, "sankey"], [17, "chord"]
            Для типов графиков [1, "lines"], [2, "cylinders"], [3, "cumulative_cylinders"], [4, "areas"],
                [5, "cumulative_areas"], [13, "corridors"] это словарь вида:
                {'OX': <value>, 'OY': <value>, 'short_format': <value>}, где
                    OX - частота подписей по оси OX (от 5 до 30 с шагом 5); по-умолчанию 10
                    OY - частота подписей по оси OY (от 5 до 30 с шагом 5); по-умолчанию 10
                    short_format - нужно ли сокращать подпись (True/False); по-умолчанию False (только для версии 5.6)
                    division_value - цена деления;
                        возможны варианты: "no", "hundreds", "thousands", "millions", "billions", "trillions";
                        по-умолчанию "no";
            Для типов графиков [8, "circles"], [9, "circles_series"], [11, "pools"], [18, "point"],
                [19, "point_series"] это словарь вида: {'OX': <value>, 'OY': <value>}, где
                    OX - частота подписей по оси OX (от 5 до 30 с шагом 5); по-умолчанию 10
                    OY - частота подписей по оси OY (от 5 до 30 с шагом 5); по-умолчанию 10
                    division_value - цена деления;
                        возможны варианты: "no", "hundreds", "thousands", "millions", "billions", "trillions";
                        по-умолчанию "no";
            Для типов графиков [10, "balls"], [12, "3d_pools"] это словарь вида:
                {'OX': <value>, 'OY': <value>, 'OZ': <value>}, где
                    OX - частота подписей по оси OX (от 1 до 10 с шагом 0.5); по-умолчанию 2.5
                    OY - частота подписей по оси OY (от 1 до 10 с шагом 0.5); по-умолчанию 2.5
                    OZ - частота подписей по оси OZ (от 1 до 10 с шагом 0.5); по-умолчанию 2.5

        :param other: дополнительные настройки графиков.
            Типы графиков, не имеющие данной настройки (если для перечисленных типов данный параметр будет задан,
            то он будет проигнорирован):
                [4, "areas"], [7, "radar"], [16, "sankey"]
            Для типов графиков [1, "lines"], [13, "corridors"] это словарь вида:
                {'hints': <value>, 'show_points': <value>}, где
                    hints - нужно ли отображать подсказки к точкам (True/False); по-умолчанию False
                    show_points - нужно ли показывать точки (True/False); по-умолчанию True
            Для типа графика [2, "cylinders"] это словарь вида:
                {'hints': <value>, 'round': <value>, 'ident': <value>, 'ident_value': <value>}, где
                    hints - нужно ли отображать подсказки к цилиндрам (True/False); по-умолчанию False
                    round - нужно ли округлять подсказки до целых чисел; по-умолчанию False;
                        актуально только если значение параметра "hints" равно True
                    ident - отображать цилиндры с отступом (True/False); по-умолчанию True
                    ident_value - значение отступа (от 0 до 1 с шагом 0.05); по-умолчанию 0.9
            Для типа графика [3, "cumulative_cylinders"] это словарь вида:
                {'hints': <value>, 'round': <value>, 'graph_type': <value>}, где:
                    hints - нужно ли отображать подсказки к цилиндрам (True/False); по-умолчанию False
                    round - нужно ли округлять подсказки до целых чисел; по-умолчанию False;
                        актуально только если значение параметра "hints" равно True
                    graph_type - вид графика, значения: 'values'-значения, 'percents'-проценты; по-умолчанию 'values'
            Для типа графика [5, "cumulative_areas"] это словарь вида:
                {'graph_type': <value>}, где:
                    graph_type - вид графика, значения: 'values'-значения, 'percents'-проценты; по-умолчанию 'values'
            Для типа графика [6, "pies"] это словарь вида:
                {
                    'show_sector_values': <value>,
                    'min_sector': <value>,
                    'restrict_signature': <value>,
                    'size_of_signatures': <value>
                }, где:
                    show_sector_values - показывать значения на секторах; по-умолчанию False
                    min_sector - минимальный сектор (от 0 до 100 с шагом 1); по-умолчанию 0
                    restrict_signature - ограничить число подписей (от 0 до 100 с шагом 1); по-умолчанию 10
                    size_of_signatures - размер подписей (от 7 до 15 с шагом 1); по-умолчанию 12
            Для типа графика [8, "circles"] это словарь вида:
                {'diameter_range': <value>, 'diameter': <value>, 'show_trend_line': <value>}, где:
                    diameter_range - диапазон диаметров, записывается в виде кортежа (min, max), где min - нижняя
                        граница, а max - верхняя; обе границы должны быть в диапазоне от 1 до 50 с шагом 1;
                        верхняя граница не может быть меньше нижней; по-умолчанию (3, 15)
                    diameter - диаметр кругов (от 1 до 50 с шагом 1); по-умолчанию 10
                    show_trend_line - показать линию тренда (True/False); по-умолчанию False
            Для типов графиков [9, "circles_series"], [11, "pools"] это словарь вида:
                {'diameter_range': <value>, 'diameter': <value>}, где:
                    diameter_range - диапазон диаметров, записывается в виде кортежа (min, max), где min - нижняя
                        граница, а max - верхняя; обе границы должны быть в диапазоне от 1 до 50 с шагом 1;
                        верхняя граница не может быть меньше нижней; по-умолчанию (3, 15)
                    diameter - диаметр кругов (от 1 до 50 с шагом 1); по-умолчанию 10
            Для типа графика [10, "balls"] это словарь вида:
                {'show_shadows': <value>, 'diameter_range': <value>, 'diameter': <value>, 'colors': <value>}, где:
                    show_shadows - нужно ли отображать тени; по-умолчанию True
                    diameter_range - диапазон диаметров, записывается в виде кортежа (min, max), где min - нижняя
                        граница, а max - верхняя; обе границы должны быть в диапазоне от 4 до 48 с шагом 1;
                        верхняя граница не может быть меньше нижней; по-умолчанию (4, 48)
                    diameter - диаметр кругов (от 4 до 48 с шагом 1); по-умолчанию 4
                    colors - градиент шаров; ожидается список из 3х цветов в формате "#RRGGBB";
                        по-умолчанию ["#ffff00", "#3c9bea"];
            Для типа графика [12, "3d_pools"] это словарь вида:
                {'diameter_range': <value>, 'diameter': <value>}, где:
                    diameter_range - диапазон диаметров, записывается в виде кортежа (min, max), где min - нижняя
                        граница, а max - верхняя; обе границы должны быть в диапазоне от 4 до 48 с шагом 1;
                        верхняя граница не может быть меньше нижней; по-умолчанию (4, 48)
                    diameter - диаметр кругов (от 4 до 48 с шагом 1); по-умолчанию 4
            Для типа графика [14, "surface"] это словарь вида:
                {'show_carcass': <value>, 'opacity': <value>, 'colors': <value>}, где:
                    show_carcass - показать каркас; по-умолчанию False
                    opacity - прозрачность (от 0 до 100 с шагом 1); по-умолчанию 100
                    colors - цвета поверхности; ожидается список из 3х цветов в формате "#RRGGBB";
                        по-умолчанию ["#eaf7fb", "#3c9bea", "#08034f"]
            Для типа графика [15, "graph"] это словарь вида:
                {
                    'node_settings': <value>,
                    'edge_settings': <value>,
                    'neighboring_nodes_count': <value>,
                    'min_thickness_on_hover': <value>,
                    'opacity_of_unselected': <value>
                }, где:
                    node_settings - настройки узлов; представляет собой словарь вида:
                        {'colors': <value>, 'min_size': <value>, 'max_size': <value>}, где:
                            colors - переход цвета узлов, имеет вид: {'first': <value>, 'second': <value>};
                                ожидаются цвета в формате "#RRGGBB";
                                значения по-умолчанию: {'first': '#1f77b4', 'second': '#17becf'};
                                в случае задания только одного цвета - второй цвет берётся из значений по-умолчанию;
                                в случае, если не задан ни один цвет - оба берутся из значений по-умолчанию
                            min_size - минимальный размер узла (от 1 до 10 с шагом 0.1); по-умолчанию 1
                            max_size - максимальный размер узла (от 5 до 15 с шагом 0.1);
                                должен быть больше, чем max_size; по-умолчанию 10
                    edge_settings - настройки рёбер; представляет собой словарь вида:
                        {'colors': <value>, 'min_thickness': <value>, 'max_thickness': <value>}, где:
                            colors - переход цвета рёбер, имеет вид: {'first': <value>, 'second': <value>};
                                ожидаются цвета в формате "#RRGGBB";
                                значения по-умолчанию: {'first': '#1f77b4', 'second': '#17becf'};
                                в случае задания только одного цвета - второй цвет берётся из значений по-умолчанию;
                                в случае, если не задан ни один цвет - оба берутся из значений по-умолчанию
                            min_thickness - минимальная толщина ребра (от 1 до 5 с шагом 0.1); по-умолчанию 1
                            max_thickness - максимальная толщина ребра (от 5 до 10 с шагом 0.1);
                                должен быть больше, чем min_thickness; по-умолчанию 5
                    neighboring_nodes_count - количество выделенных соседних узлов при наведении (от 0 до 5 с шагом 1);
                        по-умолчанию 3
                    min_thickness_on_hover - диапазон минимальной толщины при наведении;
                        записывается в виде списка/кортежа (min, max), где min - нижняя граница, а max - верхняя;
                        обе границы должны быть в диапазоне от 0.5 до 5 с шагом 0.1;
                        верхняя граница не может быть меньше нижней; по-умолчанию (1, 3)
                    opacity_of_unselected - прозрачность невыделенных узлов (от 0 до 1 с шагом 0.01); по-умолчанию 0.7
            Для типа графика [17, "chord"] это словарь вида:
                {'show_title': <value>}, где:
                    show_title - показывать подписи (True/False); по-умолчанию True
            Для типа графика [18, "point"] это словарь вида:
                {'diameter': <value>, 'diameter_range': <value>, 'show_trend_line': <value>}, где:
                    diameter - диаметр кругов (от 1 до 50 с шагом 1); по-умолчанию 10
                    diameter_range - диапазон диаметров, записывается в виде кортежа (min, max), где min - нижняя
                        граница, а max - верхняя; обе границы должны быть в диапазоне от 1 до 50 с шагом 1;
                        верхняя граница не может быть меньше нижней; по-умолчанию (3, 15);
                    show_trend_line - показать линию тренда (True/False); по-умолчанию True
            Для типа графика [19, "point_series"] это словарь вида:
                {'diameter': <value>, 'show_trend_line': <value>}, где:
                    diameter - диаметр кругов (от 1 до 20 с шагом 0.5); по-умолчанию 6.5
                    show_trend_line - показать линию тренда (True/False); по-умолчанию True
            Помимо этого, все типы графиков принимают поле 'name' - название графика (по-умолчанию False).

        :param olap_module_id: идентификатор OLAP-модуля, на основе которого будет строиться график;
            если параметр не задан, то график будет строиться на основе текущего активного OLAP-модуля;
            если и текущий активный OLAP-модуль не задан, то будет сгенерирована ошибка.

        :param m_size: размеры создаваемого окна графики; актуально для любого типа графиков.
            Представляет собой словарь, содержащий следующие ключи:
                height (h) - высота окна; минимальное значение - 240, значение по-умолчанию - 540.
                width (w) - ширина окна; минимальное значение - 840, значение по-умолчанию - 840.
            Все остальные значения, переданные в словарь, будут проигнорированы.
            При указании значения размерности, меньше минимального, будет сгенерирована ошибка.

        :return: (str) идентификатор созданного окна графики.
        """
        try:
            graph_instance = IGraph(
                self,
                g_type,
                settings,
                grid,
                labels or dict(),
                other or dict(),
                olap_module_id or self.multisphere_module_id,
                m_size or dict(),
            )
            graph_module_id = graph_instance.create()
        except Exception as ex:
            return self._raise_exception(GraphError, str(ex))
        self._set_graph_module_id(graph_module_id)
        self.func_name = "graph_create"
        return graph_module_id

    @timing
    def graph_modify(
        self,
        g_type: Union[int, str] = 1,
        settings: str = "",
        grid: int = 3,
        labels: dict = None,
        other: dict = None,
        graph_id: str = "",
        m_size: dict = None,
    ) -> str:
        """
        Изменить уже существующий график по заданным параметрам.
        Описание параметров:

        :param g_type: тип графика; можно задавать как целочисленное значение, так и строковое.
            Возможные значения (указаны целочисленные и строковые варианты):
                [1, "lines"] - линии
                [2, "cylinders"] - цилиндры
                [3, "cumulative_cylinders"] - цилиндры с накоплением
                [4, "areas"] - области
                [5, "cumulative_areas"] - области с накоплением
                [6, "pies"] - пироги
                [7, "radar"] - радар
                [8, "circles"] - круги
                [9, "circles_series"] - серии кругов
                [10, "balls"] - шары
                [11, "pools"] - бассейны
                [12, "3d_pools"] - 3D-бассейны
                [13, "corridors"] - коридоры
                [14, "surface"] - поверхность
                [15, "graph"] - граф
                [16, "sankey"] - санкей
                [17, "chord"] - хордовая
                [18, "point"] - точечный
                [19, "point_series"] - серии точек.
            По-умолчанию (если не задан параметр) график будет изменён на тип [1, "lines"] - линии.
            Для версии Полиматики 5.7 и выше доступны все перечисленные типы графиков, кроме
                [9, "circles_series"], [19, "point_series"].
            Для типа графика [13, "corridors"] необходимо установить расчётный факт в вид "Процент" и
            установить по нему расчёт по горизонтали - это необходимые условия построения этого графика.

        :param settings: битмап-строка настроек графиков, значениями могут быть только 0 или 1.
            Каждый тип графика имеет свой битмап настроек:
                1. {Заголовок, Легенда, Названия осей, Подписи на осях, Вертикальная ось справа} - актуально для типов:
                    [1, "lines"], [2, "cylinders"], [3, "cumulative_cylinders"], [4, "areas"], [5, "cumulative_areas"],
                    [8, "circles"], [9, "circles_series"], [11, "pools"], [13, "corridors"],
                    [18, "point"], [19, "point_series"].
                    По-умолчанию имеет значение "11110".
                2. {Заголовок, Легенда, Показывать подписи} - актуально для типов: [6, "pies"].
                    По-умолчанию имеет значение "111".
                3. {Заголовок, Легенда, Названия осей, Отображать метки на осях} - актуально для типов: [7, "radar"].
                    По-умолчанию имеет значение "1111".
                4. {Заголовок, Легенда, Названия осей, Подписи на осях} - актуально для типов:
                    [10, "balls"], [12, "3d_pools"].
                    По-умолчанию имеет значение "1111".
                5. {Заголовок, Названия осей, Подписи на осях} - актуально для типов: [14, "surface"].
                    По-умолчанию имеет значение "111".
                6. {Заголовок, Подсвечивать узлы} - актуально для типов: [15, "graph"].
                    По-умолчанию имеет значение "11".
                7. {Заголовок} - актуально для типов: [16, "sankey"].
                    По-умолчанию имеет значение "1".
                8. {Заголовок, Легенда} - актуально для типов: [17, "chord"].
                    По-умолчанию имеет значение "11".

        :param grid: настройка сетки.
            Типы графиков, не имеющие данной настройки (если для перечисленных типов данный параметр будет задан,
            то он будет проигнорирован):
                [6, "pies"], [7, "radar"], [10, "balls"], [12, "3d_pools"],
                [14, "surface"], [15, "graph"], [16, "sankey"], [17, "chord"]
            Все остальные типы графиков имеют одно из следующих значений:
                0 - Все линии, 1 - Горизонтальные линии, 2 - Вертикальные линии, 3 - Без сетки.
            Значение по-умолчанию (если не задан параметр) - 3.

        :param labels: настройка подписей на графиках.
            Типы графиков, не имеющие данной настройки (если для перечисленных типов данный параметр будет задан,
            то он будет проигнорирован):
                [6, "pies"], [7, "radar"], [14, "surface"], [15, "graph"], [16, "sankey"], [17, "chord"]
            Для типов графиков [1, "lines"], [2, "cylinders"], [3, "cumulative_cylinders"], [4, "areas"],
                [5, "cumulative_areas"], [13, "corridors"] это словарь вида:
                {'OX': <value>, 'OY': <value>, 'short_format': <value>}, где
                    OX - частота подписей по оси OX (от 5 до 30 с шагом 5); по-умолчанию 10
                    OY - частота подписей по оси OY (от 5 до 30 с шагом 5); по-умолчанию 10
                    short_format - нужно ли сокращать подпись (True/False); по-умолчанию False (только для версии 5.6)
                    division_value - цена деления;
                        возможны варианты: "no", "hundreds", "thousands", "millions", "billions", "trillions";
                        по-умолчанию "no";
            Для типов графиков [8, "circles"], [9, "circles_series"], [11, "pools"], [18, "point"],
                [19, "point_series"] это словарь вида: {'OX': <value>, 'OY': <value>}, где
                    OX - частота подписей по оси OX (от 5 до 30 с шагом 5); по-умолчанию 10
                    OY - частота подписей по оси OY (от 5 до 30 с шагом 5); по-умолчанию 10
                    division_value - цена деления;
                        возможны варианты: "no", "hundreds", "thousands", "millions", "billions", "trillions";
                        по-умолчанию "no";
            Для типов графиков [10, "balls"], [12, "3d_pools"] это словарь вида:
                {'OX': <value>, 'OY': <value>, 'OZ': <value>}, где
                    OX - частота подписей по оси OX (от 1 до 10 с шагом 0.5); по-умолчанию 2.5
                    OY - частота подписей по оси OY (от 1 до 10 с шагом 0.5); по-умолчанию 2.5
                    OZ - частота подписей по оси OZ (от 1 до 10 с шагом 0.5); по-умолчанию 2.5

        :param other: дополнительные настройки графиков.
            Типы графиков, не имеющие данной настройки (если для перечисленных типов данный параметр будет задан,
            то он будет проигнорирован):
                [4, "areas"], [7, "radar"], [16, "sankey"]
            Для типов графиков [1, "lines"], [13, "corridors"] это словарь вида:
                {'hints': <value>, 'show_points': <value>}, где
                    hints - нужно ли отображать подсказки к точкам (True/False); по-умолчанию False
                    show_points - нужно ли показывать точки (True/False); по-умолчанию True
            Для типа графика [2, "cylinders"] это словарь вида:
                {'hints': <value>, 'round': <value>, 'ident': <value>, 'ident_value': <value>}, где
                    hints - нужно ли отображать подсказки к цилиндрам (True/False); по-умолчанию False
                    round - нужно ли округлять подсказки до целых чисел; по-умолчанию False;
                        актуально только если значение параметра "hints" равно True
                    ident - отображать цилиндры с отступом (True/False); по-умолчанию True
                    ident_value - значение отступа (от 0 до 1 с шагом 0.05); по-умолчанию 0.9
            Для типа графика [3, "cumulative_cylinders"] это словарь вида:
                {'hints': <value>, 'round': <value>, 'graph_type': <value>}, где:
                    hints - нужно ли отображать подсказки к цилиндрам (True/False); по-умолчанию False
                    round - нужно ли округлять подсказки до целых чисел; по-умолчанию False;
                        актуально только если значение параметра "hints" равно True
                    graph_type - вид графика, значения: 'values'-значения, 'percents'-проценты; по-умолчанию 'values'
            Для типа графика [5, "cumulative_areas"] это словарь вида:
                {'graph_type': <value>}, где:
                    graph_type - вид графика, значения: 'values'-значения, 'percents'-проценты; по-умолчанию 'values'
            Для типа графика [6, "pies"] это словарь вида:
                {
                    'show_sector_values': <value>,
                    'min_sector': <value>,
                    'restrict_signature': <value>,
                    'size_of_signatures': <value>
                }, где:
                    show_sector_values - показывать значения на секторах; по-умолчанию False
                    min_sector - минимальный сектор (от 0 до 100 с шагом 1); по-умолчанию 0
                    restrict_signature - ограничить число подписей (от 0 до 100 с шагом 1); по-умолчанию 10
                    size_of_signatures - размер подписей (от 7 до 15 с шагом 1); по-умолчанию 12
            Для типа графика [8, "circles"] это словарь вида:
                {'diameter_range': <value>, 'diameter': <value>, 'show_trend_line': <value>}, где:
                    diameter_range - диапазон диаметров, записывается в виде кортежа (min, max), где min - нижняя
                        граница, а max - верхняя; обе границы должны быть в диапазоне от 1 до 50 с шагом 1;
                        верхняя граница не может быть меньше нижней; по-умолчанию (3, 15)
                    diameter - диаметр кругов (от 1 до 50 с шагом 1); по-умолчанию 10
                    show_trend_line - показать линию тренда (True/False); по-умолчанию False
            Для типов графиков [9, "circles_series"], [11, "pools"] это словарь вида:
                {'diameter_range': <value>, 'diameter': <value>}, где:
                    diameter_range - диапазон диаметров, записывается в виде кортежа (min, max), где min - нижняя
                        граница, а max - верхняя; обе границы должны быть в диапазоне от 1 до 50 с шагом 1;
                        верхняя граница не может быть меньше нижней; по-умолчанию (3, 15)
                    diameter - диаметр кругов (от 1 до 50 с шагом 1); по-умолчанию 10
            Для типа графика [10, "balls"] это словарь вида:
                {'show_shadows': <value>, 'diameter_range': <value>, 'diameter': <value>, 'colors': <value>}, где:
                    show_shadows - нужно ли отображать тени; по-умолчанию True
                    diameter_range - диапазон диаметров, записывается в виде кортежа (min, max), где min - нижняя
                        граница, а max - верхняя; обе границы должны быть в диапазоне от 4 до 48 с шагом 1;
                        верхняя граница не может быть меньше нижней; по-умолчанию (4, 48)
                    diameter - диаметр кругов (от 4 до 48 с шагом 1); по-умолчанию 4
                    colors - градиент шаров; ожидается список из 3х цветов в формате "#RRGGBB";
                        по-умолчанию ["#ffff00", "#3c9bea"];
            Для типа графика [12, "3d_pools"] это словарь вида:
                {'diameter_range': <value>, 'diameter': <value>}, где:
                    diameter_range - диапазон диаметров, записывается в виде кортежа (min, max), где min - нижняя
                        граница, а max - верхняя; обе границы должны быть в диапазоне от 4 до 48 с шагом 1;
                        верхняя граница не может быть меньше нижней; по-умолчанию (4, 48)
                    diameter - диаметр кругов (от 4 до 48 с шагом 1); по-умолчанию 4
            Для типа графика [14, "surface"] это словарь вида:
                {'show_carcass': <value>, 'opacity': <value>, 'colors': <value>}, где:
                    show_carcass - показать каркас; по-умолчанию False
                    opacity - прозрачность (от 0 до 100 с шагом 1); по-умолчанию 100
                    colors - цвета поверхности; ожидается список из 3х цветов в формате "#RRGGBB";
                        по-умолчанию ["#eaf7fb", "#3c9bea", "#08034f"]
            Для типа графика [15, "graph"] это словарь вида:
                {
                    'node_settings': <value>,
                    'edge_settings': <value>,
                    'neighboring_nodes_count': <value>,
                    'min_thickness_on_hover': <value>,
                    'opacity_of_unselected': <value>
                }, где:
                    node_settings - настройки узлов; представляет собой словарь вида:
                        {'colors': <value>, 'min_size': <value>, 'max_size': <value>}, где:
                            colors - переход цвета узлов, имеет вид: {'first': <value>, 'second': <value>};
                                ожидаются цвета в формате "#RRGGBB";
                                значения по-умолчанию: {'first': '#1f77b4', 'second': '#17becf'};
                                в случае задания только одного цвета - второй цвет берётся из значений по-умолчанию;
                                в случае, если не задан ни один цвет - оба берутся из значений по-умолчанию
                            min_size - минимальный размер узла (от 1 до 10 с шагом 0.1); по-умолчанию 1
                            max_size - максимальный размер узла (от 5 до 15 с шагом 0.1);
                                должен быть больше, чем max_size; по-умолчанию 10
                    edge_settings - настройки рёбер; представляет собой словарь вида:
                        {'colors': <value>, 'min_thickness': <value>, 'max_thickness': <value>}, где:
                            colors - переход цвета рёбер, имеет вид: {'first': <value>, 'second': <value>};
                                ожидаются цвета в формате "#RRGGBB";
                                значения по-умолчанию: {'first': '#1f77b4', 'second': '#17becf'};
                                в случае задания только одного цвета - второй цвет берётся из значений по-умолчанию;
                                в случае, если не задан ни один цвет - оба берутся из значений по-умолчанию
                            min_thickness - минимальная толщина ребра (от 1 до 5 с шагом 0.1); по-умолчанию 1
                            max_thickness - максимальная толщина ребра (от 5 до 10 с шагом 0.1);
                                должен быть больше, чем min_thickness; по-умолчанию 5
                    neighboring_nodes_count - количество выделенных соседних узлов при наведении (от 0 до 5 с шагом 1);
                        по-умолчанию 3
                    min_thickness_on_hover - диапазон минимальной толщины при наведении;
                        записывается в виде списка/кортежа (min, max), где min - нижняя граница, а max - верхняя;
                        обе границы должны быть в диапазоне от 0.5 до 5 с шагом 0.1;
                        верхняя граница не может быть меньше нижней; по-умолчанию (1, 3)
                    opacity_of_unselected - прозрачность невыделенных узлов (от 0 до 1 с шагом 0.01); по-умолчанию 0.7
            Для типа графика [17, "chord"] это словарь вида:
                {'show_title': <value>}, где:
                    show_title - показывать подписи (True/False); по-умолчанию True
            Для типа графика [18, "point"] это словарь вида:
                {'diameter': <value>, 'diameter_range': <value>, 'show_trend_line': <value>}, где:
                    diameter - диаметр кругов (от 1 до 50 с шагом 1); по-умолчанию 10
                    diameter_range - диапазон диаметров, записывается в виде кортежа (min, max), где min - нижняя
                        граница, а max - верхняя; обе границы должны быть в диапазоне от 1 до 50 с шагом 1;
                        верхняя граница не может быть меньше нижней; по-умолчанию (3, 15);
                    show_trend_line - показать линию тренда (True/False); по-умолчанию True
            Для типа графика [19, "point_series"] это словарь вида:
                {'diameter': <value>, 'show_trend_line': <value>}, где:
                    diameter - диаметр кругов (от 1 до 20 с шагом 0.5); по-умолчанию 6.5
                    show_trend_line - показать линию тренда (True/False); по-умолчанию True
            Помимо этого, все типы графиков принимают поле 'name' - название графика (по-умолчанию False).

        :param graph_id: идентификатор изменяемого модуля графики;
            если параметр не задан, то будет изменён текущий активный график;
            если и текущий активный модуль графики не задан, то будет сгенерирована ошибка.

        :param m_size: размеры создаваемого окна графики; актуально для любого типа графиков.
            Представляет собой словарь, содержащий следующие ключи:
                height (h) - высота окна; минимальное значение - 240, значение по-умолчанию - 540.
                width (w) - ширина окна; минимальное значение - 840, значение по-умолчанию - 840.
            Все остальные значения, переданные в словарь, будут проигнорированы.
            При указании значения размерности, меньше минимального, будет сгенерирована ошибка.

        :return: (str) идентификатор изменённого окна графики.
        """
        try:
            graph_instance = IGraph(
                self,
                g_type,
                settings,
                grid,
                labels or dict(),
                other or dict(),
                graph_id or self.graph_module_id,
                m_size or dict(),
            )
            graph_module_id = graph_instance.update()
        except Exception as ex:
            return self._raise_exception(GraphError, str(ex))
        self._set_graph_module_id(graph_module_id)
        self.func_name = "graph_modify"
        return graph_module_id

    @timing
    def column_resize(
        self, module: str = "", width: int = 200, olap_resize: bool = False
    ) -> dict:
        """
        Изменение ширины колонок фактов (чтобы текст на них становился видимым).
        Некая имитация интерфейсной кнопки "Показать контент". Актуально только для OLAP-модулей (мультисфер).
        Если пользователем не указан идентификатор модуля, то расширяется текущий активный OLAP-модуль.
        :param module: название/идентификатор OLAP-модуля;
            если модуль указан, но такого нет - сгенерируется исключение;
            если модуль не указан, то берётся текущий (активный) модуль (если его нет - сгенерируется исключение).
        :param width: ширина, на которую будет меняться каждая колонка фактов; можно указать отрицательное значение,
            тогда ширина колонок будет уменьшаться; при указании положительного значения - ширина колонок увеличится.
        :param olap_resize: нужно ли изменять ширину окна мультисферы
            (True - нужно, False - не нужно). По-умолчанию False.
        :return: результат команды ("user_iface", "save_settings").
        :call_example:
            1. Инициализируем класс: bl_test = sc.BusinessLogic(login="login", password="password", url="url")
            2. Вызов метода:
                module, width, olap_resize = "module_id_or_module_name", "width", "olap_resize"
                bl_test.column_resize(module=module, width=width, olap_resize=olap_resize)
            3. Вызов метода с передачей неверного идентификатора/названия модуля:
                module, width, olap_resize = "invalid_module_id_or_invalid_module_name", "width", "olap_resize"
                bl_test.column_resize(module=module, width=width, olap_resize=olap_resize)
                output: exception "Module {} not found".
        """
        # проверка значений
        if not isinstance(olap_resize, bool):
            return self._raise_exception(
                ValueError,
                'Wrong param "olap_resize"! It can only be "True" or "False"!',
                with_traceback=False,
            )

        # получаем идентификатор OLAP-модуля
        module_id = self._get_olap_module_id(module)

        # вычисляем новую ширину каждой ячейки фактов
        measure_widths, olap_width = self._get_current_widths(module_id)
        new_measure_widths = list(map(lambda x: max(x + width, MIN_MEASURE_CELL_WIDTH), measure_widths))

        # вычисляем новую ширину OLAP-модуля
        olap_width += 0 if olap_resize is False else width * len(measure_widths)

        # в случае уменьшения ячеек ограничиваем ширину OLAP модуля минимально допустимой
        olap_width = max(olap_width, MIN_OLAP_WIDTH)
        current_settings = self.execute_manager_command(
            command_name="user_iface", state="load_settings", module_id=module_id
        )
        title = self.h.parse_result(result=current_settings, key="settings", nested_key="title")

        # сохраняем новые настройки, где текущую ширину колонок увеличиваем на значение, заданное пользователем
        settings = {
            "title": title,
            "dimAndFactShow": True,
            "itemWidth": new_measure_widths,
            "geometry": {"width": olap_width},
        }
        return self.execute_manager_command(
            command_name="user_iface",
            state="save_settings",
            module_id=module_id,
            settings=settings,
        )

    def _get_current_widths(self, module_id) -> Union[List, int]:
        """
        Получает текущие настройки интерфейса и возвращает ширину фактов в заданной мультисфере, а также ширину
        самого окна мультисферы. Если интерфейсные настройки не заданы, возвращаются значения по-умолчанию.
        :param module_id: идентификатор OLAP-модуля; гарантируется, что такой модуль точно существует.
        :return: (list) список, содержащий значение ширины каждого факта.
        :return: (int) значение ширины окна мультисферы.
        """
        # считаем количество фактов мультисферы
        multisphere_data = self.get_multisphere_data()
        measure_count = len(multisphere_data.get("facts", []))
        # получаем настройки
        settings = self.execute_manager_command(
            command_name="user_iface", state="load_settings", module_id=module_id
        )
        current_settings = self.h.parse_result(result=settings, key="settings")
        measure_widths = current_settings.get("itemWidth", [MIN_MEASURE_CELL_WIDTH] * measure_count)
        olap_width = current_settings.get("geometry", {}).get("width", MIN_OLAP_WIDTH)
        return measure_widths, olap_width

    @timing
    def get_cubes_list(self) -> json_type:
        """
        Возвращает список кубов.
        :return: (json) информация по каждому кубу в формате JSON.
        """
        result = self.execute_manager_command(
            command_name="user_cube", state="list_request"
        )
        return self.h.parse_result(result=result, key="cubes")

    @timing
    def get_cube_permissions(self) -> List:
        """
        Возвращает доступность кубов для текущего пользователя.
        :return: (List) список кубок в следующем формате:
            [{'cube_id': "cube_id", 'cube_name': "cube_name", 'accessible': "accessible"}, ...], где
            cube_id и cube_name - идентификатор и имя куда соответственно,
            accessible - доступность куба для текущего пользователя (True - куб доступен, False - не доступен)
        :call_example:
            1. Инициализируем класс: bl_test = sc.BusinessLogic(login="login", password="password", url="url")
            2. Вызов метода: permission_data = bl_test.get_cube_permissions()
        """
        try:
            # ---------------------- пересмотреть закомменченное решение в рамках Polymatica 5.7 ----------------------
            # # получаем uuid текущего пользователя
            # users_result = self.execute_manager_command(command_name="user", state="list_request")
            # users_data = self.h.parse_result(result=users_result, key="users")
            # for user in users_data:
            #     if user.get('login') == self.login:
            #         requested_uuid = user.get('uuid')
            #         break

            # # для найденного пользователя получаем информацию о доступности кубов
            # cube_permission_result = self.execute_manager_command(
            #     command_name="user_cube", state="user_permissions_request", user_id=requested_uuid)
            # cube_permission_data = self.h.parse_result(result=cube_permission_result, key="permissions")
            # ---------------------------------------------------------------------------------------------------------

            cubes_list = self.get_cubes_list() or list()
            cube_permission_data = list()
            for cube in cubes_list:
                cube_permission_data.append(
                    {
                        "cube_id": cube.get("uuid"),
                        "cube_name": cube.get("name"),
                        "accessible": True,
                    }
                )
        except Exception as ex:
            return self._raise_exception(PolymaticaException, str(ex))
        self.func_name = "get_cube_permissions"
        return cube_permission_data

    @timing
    def get_last_update_date(self, script_uuid: str) -> str:
        """
        Возвращает дату последнего обновления мультисферы, входящей в заданный сценарий. Если мультисфер
        несколько, вернётся наибольшая из дат обновления.
        В методе учитывается тот факт, что текущий пользователь может не иметь прав на мультисферы, входящие в сценарий.
        Есть несколько случаев:
            1. Пользователь не имеет прав на ВСЕ мультисферы, входящие в сценарий. В таком случае сгенерируется
               ошибка ScenarioError.
            2. Пользователь не имеет прав на НЕКОТОРЫЕ мультисферы, входящие в сценарий. В таком случае в логи запишется
               соответствующее сообщение, но метод продолжит работу - вернётся наибольшая из дат обновления мультисфер,
               доступных пользователю.
        :param script_uuid: (str) uuid сценария.
        :return: (str) дата обновления в строковом формате (ISO).
        :call_example:
            1. Инициализируем класс: bl_test = sc.BusinessLogic(login="login", password="password", url="url")
            2. Вызов метода с передачей валидного script_uuid:
                script_uuid = "script_uuid"
                bl_test.get_last_update_date(script_uuid)
            3. Вызов метода с передачей невалидного script_uuid:
                script_uuid = "invalid_script_uuid"
                bl_test.get_last_update_date(script_uuid)
                output: exception "Ошибка получения мультисфер, входящих в сценарий.
                    Возможно, сценарий с идентификатором "{}" не существует".
        """
        # получаем список всех сценариев и проверяем, есть ли средни них сценарий с заданным идентификатором
        script_list = self.get_scripts_description_list() or list()
        for script in script_list:
            if script.get("id") == script_uuid:
                break
        else:
            msg = f'Scenario with id "{script_uuid}" not found!'
            self._raise_exception(ScenarioError, msg, with_traceback=False)

        # получаем идентификаторы кубов в заданном сценарии; могут встречаться ситуации,
        # когда в сценарии нет ни одного куба, поэтому, если список идентификаторов кубов пуст - генерируем ошибку
        script_cube_ids = self.get_scenario_cube_ids(scenario_id=script_uuid) or []
        if not script_cube_ids:
            msg = f'There are no multispheres in the "{script_uuid}" scenario'
            self._raise_exception(ScenarioError, msg, with_traceback=False)

        # получаем список мультисфер и для мультисфер, входящих в заданный сценарий, извлекаем дату обновления
        cubes_info = self.get_cubes_list()
        update_times = [
            cube.get("update_time")
            for cube in cubes_info
            if cube.get("uuid") in script_cube_ids
        ]

        # список дат обновлений может быть пуст (не полон), если не найдены мультисферы, входящие в сценарий;
        # это в свою очередь может быть из-за того, что у текущего пользователя нет прав на эти мультисферы.
        # 1. Если список дат обновлений пуст, т.е. у текущего пользователя нет прав ни на одну мультисферу
        #    из списка мультисфер заданного сценария - генерируем ошибку.
        # 2. Если же список дат обновлений не полон, т.е. у текущего пользователя нет прав только на некоторые
        #    мультисферы из списка мультисфер заданного сценария - кидаем предупреждение в логи.
        base_msg = "The current user does not have rights"
        if not update_times:
            msg = f"{base_msg} to any multisphere included in the specified scenario!"
            self._raise_exception(ScenarioError, msg, with_traceback=False)
        if len(script_cube_ids) != len(update_times):
            self.logger.warning(
                f"{base_msg} to some of the multispheres included in the specified scenario!"
            )

        self.func_name = "get_last_update_date"

        # берём максимальную дату (т.к. она в мс, то делим на миллион) и приводим к формату ISO
        max_update_time = int((max(update_times)) / 10**6)
        return datetime.datetime.fromtimestamp(max_update_time).strftime(
            ISO_DATE_FORMAT
        )

    def _find_olap_module(self, olap_data: str) -> List:
        """
        Поиск OLAP-модуля с заданным именем/идентификатором. Если искомый модуль не найден, вернётся ('', '').
        :param olap_data: (str) идентификатор или имя OLAP-модуля.
        :return: (List) список кортежей [(str) идентификатор слоя, на котором находится искомый модуль, и
        (str) идентификатор найденного модуля (uuid)]
        """
        return self._find_module(olap_data, MULTISPHERE_ID)

    def _find_graph_module(self, graph_data: str) -> List:
        """
        Поиск модуля графиков с заданным именем/идентификатором. Если искомый модуль не найден, вернётся ('', '').
        :param graph_data: (str) идентификатор или имя модуля графиков.
        :return: (List) список кортежей [(str) идентификатор слоя, на котором находится искомый модуль, и
        (str) идентификатор найденного модуля (uuid)]
        """
        return self._find_module(graph_data, GRAPH_ID)

    def _find_module(self, module_data: str, module_type: int = None) -> List:
        """
        Поиск произвольного модуля с заданным именем/идентификатором.
        Если такой модуль не найден, вернётся пустой список.
        :param module_data: (str) идентификатор или имя модуля.
        :param module_type: (int) тип модуля, среди которого нужно искать искомый модуль (например, 500 - OLAP и тд).
        :return: (List) список кортежей [(str) идентификатор слоя, на котором находится искомый модуль, и
        (str) идентификатор найденного модуля (uuid)]
        """
        result = []
        # проверка на пустоту
        if module_data:
            # получаем список слоёв
            layer_list = self.get_layer_list()
            if layer_list:
                # проходя по каждому слою, получаем список его модулей и ищем сопоставления
                for layer in layer_list:
                    # param layer is ['layer_id', 'layer_name']
                    layer_id = layer[0]
                    module_list = self._get_modules_in_layer(layer_id)
                    for module in module_list:
                        # param module is ['module_uuid', 'module_name', 'module_int_type']
                        module_uuid, module_name, module_type_int, _ = module
                        if (
                            module_type is None or module_type_int == module_type
                        ) and module_data in [module_uuid, module_name]:
                            result.append((layer_id, module_uuid))
        return result

    @timing
    def get_measure_format_by_scenario_id(
        self, scenario_id: str = None, scenario_name: str = None
    ) -> dict:
        """
        Получить форматы всех вынесенных (видимых) фактов мультисферы, использующихся в заданном сценарии.
        Сценарий задаётся либо его идентификатором, либо его названием (и то, и то указывать не обязательно).
        Подразумевается, что в сценарии участвует только одна мультисфера (иначе будет сгенерирована ошибка).
        ВАЖНО:
            1. Для получения настроек форматирования фактов необходим запуск указанного сценария.
            2. Если в мультисфере есть вынесенные вверх размерности, то информация по форматированию фактов
            не дублируется (т.е. в результате присутствуют только уникальные факты).
        :param scenario_id: (str) идентификатор сценария.
        :param scenario_name: (str) название сценария.
        :return: (dict) описание форматирования фактов в виде:
            {
                'measure_id_1': {
                    'color': <value>,      # цвет факта; возможно любое RGB-значение; по-умолчанию #000000 (чёрный цвет)
                    'delim': <value>,      # разделитель; возможны варианты: [".", " ", ","]; по-умолчанию точка (".")
                    'precision': <value>,  # точность; возможно любое строковое значение от 0 до 9; по-умолчанию '2'
                    'prefix': <value>,     # префикс; возможно любое значение; по-умолчанию пустая строка
                    'suffix': <value>,     # суффикс; возможно любое значение; по-умолчанию пустая строка
                    'split': <value>       # разделение на разряды; возможны варианты: True, False; по-умолчанию True
                },
                'measure_id_2': {...},
                ...
            }
        """
        # сохраняем данные по слою/мультисфере до запуска скрипта
        active_layer_id, active_module_id = (
            self.get_active_layer_id(),
            self.multisphere_module_id,
        )

        # проверка, что задана хоть какая-то информация о сценарии
        if scenario_id is None and scenario_name is None:
            return self._raise_exception(
                ScenarioError,
                "You must specify either a scenario id or a scenario name!",
                with_traceback=True,
            )

        # запускаем сценарий
        self.run_scenario(scenario_id=scenario_id, scenario_name=scenario_name)

        # получаем список модулей на активном слое, среди которых ищем OLAP-модуль
        new_active_layer_id = self.get_active_layer_id()
        modules = self._get_modules_in_layer(new_active_layer_id)
        current_module_id = ""
        for module in modules:
            if module[2] == MULTISPHERE_ID:
                if not current_module_id:
                    current_module_id = module[0]
                else:
                    # если в сценарии обнаружено несколько мультисфер, то закрываем созданный слой и генерируем ошибку
                    error_msg = "Multiple multispheres found in scenario! No further work possible!"
                    self.close_layer(new_active_layer_id)
                    self.active_layer_id = active_layer_id
                    self.set_multisphere_module_id(active_module_id)
                    return self._raise_exception(
                        PolymaticaException, error_msg, with_traceback=True
                    )
        self.set_multisphere_module_id(current_module_id)

        # получаем текущие настройки
        settings = self.execute_manager_command(
            command_name="user_iface",
            state="load_settings",
            module_id=current_module_id,
        )
        current_settings = self.h.parse_result(settings, "settings")
        format_settings = (
            current_settings.get("config_storage", {})
            .get("facts-format", {})
            .get("__suffixes", {})
        )

        # получаем все вынесенные в рабочую область факты мультисферы
        all_measures = self._get_measures_list()
        visible_measure_ids = [
            measure.get("id") for measure in all_measures if measure.get("visible")
        ]

        # составляем итоговую выборку
        result = {}
        default_field_values = {
            "color": "#000000",
            "delim": ".",
            "precision": "2",
            "prefix": "",
            "suffix": "",
            "split": True,
        }
        for measure_id in visible_measure_ids:
            measure_format_settings = format_settings.get(measure_id, {})
            current_settings = {}
            for field in default_field_values:
                current_settings.update(
                    {
                        field: measure_format_settings.get(
                            field, default_field_values.get(field)
                        )
                    }
                )
            result.update({measure_id: current_settings})

        # удаляем созданный слой, возвращает изначальные значения переменных и возвращаем результат
        self.close_layer(new_active_layer_id)
        self.active_layer_id = active_layer_id
        self.set_multisphere_module_id(active_module_id)
        self.func_name = "get_measure_format_by_scenario_id"
        return result

    @timing
    def close_module(self, module_id: str) -> dict:
        """
        Закрытие конкретного модуля по его идентификатору. Подходит для любых типов модулей (OLAP, графики, карты и тд).
        :param module_id: (str) идентификатор модуля; ожидается строка (в противном случае будет сгенерирована ошибка).
        :return: (dict) результат команды ("user_iface", "close_module").
        """
        # проверка типа параметра
        if not isinstance(module_id, str):
            return self._raise_exception(
                ValueError, 'Param "module_id" must be str type!'
            )

        # пытаемся закрыть модуль с заданным идентификатором
        try:
            result = self.execute_manager_command(
                command_name="user_iface", state="close_module", module_id=module_id
            )
        except Exception:
            error_msg = (
                f'Failed to close module with ID "{module_id}". '
                "Possible that a module with this ID does not exist."
            )
            return self._raise_exception(PolymaticaException, error_msg)
        return result

    @timing
    def close_modules(
        self, module_ids: Union[list, set, tuple], is_skip: bool = True
    ) -> bool:
        """
        Закрыть модули по их идентификаторам. Подходит для любых типов модулей (OLAP, графики, карты и тд).
        :param module_ids: Union[list, set, tuple] идентификаторы закрываемых модулей;
            можно передавать список, множество или кортеж (в противном случае будет сгенерирована ошибка).
        :param is_skip: (bool) нужно ли пропускать модули, закрыть которые не удалось.
            Если значение установлено в True (является значением по-умолчанию), то в случае
            неудачной попытки закрытия модуля ошибки не будет, все последующие модули будут закрыты.
            В противном случае будет сгенерирована ошибка, и все последующие модули не будут закрыты.
        :return: (bool) True, если все модули были закрыты.
        """
        # проверка типа параметра
        if not isinstance(module_ids, (list, set, tuple)):
            error_msg = (
                'Param "module_ids" must be of one of the types [list, set, tuple]!'
            )
            return self._raise_exception(ValueError, error_msg)

        # пытаемся закрыть каждый модуль
        for module_id in module_ids:
            try:
                self.close_module(module_id)
            except Exception as ex:
                if is_skip:
                    self.logger.warning(ex.user_msg)
                    continue
                raise
        self.func_name = "close_modules"
        return True

    @timing
    def set_measure_direction(self, measure_name: str, is_horizontal: bool) -> dict:
        """
        Установка расчёта по горизонтали для заданного факта. Для этого требуется выполнение нескольких условий:
            1. Необходимо наличие верхней и левой размерности (хотя бы по одной);
            2. Вид факта должен быть отличен от вида "Значение".
        При несоблюдении хотя бы одного из вышеперечисленных условий будет сгенерирована ошибка.
        :param measure_name: (str) название факта; если указанного факта нет в мультисфере, будет сгенерирована ошибка.
        :param is_horizontal: (bool) True, если требуется установить расчёт по горизонтали для заданного факта,
            False в противном случае.
        :return: (dict) результат команды ("fact", "set_direction").
        """
        # проверки
        try:
            self.checks(self.func_name, is_horizontal)
        except Exception as e:
            return self._raise_exception(ValueError, str(e), with_traceback=False)

        initial_error_msg = "Impossible to set horizontal calculation!"

        # проверяем количество левых и верхних размерностей
        left_dims_count, top_dims_count = self._get_left_and_top_dims_count()
        if left_dims_count == 0 or top_dims_count == 0:
            error_msg = f"{initial_error_msg} At least one left and top dimensions must be taken out!"
            return self._raise_exception(PolymaticaException, error_msg)

        # получаем идентификатор факта по его имени, параллельно проверяя его вид
        measures_data = self.execute_olap_command(command_name="fact", state="list_rq")
        measures = self.h.parse_result(measures_data, "facts")
        measure_id = ""
        for measure in measures:
            if measure.get("name").strip() == measure_name:
                # 0 означает, что установлен вид факта "Значение"
                if measure.get("plm_type") == 0:
                    error_msg = f'{initial_error_msg} Measure type must be different from "Value"!'
                    return self._raise_exception(PolymaticaException, error_msg)
                # если текущий факт уже установлен в нужный расчёт, то также сгененируем ошибку
                if measure.get("horizontal") == is_horizontal:
                    error_msg = f'{initial_error_msg} Measure "{measure_name}" already set in necessary calculation!'
                    return self._raise_exception(PolymaticaException, error_msg)
                # получаем идентификатор факта и покидаем цикл
                measure_id = measure.get("id")
                break

        # если факт не найден - также сгенерирем ошибку
        if not measure_id:
            error_msg = f'Measure name "{measure_name}" is not valid for Multisphere "{self.cube_name}"!'
            return self._raise_exception(PolymaticaException, error_msg)

        # исполняем команду
        return self.execute_olap_command(
            command_name="fact",
            state="set_direction",
            fact=measure_id,
            is_horizontal=is_horizontal,
        )

    @timing
    def get_scenario_metadata(self, script_id: str) -> List:
        """
        Получение метаданных сценария с заданным идентификатором без запуска этого самого сценария.
        Метаданные - информация о каждой мультисфере, входящей в заданный сценарий: идентификатор, название,
            идентификатор OLAP-модуля, заголовок OLAP-модуля, список вынесенных (видимых) размерностей и фактов.
        Актуально только для версии Polymatica 5.7 и выше.
        :param script_id: (str) идентификатор сценария; если такого сценария не существует - будет сгенерирована ошибка.
        :return: (dict) метаданные заданного сценария в формате:
            [
                {
                    "cube_id": "",
                    "cube_name": "",
                    "module_id": "",
                    "module_name": "",
                    "used_dimensions": [
                        {
                            "id": "",
                            "level": 0,
                            "name": "",
                            "position": 0,
                            "type": 0
                        },
                        ...
                    ],
                    "used_measures":[
                        {
                            "id": "",
                            "measure_type": 0,
                            "name": "",
                            "position": 0,
                            "type": 0
                        },
                        ...
                    ]
                },
                ...
            ]
            В случае, если мультисфер в сценарии нет, вернётся пустой список.
            В случае, если в мультисфере нет вынесенных размерностей, то в "used_dimensions"
                будет пустой список.
        """
        # проверки
        try:
            self.checks(self.func_name, script_id)
        except Exception as e:
            return self._raise_exception(ValueError, str(e), with_traceback=False)

        # получаем список сценариев и находим необходимый нам
        scripts_list = self.get_scripts_list()
        self.func_name = "get_scenario_metadata"
        for script in scripts_list:
            if script.get("id") == script_id:
                break
        else:
            return self._raise_exception(
                ValueError, f'Scenario with id "{script_id}" not found!'
            )

        # получаем метаданные
        metadata_result = self.execute_manager_command(
            command_name="scripts", state="get_script_metadata", script_id=script_id
        )
        return self.h.parse_result(metadata_result, "modules")

    def _get_cube_update_type(self, cube_id: str) -> str:
        """
        Получить тип обновления мультисферы с заданным идентификатором.
        :param cube_id: (str) идентификатор куба.
        :return: (str) тип обновления; возможен один из вариантов:
            ["полное", "интервальное", "инкрементальное", "обновление измененных записей", "undefined"];
            первые четыре типа актуальны для БД-источников, последний тип - для файловых источников.
        """
        empty_id = "00000000"
        metadata_result = self.execute_manager_command(
            command_name="user_cube",
            state="ext_info_several_sources_request",
            cube_id=cube_id,
        )

        # для файловых источников тип обновления отсутствует - вернём "undefined"
        for datasource in self.h.parse_result(
            metadata_result, "datasources", default_value=list()
        ):
            if datasource.get("server_type") in DB_SOURCE_TYPES:
                break
        else:
            return "undefined"

        # далее подразумеваются SQL-источники, имеющие типы обновлений
        if (
            self.h.parse_result(
                metadata_result, "increment_field", default_value=empty_id
            )
            != empty_id
        ):
            return "инкрементальное"
        interval = self.h.parse_result(
            metadata_result, "interval", default_value=dict()
        )
        if interval and interval.get("dimension_id", empty_id) != empty_id:
            return "интервальное"
        if (
            self.h.parse_result(
                metadata_result, "delta", default_value=dict()
            ).get("primary_key_dim", empty_id)
            != empty_id
        ):
            return "обновление измененных записей"
        return "полное"

    @timing
    def get_cube_info(self, cube: str = "") -> dict:
        """
        Получить информацию о заданном кубе. Если заданный куб не будет найден - будет сгенерировано исключение.
        :param cube: (str) название/идентификатор куба, ожидается непустая строка;
            в случае, если параметр не задан, будет выведена информация о текущем (активном) кубе;
            если текущий (активный) куб не задан, то будет сгенерировано исключение.
        :return: (dict) информация о текущем кубе по аналогии с информацией, отображаемой на интерфейсе;
            формат ответа:
            {
                'name': <value>,              # название куба
                'uuid': <value>,              # идентификатор куба
                'creator': <value>,           # создатель куба
                'update_time': <value>,       # дата-время обновления
                'last_use_time': <value>,     # дата-время последнего использования
                'creation_time': <value>,     # дата-время создания
                'size': <value>,              # размер
                'record_count': <value>,      # число записей
                'dimension_count': <value>,   # число размерностей
                'measure_count': <value>,     # число фактов
                'update_type': <value>        # тип обновления
            }
        """
        # проверки
        try:
            self.checks(self.func_name, cube)
        except Exception as e:
            return self._raise_exception(ValueError, str(e), with_traceback=False)

        # если не указан куб - берём текущий
        current_cube = cube or self.cube_id
        if not current_cube:
            return self._raise_exception(
                CubeError,
                'Param "cube" not set and no active cube!',
                with_traceback=False,
            )

        # получаем список кубов и ищем среди них нужный
        cubes = self.get_cubes_list()
        cube_info = dict()
        for cube in cubes:
            cube_name, cube_id = cube.get("name"), cube.get("uuid")
            if self.script_mode:
                result = self.execute_olap_command(command_name="view",
                                                   state="get",
                                                   from_row=0,
                                                   from_col=0,
                                                   num_row=1,
                                                   num_col=1)
                relevance_date = self.h.parse_result(result, "relevance_date", default_value="")
            else:
                relevance_date = ""

            if current_cube not in (cube_name, cube_id):
                continue
            cube_info.update(
                {
                    "name": cube_name,
                    "uuid": cube_id,
                    "creator": cube.get("creator"),
                    "update_time": self.h.get_datetime_from_timestamp(
                        cube.get("update_time")
                    ),
                    "last_use_time": self.h.get_datetime_from_timestamp(
                        cube.get("last_use_time")
                    ),
                    "creation_time": self.h.get_datetime_from_timestamp(
                        cube.get("creation_time")
                    ),
                    "size": self.h.get_pretty_size(cube.get("size")),
                    "record_count": cube.get("row_count"),
                    "dimension_count": cube.get("dimension_count"),
                    "measure_count": cube.get("fact_count"),
                    "update_type": self._get_cube_update_type(cube_id),
                    "relevance_date": relevance_date
                }
            )
            break
        else:
            return self._raise_exception(
                CubeError,
                f'Cube with ID/name "{current_cube}" not found!',
                with_traceback=False,
            )

        self.func_name = "get_cube_info"
        return cube_info

    @timing
    def get_cube_metadata(self, cube: str = "") -> List:
        """
        Получить метаданные заданного куба, не открывая его (т.е. без создания соответствующего OLAP-модуля).
        Под метаданными имеется ввиду информация о размерностях и фактах мультисферы.
        :param cube: (str) название/идентификатор куба, ожидается непустая строка;
            в случае, если параметр задан, но искомого куба нет, то будет сгенерировано исключение;
            в случае, если параметр не задан, будет выведены метаданные для текущего (активного) куба;
            если и текущий (активный) куб не задан, то будет сгенерировано исключение.
        :return: (List) метаданные куба:
            [
                {
                    'column_name': <value>,       # название размерности/факта
                    'id': <value>,                # идентификатор размерности/факта
                    'polymatica_type': <value>,   # тип данных, используемый в Полиматике
                                                    (для фактов - всегда пустая строка)
                    'general_type': <value>,      # общий тип данных (для фактов - всегда "float")
                    'column_type': <value>        # одно из двух значений: либо "dimension", либо "fact"
                }
            ]
        """
        # проверки
        try:
            self.checks("get_cube_info", cube)
        except Exception as e:
            return self._raise_exception(ValueError, str(e), with_traceback=False)
        if not cube and not self.cube_id:
            return self._raise_exception(
                CubeError,
                'Param "cube" not set and no active cube!',
                with_traceback=False,
            )

        # получаем идентификатор заданного куба (который может оказаться текущим активным кубом)
        if cube:
            cubes_list, cube_id = self.get_cubes_list(), ""
            for current_cube in cubes_list:
                if cube in (current_cube.get("name"), current_cube.get("uuid")):
                    cube_id = current_cube.get("uuid")
                    break
            if not cube_id:
                return self._raise_exception(
                    CubeError,
                    f'Cube with ID/name "{cube}" not found!',
                    with_traceback=False,
                )
        else:
            cube_id = self.cube_id

        metadata = list()

        # получаем метаданные мультисферы без открытия OLAP-модуля
        metadata_result = self.execute_manager_command(
            command_name="user_cube",
            state="ext_info_several_sources_request",
            cube_id=cube_id,
        )
        for dim in self.h.parse_result(metadata_result, "dims"):
            polymatica_type = POLYMATICA_INT_TYPES_MAP.get(dim.get("type"))
            metadata.append(
                {
                    "column_name": dim.get("name"),
                    "id": dim.get("id"),
                    "polymatica_type": polymatica_type,
                    "general_type": TYPES_MAP.get(polymatica_type),
                    "column_type": "dimension",
                }
            )
        for fact in self.h.parse_result(metadata_result, "facts"):
            metadata.append(
                {
                    "column_name": fact.get("name"),
                    "id": fact.get("id"),
                    "polymatica_type": "",
                    "general_type": "float",
                    "column_type": "fact",
                }
            )

        self.func_name = "get_cube_metadata"
        return metadata

    @timing
    def get_olap_module_info(self, module: str = "") -> dict:
        """
        Получить текущую конфигурацию заданного OLAP - модуля.
        :param module: (str) название/идентификатор OLAP-модуля, конфигурацию которого нужно получить;
            если модуль указан, но такого нет - сгенерируется исключение;
            если модуль не указан, то берётся текущий (активный) модуль (если его нет - сгенерируется исключение).
        :result: (dict) текущая конфигурация OLAP-модуля;
            формат ответа:
            {
                'dimensions': [...],   # список всех размерностей
                'measures': [...]      # список всех фактов, включая группы фактов
            },
            где оба списка содержат словарь следующего формата:
            {
                'name': <value>,           # название размерности/факта
                'id': <value>,             # идентификатор размерности/факта
                'is_copy': <value>,        # является ли размерность/факт копией
                'data_type': <value>,      # тип данных размерности; для факта - None
                'is_composite': <value>,   # является ли размерность составной; для факта - None
                'position': <value>,       # позиция размерности ("left"/"up"/"out"); для факта - None
                'have_filter': <value>,    # наложен ли фильтр на размерность; для факта - None,
                'visible': <value>,        # видимость факта; для размерности - None
                'horizontal': <value>,     # включён ли горизонтальный расчёт для факта; для размерности - None
                'is_calculated': <value>,  # является ли факт вычислимым; для размерности - None
                'is_group': <value>,       # является ли факт группировкой других фактов; для размерности - None
                'group_id': <value>,       # идентификатор группы, в которую ходит данный факт;
                                             если факт не входит ни в какую группу, то None;
                                             для размерности - None
                'type': <value>            # тип факта; для размерности - None
            }
            Группы фактов представляют собой словарь следующего формата:
            {
                 'id': <value>,            # идентификатор группы
                 'type': 'group',          # тип: группа
                 'name': <value>,          # имя группы
                 'visibility': 'visible',  # видимость группы
                 'nodes':                  # узлы (факты и группы), входящие в группу, в формате списка словарей
                            [
                                {
                                    'id': идентификатор узла,
                                    'type': тип, для факта - 'measure',
                                    'measure': идентификатор самого факта,
                                    group_id': идентификатор группы, в которую входит этот узел
                                },
                                {...}
                            ]
            }
        """
        # получаем идентификатор OLAP-модуля
        module_id = self._get_olap_module_id(module, set_active_layer=False)
        current_ms_id = self.multisphere_module_id
        self.set_multisphere_module_id(module_id)
        olap_config = {"dimensions": list(), "measures": list()}

        # получаем список размерностей и фактов
        dimensions, measures = self._get_dimensions_list(), self._get_measures_list()
        dim_base_dict = dict.fromkeys(
            ["visible", "horizontal", "is_calculated", "is_group", "group_id", "type"],
            None,
        )
        measure_base_dict = dict.fromkeys(
            ["data_type", "is_composite", "position", "have_filter"], None
        )

        # конфигурация размерностей
        for dimension in dimensions:
            current_dim_dict = {
                "name": dimension.get("name"),
                "id": dimension.get("id"),
                "is_copy": dimension.get("base_id") != "00000000",
                "data_type": TYPES_MAP.get(
                    POLYMATICA_INT_TYPES_MAP.get(dimension.get("olap_type"))
                ),
                "is_composite": dimension.get("olap3_type") == 3,
                "position": POSITION_MAP.get(dimension.get("position")),
                "have_filter": dimension.get("haveFilter"),
            }
            current_dim_dict.update(dim_base_dict)
            olap_config["dimensions"].append(current_dim_dict)

        # конфигурация фактов
        nodes_list = self._get_tree_fact_list()
        nodes_dict_with_group = self._rec_nodes_to_dict_measure_with_group_id(
            nodes_list
        )
        for measure in measures:
            current_measure_dict = {
                "name": measure.get("name"),
                "id": measure.get("id"),
                "is_copy": measure.get("base_id") != "00000000",
                "visible": measure.get("visible"),
                "horizontal": measure.get("horizontal"),
                "is_calculated": measure.get("olap3_type") == 3,
                "is_group": measure.get("olap3_type") == 4,
                "group_id": measure.get("fgroup_id"),  # deprecated
                "type": MEASURE_INT_STR_TYPES_MAP.get(measure.get("plm_type")),
            }
            node = nodes_dict_with_group[measure["id"]]
            current_measure_dict["group_id"] = node["group_id"]
            current_measure_dict.update(measure_base_dict)
            olap_config["measures"].append(current_measure_dict)

        # добавляем группы фактов в список фактов
        measures_groups = [node for node in nodes_list if node.get("type") == "group"]
        olap_config["measures"].extend(measures_groups)
        # меняем фокус на исходную мультисферу и возвращаем данные
        self.set_multisphere_module_id(current_ms_id)
        return olap_config

    def _rec_nodes_to_dict_measure_with_group_id(self, nodes_list, group_id=None):
        nodes = {}

        for node in nodes_list:
            if node["type"] == "measure":
                node["group_id"] = group_id
                nodes[node["measure"]] = node
            elif node["type"] == "group":
                tmp_nodes = self._rec_nodes_to_dict_measure_with_group_id(
                    node["nodes"], node["id"]
                )
                nodes.update(tmp_nodes)

        return nodes

    @timing
    def get_total_mode(self) -> bool:
        """
        Получить режим отображения тоталов в текущем OLAP-модуле.
        :return: (bool) True, если режим отображения тоталов включён, иначе False.
        """
        if not self.multisphere_module_id:
            return self._raise_exception(
                PolymaticaException,
                "Active OLAP-module not found!",
                with_traceback=False,
            )

        # Если 'inter_total_hidden_dimensions' в ответе сервера пустой, то
        # 'show_inter_total' = True (режим отображения тоталов)
        result = self.execute_olap_command(command_name="view", state="get")
        return not self.h.parse_result(result, "inter_total_hidden_dimensions")

    @timing
    def get_global_horizontal_total(self) -> bool:
        """
        Получить режим отображения общего итога по столбцам в текущем OLAP-модуле.
        Общий итог по столбцам по умолчанию включен, если влево не вынесено ни одной размерности.
        :return: (bool) True, если режим отображения общего итога по столбцам включён, иначе False.
        """
        if not self.multisphere_module_id:
            return self._raise_exception(
                PolymaticaException,
                "Active OLAP-module not found!",
                with_traceback=False,
            )

        result = self.execute_olap_command(command_name="view", state="get")
        return self.h.parse_result(result, "show_global_horz_total")

    @timing
    def get_global_vertical_total(self) -> bool:
        """
        Получить режим отображения общего итога по строкам в текущем OLAP-модуле.
        Общий итог по строкам по умолчанию включен, если вверх не вынесено ни одной размерности.
        :return: (bool) True, если режим отображения общего итога по строкам включён, иначе False.
        """
        if not self.multisphere_module_id:
            return self._raise_exception(
                PolymaticaException,
                "Active OLAP-module not found!",
                with_traceback=False,
            )

        result = self.execute_olap_command(command_name="view", state="get")
        return self.h.parse_result(result, "show_global_vert_total")

    @timing
    def change_total_mode(self) -> dict:
        """
        Изменение режима показа тоталов (промежуточных сумм, обозначающихся как "всего") в мультисфере.
        Если до вызова данного метода тоталов в таблице не было, то они отобразятся, и наоборот.
        Устаревший метод. Рекомендуется использовать отдельные методы для общих тоталов по столбцам и
        строкам: set_global_horizontal_total() и set_global_vertical_total().
        :return: (dict) command ("view", "change_show_inter_total_mode")
        """
        return self.execute_olap_command(
            command_name="view", state="change_show_inter_total_mode"
        )

    @timing
    def set_global_horizontal_total(self, show: bool) -> dict:
        """
        Изменить режим отображения общего итога по столбцам в текущем OLAP-модуле.
        :param show: (bool) Режим отображения, если True, то отобразить общий итог по столбцам,
            если False, то скрыть общий итог по столбцам.
        :return: (dict) command ("view", "set_show_horizontal_total_mode_rp"
        """
        if not self.multisphere_module_id:
            return self._raise_exception(
                PolymaticaException,
                "Active OLAP-module not found!",
                with_traceback=False,
            )

        result = self.execute_olap_command(
            command_name="view", state="set_show_horizontal_total_mode", show=show
        )
        return result

    @timing
    def set_global_vertical_total(self, show: bool) -> dict:
        """
        Изменить режим отображения общего итога по строкам в текущем OLAP-модуле.
        :param show: (bool) Режим отображения, если True, то отобразить общий итог по строкам,
            если False, то скрыть общий итог по строкам.
        :return: (dict) command ("view", "set_show_vertical_total_mode_rp"
        """
        if not self.multisphere_module_id:
            return self._raise_exception(
                PolymaticaException,
                "Active OLAP-module not found!",
                with_traceback=False,
            )

        result = self.execute_olap_command(
            command_name="view", state="set_show_vertical_total_mode", show=show
        )
        return result

    @timing
    def set_all_inter_horizontal_total(self, show: bool) -> dict:
        """
        Изменить режим отображения промежуточного итога по столбцам в текущем OLAP-модуле.
        :param show: (bool) Режим отображения, если True, то отобразить промежуточный итог по столбцам,
            если False, то скрыть промежуточный итог по столбцам.
        :return: (dict) command ("view", "set_show_all_inter_total_mode_rp"
        """
        if not self.multisphere_module_id:
            return self._raise_exception(
                PolymaticaException,
                "Active OLAP-module not found!",
                with_traceback=False,
            )

        left_dims, _ = self._get_left_and_top_dims_count()
        if left_dims < 2:
            return self._raise_exception(
                PolymaticaException,
                "There must be at least 2 left dimensions!",
                with_traceback=False,
            )

        result = self.execute_olap_command(
            command_name="view",
            state="set_show_all_inter_total_mode",
            show=show,
            position=1,
        )
        return result

    @timing
    def set_all_inter_vertical_total(self, show: bool) -> dict:
        """
        Изменить режим отображения промежуточного итога по строкам в текущем OLAP-модуле.
        :param show: (bool) Режим отображения, если True, то отобразить промежуточный итог по строкам,
            если False, то скрыть промежуточный итог по строкам.
        :return: (dict) command ("view", "set_show_all_inter_total_mode_rp"
        """
        if not self.multisphere_module_id:
            return self._raise_exception(
                PolymaticaException,
                "Active OLAP-module not found!",
                with_traceback=False,
            )

        _, top_dims = self._get_left_and_top_dims_count()
        if top_dims < 2:
            return self._raise_exception(
                PolymaticaException,
                "There must be at least 2 top dimensions!",
                with_traceback=False,
            )

        result = self.execute_olap_command(
            command_name="view",
            state="set_show_all_inter_total_mode",
            show=show,
            position=2,
        )
        return result

    @timing
    def set_inter_horizontal_total(self, dimension_name: str, show: bool) -> dict:
        """
        Изменить режим отображения промежуточного итога по вынесенной влево размерности в текущем OLAP-модуле.
        :param dimension_name: Имя размерности. Размерность не должна быть на самом правом уровне.
        :param show: (bool) Режим отображения, если True, то отобразить промежуточный итог по указанной размерности,
            если False, то скрыть промежуточный итог по ней.
        :return: (dict) command ("view", "set_show_inter_total_mode_rp"
        """
        if not self.multisphere_module_id:
            return self._raise_exception(
                PolymaticaException,
                "Active OLAP-module not found!",
                with_traceback=False,
            )

        left_dims, _ = self._get_left_and_top_dims_count()
        if left_dims < 2:
            return self._raise_exception(
                PolymaticaException,
                "There must be at least 2 left dimensions!",
                with_traceback=False,
            )

        dim_id = self.get_dim_id(dimension_name)
        dims_data_result = self.execute_olap_command(
            command_name="view",
            state="get",
            from_row=0,
            from_col=0,
            num_row=1,
            num_col=1,
        )
        left_dims = self.h.parse_result(dims_data_result, "left_dims")
        if left_dims[-1] == dim_id:
            return self._raise_exception(
                PolymaticaException,
                "The dimension should not be at the rightmost level!",
                with_traceback=False,
            )

        result = self.execute_olap_command(
            command_name="view",
            state="set_show_inter_total_mode",
            show=show,
            dimension_id=dim_id,
            position=1,
        )
        return result

    @timing
    def set_inter_vertical_total(self, dimension_name: str, show: bool) -> dict:
        """
        Изменить режим отображения промежуточного итога по вынесенной вверх размерности в текущем OLAP-модуле.
        :param dimension_name: Имя размерности. Размерность не должна быть на самом нижнем уровне.
        :param show: (bool) Режим отображения, если True, то отобразить промежуточный итог по указанной размерности,
            если False, то скрыть промежуточный итог по ней.
        :return: (dict) command ("view", "set_show_inter_total_mode_rp"
        """
        if not self.multisphere_module_id:
            return self._raise_exception(
                PolymaticaException,
                "Active OLAP-module not found!",
                with_traceback=False,
            )

        _, top_dims = self._get_left_and_top_dims_count()
        if top_dims < 2:
            return self._raise_exception(
                PolymaticaException,
                "There must be at least 2 top dimensions!",
                with_traceback=False,
            )

        dim_id = self.get_dim_id(dimension_name)
        dims_data_result = self.execute_olap_command(
            command_name="view",
            state="get",
            from_row=0,
            from_col=0,
            num_row=1,
            num_col=1,
        )
        top_dims = self.h.parse_result(dims_data_result, "top_dims")
        if top_dims[-1] == dim_id:
            return self._raise_exception(
                PolymaticaException,
                "The dimension should not be at the lowest level!",
                with_traceback=False,
            )

        result = self.execute_olap_command(
            command_name="view",
            state="set_show_inter_total_mode",
            show=show,
            dimension_id=dim_id,
            position=2,
        )
        return result

    @timing
    def request_to_api_v2(
        self,
        url: str,
        method: str,
        headers: dict,
        cookies=None,
        data=None,
        json: dict = None,
    ):
        if cookies is None:
            cookies = {"session": self.session_id}

        return requests.request(
            method=method,
            url=url,
            headers=headers,
            cookies=cookies,
            data=data,
            json=json,
        )

    @timing
    def switch_session(self, new_owner_uuid: str) -> int:
        """
        Переключить владельца сессии.
        :param new_owner_uuid: (str) UUID_4 - идентификатор пользователя, который должен стать владельцем текущей сессии
        :return: (int) статус код:
            Статусы ответа:
            204 No Content - успешно.
            401 Unauthorized - запрос от неавторизованного пользователя;
            400 Bad Request - пустое тело запроса; content type не "application/json"; не было запрошено никаких
                изменений, например, при передаче пустого Json-объекта в теле запроса; тип данных в полях тела
                запроса не соответствует ожидаемому;
            403 Forbidden - текущий пользователь не имеет роли администратора системы;
            404 Not Found - пользователь с идентификатором new_owner не найден;
            500 Internal server error - что-то пошло не так на стороне сервера.
        """
        url = self.base_url + "api/v2/sessions/current"
        data = {"new_owner": new_owner_uuid}
        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
        }

        response = self.request_to_api_v2(
            url=url, method="PATCH", headers=headers, json=data
        )
        assert response.status_code == 204, "Response status code != 204"

        return response.status_code

    @timing
    def cleanup_multisphere_data(
        self,
        cube_name: str,
        dimension_name: str,
        sql_params: dict,
        is_update: bool = True,
    ) -> dict:
        """
        Удаляет записи из мультисферы на основе SQL-запроса.

        :param cube_name: (str) Название обновляемой мультисферы.
        :param dimension_name: (str) Название размерности, по которой происходит обновление.
        :param sql_params: (dict) параметр для источника данных SQL.
            Поля, передаваемые в словарь:
                "query" - запрос, который необходимо выполнить на сервере.
            Пример задания параметра:
                {
                    "query": "SELECT pi.square FROM public.impl pi;",
                }
            или
                {
                    "query": "SELECT dist FROM table WHERE dist = 'ЮФО';",
                }
            или
                {
                    "query": "SELECT \"Клиент_Компания\" FROM public.bi_orders_details
                    WHERE \"Клиент_Компания\" = 'ВАРП АГ'"
                }

        :param is_update: (bool) Запустить обновление после удаления. По умолчанию True.
        :return: (dict) - результат команды ("user_cube", "cleanup_rp").
        """
        # Проверки типов
        params = validate_params(
            CleanUpParams,
            self._raise_exception,
            cube_name=cube_name,
            dimension_name=dimension_name,
            sql_params=sql_params,
            is_update=is_update,
        )
        cube_name, dimension_name, sql_params, is_update = (
            params.cube_name,
            params.dimension_name,
            params.sql_params,
            params.is_update,
        )

        # Получаем id куба
        cube_id = self.get_cube_without_creating_module(cube_name)

        # Получаем источник
        metadata_result = self.execute_manager_command(
            command_name="user_cube",
            state="ext_info_several_sources_request",
            cube_id=cube_id,
        )
        datasources = self.h.parse_result(metadata_result, "datasources")

        # Проверяем источник
        if len(datasources) != 1:
            return self._raise_exception(
                PolymaticaException,
                "There must be one data source!",
                with_traceback=False,
            )
        datasource = datasources[0]
        datasource_id = datasource.get("id")
        if datasource.get("server_type") not in DB_SOURCE_TYPES:
            return self._raise_exception(
                PolymaticaException,
                "Data source must be DB-type!",
                with_traceback=False,
            )

        # Проверяем SQL-запрос
        query = sql_params["query"]
        datasource["sql_query"] = query
        sql_query_preview = self.execute_manager_command(
            command_name="user_cube",
            state="data_preview_request",
            cube_id=cube_id,
            datasource=datasource,
        )
        column_name = self.h.parse_result(sql_query_preview, "preview_result")[0]
        if len(column_name) != 1:
            return self._raise_exception(
                PolymaticaException,
                "Query must return exactly 1 column. Please change the query.",
                with_traceback=False,
            )

        # Получаем id поля размерности в БД
        dims = self.h.parse_result(metadata_result, "dims")
        field_id = next(
            (
                dim.get("field_id")
                for dim in dims
                if dim.get("db_field") == dimension_name
            ),
            None,
        )
        if not field_id:
            return self._raise_exception(
                PolymaticaException, "Dimension not found!", with_traceback=False
            )

        # Собираем sql_params и выполняем команду cleanup.
        sql_params["datasource_id"] = datasource_id
        sql_params["field_id"] = field_id
        cleanup = {
            "querying_datasources": [sql_params],
            "start_update_after": is_update,
        }
        cleanup_result = self.execute_manager_command(
            command_name="user_cube", state="cleanup", cube_id=cube_id, cleanup=cleanup
        )
        return cleanup_result

    def filter_get_data(self, dim_id: str, num: int, from_num: int = 0) -> dict:
        """
        Вызов команды ("filter", "get_data"). Получение данных для окна фильтрации элементов размерности.
        :param dim_id: (str) идентификатор размерности;
        :param num: (int) количество считываемых элементов.
        :param from_num: (int) с какого элемента начинать получение данных, по умолчанию 0.
        :return: (dict) Результат команды ("filter", "pattern_change").
        """
        result = self.execute_olap_command(
            command_name="filter",
            state="get_data",
            dimension=dim_id,
            **{"from": from_num},
            num=num)
        return result


class GetDataChunk:
    """Класс для получения данных чанками"""

    def __init__(self, sc: BusinessLogic):
        """
        Инициализация класса GetDataChunk
        :param sc: экземпляр класса BusinessLogic
        """
        self.logger = sc.logger
        self.logger.info("GetDataChunk init")

        # флаг работы в Jupiter Notebook
        self.jupiter = sc.jupiter

        # helper class
        self.h = Helper(self)

        # экзмепляр класса BusinessLogic
        self.sc = sc

        # хранит функцию-генератор исключений
        self._raise_exception = raise_exception(self.sc)

        # флаги наличия дубликатов размерностей и фактов
        self.measure_duplicated, self.dim_duplicated = False, False

        # получаем левые/верхние размерности, считаем их количество
        self.left_dims, self.top_dims = self._get_active_dims()

        # внутренний флаг работы со скриптом
        self.script_mode = sc.script_mode

        # обязательное условие: чтобы получить данные, должна быть вынесена хотя бы одна левая размерность
        # (кроме специальных скриптов)
        if not self.left_dims and not self.script_mode:
            error_msg = (
                "For page-by-page loading of the multisphere, "
                "at least one dimension must be moved to the left!"
            )
            self._raise_exception(
                PolymaticaException, error_msg, with_traceback=False
            )

        # считаем количество левых размерностей, верхних размерностей, фактов и общее число колонок
        self.left_dims_qty, self.top_dims_qty, self.facts_qty = (
            len(self.left_dims),
            len(self.top_dims),
            0,
        )

        # список имён активных размерностей
        self.dim_lst = []

        # получаем количество строк в мультисфере
        total_row, _ = self.sc.get_row_and_col_num(
            with_total_cols=False, with_total_rows=False
        )
        self.total_row = total_row

        self.total_row_show_full = self.get_total_rows(True)

        # словарь типов размерностей Полиматики; т.к. все значения этого словаря уникальны, его можно "перевернуть"
        self.olap_types = self.sc.server_codes.get("olap", {}).get("olap_data_type", {})
        self.reversed_olap_types = {
            value: key for key, value in self.olap_types.items()
        }

        # список колонок в формате
        # {"id": <column id>, "data_type": <dimension/fact/fact_dimension>,
        # "name": <column name>, "type": <column type>}
        self.columns = self._get_col_types()

        # общее количество колонок
        self.total_cols = (
            self.left_dims_qty + self.facts_qty
        )  # можно ещё так: self.total_cols = len(self.columns)

        # все размерности и факты с дополнительными параметрами
        self._olap_module_info = None

        # сохраняем отдельно названия, типы и id колонок, чтобы их не вычислять по несколько раз
        self.column_names, self.column_types, self.column_ids = [], [], []
        for column in self.columns:
            self.column_names.append(column.get("name"))
            self.column_types.append(column.get("type"))
            self.column_ids.append(column.get("id"))

    def _get_active_dims(self) -> List:
        """
        Возвращает список левых и верхних размерностей мультисферы.
        """
        result = self.sc.execute_olap_command(
            command_name="view",
            state="get",
            from_row=0,
            from_col=0,
            num_row=1,
            num_col=1,
        )
        return (
            self.h.parse_result(result, "left_dims") or [],
            self.h.parse_result(result, "top_dims") or [],
        )

    def _get_data(self) -> List:
        """
        Получение первой строки данных. Необходимо для дальнейшего определения типов столбцов.
        """
        columns_data = self.sc.execute_olap_command(
            command_name="view",
            state="get_2",
            from_row=0,
            from_col=0,
            num_row=10,
            num_col=1000,
        )
        data = self.h.parse_result(columns_data, "data")
        return data[self.top_dims_qty + 1] if self.top_dims_qty + 1 < len(data) else []

    def _get_all_dims(self) -> List:
        """
        Получение всех размерностей мультисферы.
        """
        all_dims_data = self.sc.execute_olap_command(
            command_name="dimension", state="list_rq"
        )
        return self.h.parse_result(all_dims_data, "dimensions")

    def _get_measures(self) -> List:
        """
        Получение всех фактов мультисферы.
        """
        all_measures_data = self.sc.execute_olap_command(
            command_name="fact", state="list_rq"
        )
        return self.h.parse_result(all_measures_data, "facts")

    def _get_dim_type(self, olap_type: int) -> str:
        """
        Возвращает тип размерности.
        """
        return list(self.olap_types.keys())[
            list(self.olap_types.values()).index(olap_type)
        ]

    def _update_or_append_key(self, dict_container: dict, key: str):
        """
        Добавляет ключ в словарь, если его ещё там нет, иначе значение ключа увеличивает на 1.
        """
        if key not in dict_container:
            dict_container.update({key: 1})
        else:
            dict_container[key] += 1

    def _get_active_measure_ids(self) -> List:
        """
        Получение активных фактов (т.е. фактов, отображаемых в таблице мультисферы)
        """
        data = self.sc.execute_olap_command(
            command_name="view",
            state="get",
            from_row=0,
            from_col=0,
            num_row=10,
            num_col=1000,
        )
        top, measure_data = self.h.parse_result(data, "top"), dict()
        for i in top:
            if "fact_id" in str(i):
                measure_data = i
                break
        return [measure.get("fact_id") for measure in measure_data]

    def _get_col_types(self) -> List:
        """
        Получить текущие колонки мультисферы в заданном формате.
        :return: (list) колонки мультисферы в формате
            [{"id": "column_id", "name": "column_name", "type": "column_type", "data_type": "column_data_type"}, ...]
        """
        # список колонок,
        # содержащий словари вида {"id": <column_id>, "name": <column_name>,
        # "type": <column_type>, "data_type": <column_data_type>}
        columns = list()
        exists_columns = set()

        # получение первой строки, содержащей данные мультисферы
        # если по какой-то причине данных нет - выдаём ошибку
        data = self._get_data()
        if not data:
            error_msg = (
                "To page-by-page loading of a multisphere, it must contain data!"
            )
            return self._raise_exception(
                PolymaticaException, error_msg, with_traceback=False
            )

        # получение списка всех размерностей
        all_dims = self._get_all_dims()

        # получение всех фактов и формирование из них вспомогательных данных
        measures_data = self._get_measures()
        measure_id_map = {
            measure.get("id"): measure.get("name") for measure in measures_data
        }
        measures_name_list = [measure.get("name") for measure in measures_data]

        # для накопления списка всех размерностей-дубликатов и фактов-дубликатов
        dims_dups, measure_dups = dict(), dict()

        # добавление размерностей в список колонок
        for my_dim in self.left_dims:
            for dim in all_dims:
                if my_dim == dim.get("id"):
                    dim_name = dim.get("name")
                    if dim_name in exists_columns:
                        self._update_or_append_key(dims_dups, dim_name)
                        dim_name = f"{dim_name} (dim{dims_dups.get(dim_name)})"
                        self.dim_duplicated = True

                    # составляем итоговый словарь и добавляем его в список колонок
                    dim_data = {
                        "id": dim.get("id"),
                        "name": dim_name,
                        "type": self._get_dim_type(dim.get("olap_type")),
                        # "type": self.reversed_olap_types.get(dim.get("olap_type")), # альтернатива
                        "data_type": "fact_dimension"
                        if dim_name in measures_name_list
                        else "dimension",
                    }
                    columns.append(dim_data)
                    exists_columns.add(dim_name)
                    self.dim_lst.append(dim_name)
                    break

        # получение идентификаторов активных фактов
        measure_ids = self._get_active_measure_ids()

        measure_types = dict()

        # добавление фактов в список колонок
        for measure_id in measure_ids:
            measure_name = measure_id_map.get(measure_id)
            check_measure_name = measure_name
            if measure_name in exists_columns:
                self._update_or_append_key(measure_dups, measure_name)
                measure_name = f"{measure_name} (fact{measure_dups.get(measure_name)})"
                self.measure_duplicated = True

            # определяем тип факта
            if measure_id not in measure_types:
                measure_type = (
                    "double" if isinstance(data[len(columns)], float) else "uint32"
                )
                measure_types.update({measure_id: measure_type})
            else:
                measure_type = measure_types[measure_id]

            # составляем итоговый словарь и добавляем его в список колонок
            measure_data = {
                "id": measure_id,
                "name": measure_name,
                "type": measure_type,
                "data_type": "fact_dimension"
                if check_measure_name in self.dim_lst
                else "fact",
            }
            columns.append(measure_data)
            exists_columns.add(measure_name)
            self.facts_qty += 1

        return columns

    def get_total_rows(self, show_full: bool = False) -> int:
        response = self.sc.execute_olap_command(
            command_name="view",
            state="get_2",
            from_row=0,
            from_col=0,
            num_row=1,
            num_col=1,
            show_inter_total=show_full,
            show_horz_total=show_full,
            show_vert_total=show_full,
        )
        return self.h.parse_result(response, "total_row")

    def load_sphere_chunk(
        self,
        units: int = UNITS_LOAD_DATA_CHUNK,
        convert_type: bool = False,
        default_value: Any = None,
        convert_empty_values: bool = True,
        show_full: bool = False,
    ) -> dict:
        """
        Генератор, подгружающий мультисферу постранично (порциями строк).
        Особенности использования метода:
            1. В мультисфере не должно быть вынесенных вверх размерностей, иначе будет сгенерировано исключение.
            2. Для корректного получения данных необходимо,
                чтобы перед вызовом метода были развёрнуты все узлы мультисферы.
            3. Все тоталы (как промежуточные, так и итоговые) генератором выведены не будут вне зависимости от того,
                включены они или нет.
        :param units: (int) количество подгружаемых строк; ожидается целое положительное число больше 0;
            по-умолчанию 100.
        :param convert_type: (bool) нужно ли преобразовывать данные из типов, определённых Полиматикой, к Python-типам;
            по-умолчанию False (т.е. не нужно).
        :param default_value: (Any) актуален только при convert_type = True;
            дефолтное значение, использующееся в случае, если не удалось преобразовать исходные данные к нужному типу;
            по-умолчанию None.
        :param convert_empty_values: (bool) актуален только при convert_type = True;
            нужно ли преобразовывать строки формата "(Пустой)"/"(Empty)" к дефолтному значению (см. default_value);
            строки, состоящие только из одних пробелов, также считаются пустыми; по-умолчанию True (т.е. нужно).
        :param show_full: (bool) отобразить таблицу вместе с загололвками;
        :return: (dict) словарь {имя колонки: значение колонки}.
        :call_example:
            # импорт модуля из библиотеки
            from polyapi import business_scenarios

            # инициализация класса BusinessLogic
            bl = business_scenarios.BusinessLogic(login="login", password="password", url="url", **args)

            # делаем все необходимые действия (открытие мультисферы, раскрытие всех узлов и тд)
            bl.get_cube('cube_name')
            bl.expand_all_dims()

            # инициализация класса GetDataChunk
            gdc = business_scenarios.GetDataChunk(bl)

            # получение генератора данных
            gen = gdc.load_sphere_chunk(
                units="units",
                convert_type="convert_type",
                default_value="default_value",
                convert_empty_values="convert_empty_values"
            )

            # получение данных мультисферы чанками
            for row_data in gen:
                print(row_data)
        """
        # проверка на вынесенные вверх размерности
        if self.top_dims and not show_full:
            error_msg = (
                "Page-by-page loading of multisphere is not possible "
                "because there are some top dimensions.\n"
                "You must first move all dimensions to the left "
                'by calling the "move_up_dims_to_left()" method of the BusinessLogic class,\n'
                "or set the show_full = True flag to display the table with headers.\n"
                "Also, to get correct data, it is recommended to expand all dimensions "
                "of the multisphere.\n"
                'This can be done by calling the "expand_all_dims()" method of the BusinessLogic class.'
            )
            return self._raise_exception(
                PolymaticaException, error_msg, with_traceback=False
            )

        # проверка на количество подгружаемых строк
        self.sc.checks("load_sphere_chunk", units, convert_type, convert_empty_values)

        # если был передан параметр convert_type, то нужно инициализировать класс преобразования типов
        if convert_type:
            type_converter = TypeConverter(self.sc, default_value, convert_empty_values)

        self.total_row_show_full = self.get_total_rows(show_full)
        headers_count = self.top_dims_qty + 1

        rows_data = None
        start, total_row = 0, self.total_row_show_full
        while total_row > 0:
            total_row -= units

            # получаем число вызываемых строк и столбцов
            exec_num_row, exec_num_col = units, self.total_cols

            # получаем информацию о представлении
            rows_result = self.sc.execute_olap_command(
                command_name="view",
                state="get_2",
                from_row=start,
                from_col=0,
                num_row=exec_num_row,
                num_col=exec_num_col,
                show_inter_total=show_full,
                show_horz_total=show_full,
                show_vert_total=show_full,
            )
            data_parsed = self.h.parse_result(result=rows_result, key="data")

            headers_count = self.top_dims_qty + 1
            if rows_data is None and show_full:
                rows_data = data_parsed
            else:
                rows_data = data_parsed[headers_count:]

            for idx, item in enumerate(rows_data):
                if show_full and idx < headers_count:
                    yield dict(zip(range(len(item)), item))  # return header
                else:
                    ms_data = (
                        type_converter.convert_data_types(self.column_types, item)
                        if convert_type
                        else item
                    )
                    yield dict(zip(self.column_names, ms_data))  # return converted data

            start += units

    DICT_CELL_TYPES = {
        1: "Пустая ячейка",
        2: "Базовая размерность",
        3: "Групповая размерность",
        4: "Факты",
        5: "Всего",
    }

    def load_sphere_chunk_v2(
        self,
        units: int = UNITS_LOAD_DATA_CHUNK,
    ) -> Tuple[list, list, list, Callable, dict]:
        """
        Обновленный метод, возвращающий хедеры и функцию-генератор для выгрузки данных мультисферы по чанкам.
        Данные выгружаются с типами. Формат ячейки с данными: {"value": <value (str)>, "type": <тип (int)>}.
        :return: top dims list, left dims list, data header list[list], load_data_by_chunk function, extra info dict:
            {
                "data_cols_count": <количество колонок с данными>,
                "data_rows_count": <количество строк с данными>,
                "inter_total_hidden_dimensions": <скрытые подыитоги>,
                "show_global_horz_total": <скрытые глобальные горизантальные итоги>,
                "show_global_vert_total": <скрытые глобальные вертикальные итоги>,
            }
        """
        assert units > 0, ValueError("units (size of chank) cannot be less 1")

        # get dimensions
        response = self.sc.execute_olap_command(
            command_name="dimension",
            state="list_rq",
        )
        dimensions: Dict[dict] = {
            dim["id"]: dim for dim in self.h.parse_result(response, "dimensions")
        }

        # get facts
        response = self.sc.execute_olap_command(
            command_name="fact",
            state="list_rq",
        )
        facts: Dict[dict] = {
            dim["id"]: dim for dim in self.h.parse_result(response, "facts")
        }

        # load 1 row with 1 col to get valid total_col and total_row
        response = self.sc.execute_olap_command(
            command_name="view",
            state="get",
            from_row=0,
            from_col=0,
            num_row=1,
            num_col=1,
        )

        data_cols_count = self.h.parse_result(response, "total_col")
        data_rows_count = self.h.parse_result(response, "total_row")
        inter_total_hidden_dimensions = self.h.parse_result(
            response, "inter_total_hidden_dimensions"
        )
        show_global_horz_total = self.h.parse_result(response, "show_global_horz_total")
        show_global_vert_total = self.h.parse_result(response, "show_global_horz_total")

        extra_info = {
            "data_cols_count": data_cols_count,
            "data_rows_count": data_rows_count,
            "inter_total_hidden_dimensions": inter_total_hidden_dimensions,
            "show_global_horz_total": show_global_horz_total,
            "show_global_vert_total": show_global_vert_total,
        }

        # load all cols to create correct data headers
        response = self.sc.execute_olap_command(
            command_name="view",
            state="get",
            from_row=0,
            from_col=0,
            num_row=1,
            num_col=data_cols_count,
        )

        top_dims = [
            dimensions[dim_id]["name"]
            for dim_id in self.h.parse_result(response, "top_dims")
        ]
        left_dims = [
            dimensions[dim_id]["name"]
            for dim_id in self.h.parse_result(response, "left_dims")
        ]

        data_header = []
        for row in self.h.parse_result(response, "top"):
            tmp_data_header_row = []
            for cell in row:
                if cell["type"] == 4:  # fact
                    fact_id = cell["fact_id"]
                    cell["value"] = facts[fact_id]["name"]
                tmp_data_header_row += [{
                    "value": cell.get("value", None),
                    "type": cell.get("type"),
                    "fact_id": cell.get("fact_id")
                }]
            data_header += [tmp_data_header_row]

        def load_data_by_chunk() -> Tuple[list, list]:
            """
            Function-generator for loading data from sphere by chunks.
            :return: left columns list[list], data list[list]
            """
            idx_start_row = 0

            while idx_start_row < data_rows_count:
                idx_end_row = idx_start_row + units

                response = self.sc.execute_olap_command(
                    command_name="view",
                    state="get",
                    from_row=idx_start_row,
                    from_col=0,
                    num_row=units,
                    num_col=data_cols_count,
                )
                left_data = [
                    [
                        {"value": cell.get("value", None), "type": cell.get("type")}
                        for cell in row
                    ]
                    for row in self.h.parse_result(response, "left")
                ]
                data = self.h.parse_result(response, "data")

                yield left_data, data

                idx_start_row = idx_end_row

        return top_dims, left_dims, data_header, load_data_by_chunk, extra_info

    @property
    def olap_module_info(self):
        """
        Получает дополнительную информацию по размерностям в обработанном формате.
        Подробнее в методе BusinessLogic.get_olap_module_info.

        :return: (dict) текущая конфигурация OLAP--модуля;
        """
        if not self._olap_module_info:
            self._olap_module_info = self.sc.get_olap_module_info()
        return self._olap_module_info

    def _get_filter_for_dim(self, dim_id: str, num: int = 500000) -> (list, list):
        """
        Получает фильтры для размерности и возвращает значения с маской: 0 - выключен, 1 - включен.
        Загружает элементы размерности чанками по 500k.
        :param dim_id: (Str) id размерности
        :param num: (int) количество элементов, которое необходимо передать.
        :return: (List, List) возвращает два списка со значениями и маской 0-1
        """
        filter_values = []
        filter_mask = []
        from_num = 0
        global_elems = None
        while True:
            result = self.sc.filter_get_data(dim_id=dim_id, num=num, from_num=from_num)
            filter_values.extend(self.h.parse_result(result=result, key="data"))
            filter_mask.extend(self.h.parse_result(result=result, key="marks"))
            if global_elems is None:
                global_elems = self.sc.h.parse_result(result=result, key="global")
            if global_elems <= len(filter_values):
                break
            from_num += num

        return filter_values, filter_mask

    def get_dimension_with_filters(self, copy_dims: bool = True) -> list:
        """
        Подгружает фильтры для размерностей и дополняет ранее созданный словарь.
        Возвращает список с дополненными размерностями.

        :param copy_dims: (Bool) если 'True', копирует данные в новый объект, если 'False', редактирует исходный
        :return: (List) список  [{... , 'filter': {'values': [...] ,'mask': [...]}}, ...]
        """
        dimensions: list = self.olap_module_info["dimensions"]

        dims = []
        for dimension in dimensions:
            if dimension.get("have_filter", None):
                edit_dimension = copy.deepcopy(dimension) if copy_dims else dimension
                filter_values, filter_mask = self._get_filter_for_dim(
                    edit_dimension["id"]
                )
                edit_dimension["filter"] = {
                    "values": filter_values,
                    "mask": filter_mask,
                }
                dims += [edit_dimension]
        return dims

    def get_measure_dims(self, visible: Optional[bool] = None) -> list:
        """
        Получение всех фактов мультисферы, с некоторыми ограничениями при указании параметров.

        :param visible: (Optional[bool]) размерность видима или скрыта
        :return: (List) список размерностей с дополнительными параметрами [{'id': ..., ...}, ...]
        """
        res = self._get_measures()
        if visible is not None:
            res = [dim for dim in res if visible == dim["visible"]]
        return res
