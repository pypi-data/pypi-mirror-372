#!/usr/bin/python3
""" Описание базового класса, необходимого для реализации и исполнения команд различных модулей """

import logging
from typing import Dict


class BaseCommand:
    """
    Базовый класс, необходимый для реализации и исполнения команд различных модулей.
    Содержит общую часть для создания всех запросов.
    Именно от этого класса наследуются классы, реализующие команды непосредственно каждого модуля.
    """

    def __init__(
        self, session_id: str, server_codes: Dict, uuid: str, jupiter: bool = False
    ):
        self.session_id = session_id
        self.server_codes = server_codes
        self.uuid = uuid
        self.jupiter = jupiter

    def common_request_params(self) -> Dict:
        """
        Описание шаблона всех запросов.
        :return: словарь с общими параметрами для дальнейшего исполнения всех запросов.
        """
        return {
            # в запросе имеет значение 0, в ответе - 1
            "state": 0,
            # идентификатор текущей сессии
            "session": self.session_id,
            # query1, query2, ..., queryN будут присоединены к этому списку запросов
            "queries": [],
        }

    def collect_command(
        self, module: str, command_name: str, state: str, **kwargs
    ) -> Dict:
        """
        Сбор пары (команда, состояние) воедино на основе server_codes.json для дальнейшего вызова этого запроса.
        :param module: название модуля; возможны варианты: "manager", "olap", "graph".
        :param command_name: название команды.
        :param state: название состояния.
        :param kwargs: все остальные поля, которые необходимо передать в команде (но их может и не быть).
        :return: (dict) {"plm_type_code": ..., "state": ...}
        """
        query = {"uuid": self.uuid, "command": "your command"}

        # добавляет обязательные поля в словарь, который вернет метод:
        try:
            command = {
                "plm_type_code": self.server_codes[module]["command"][command_name][
                    "id"
                ],
                "state": self.server_codes[module]["command"][command_name]["state"][
                    state
                ],
            }
        except KeyError as e:
            error_msg = (
                f'EXCEPTION! No such command/state in server_codes.json: "{e.args[0]}"'
            )
            logging.exception(error_msg)
            logging.info("APPLICATION STOPPED")
            if self.jupiter:
                return error_msg
            raise ValueError(error_msg)

        # если указаны необязательные параметры, добавялем их в возвращаемое значение
        # если необязательных полей нет, то в словаре останутся только обязательные поля plm_type_code, state
        for param in kwargs:
            if state == "apply_data":
                command.update({"from": 0})
            command.update({param: kwargs.get(param)})
        query["command"] = command
        return query

    def collect_request(self, *args) -> Dict:
        """
        Формирование тела запроса.
        :param args: команды, добавляемые в запрос.
        :return: конечный запрос.
        """
        params = self.common_request_params()
        for query in args:
            params["queries"].append(query)
        return params
