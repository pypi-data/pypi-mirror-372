#!/usr/bin/python3
""" Реализация команд модуля OLAP (500) """

import logging
from typing import Dict, List

from polymatica.commands.base_command import BaseCommand


class OlapCommands(BaseCommand):
    """Класс, исполняющий команды модуля OLAP"""

    def __init__(
        self, session_id: str, uuid: str, server_codes: Dict, jupiter: bool = False
    ):
        """
        Инициализация класса OlapCommands, исполняющего команды модуля OLAP.
        :param session_id: идентификатор сессии.
        :param uuid: идентификатор текущего мененджера.
        :param server_codes: словарь, хранящий описание команд и состояний (файл "server_codes.json").
        :param jupiter: флаг использования в Jupyter Notebook.
        """
        super().__init__(session_id, server_codes, uuid, jupiter)

    def multisphere_data_query(self, multisphere_module_id: str, view: Dict) -> List:
        """
        Формирование запроса, получающего всю информацию о мультисфере: данные, размерности (левые/верхние) и факты.
        :param multisphere_module_id: идентификатор OLAP-модуля (модуля мультисферы).
        :param view: словарь вида {"from_row": value, "from_col": value, "num_row": value, "num_col": value}.
        :return: (dict) запрос, содержащий команды на получение данных, размерностей и фактов мультисферы.
        """
        assert "from_row" in view, "key 'from_row' was not added in param: view"
        assert "from_col" in view, "key 'from_col' was not added in param: view"
        assert "num_row" in view, "key 'num_row' was not added in param: view"
        assert "num_col" in view, "key 'num_col' was not added in param: view"

        params = self.common_request_params()
        olap_command_codes = self.server_codes["olap"]["command"]
        commands = ["dimension", "fact", "view"]

        for index, item in enumerate(commands):
            try:
                command = {
                    "plm_type_code": olap_command_codes[item]["id"],
                    "state": olap_command_codes["dimension"]["state"]["list_rq"],
                }
            except KeyError as e:
                error_msg = f'No such command/state in "server_codes.json": {e}'
                logging.exception(error_msg)
                logging.info("APPLICATION STOPPED")
                if self.jupiter:
                    return error_msg
                raise
            if command["plm_type_code"] == 506:
                command.update(view)
            query = {"uuid": multisphere_module_id, "command": command}
            params["queries"].append(query)
            params["queries"][index]["command"] = command

        return params
