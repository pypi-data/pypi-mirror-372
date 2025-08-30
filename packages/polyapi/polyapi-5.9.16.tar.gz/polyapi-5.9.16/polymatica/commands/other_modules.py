#!/usr/bin/python3
""" Реализация команд всех модулей, отличных от OLAP (500), а именно: Manager (200), Graph (600) и др."""

from typing import Dict

from polymatica.commands.base_command import BaseCommand


class ManagerCommands(BaseCommand):
    """Класс, исполняющий команды модуля Manager"""

    def __init__(
        self, session_id: str, uuid: str, server_codes: Dict, jupiter: bool = False
    ):
        """
        Инициализация класса ManagerCommands, исполняющего команды модуля Manager.
        :param session_id: идентификатор сессии.
        :param uuid: идентификатор текущего мененджера.
        :param server_codes: словарь, хранящий описание команд и состояний (файл "server_codes.json").
        :param jupiter: флаг использования в Jupyter Notebook.
        """
        super().__init__(session_id, server_codes, uuid, jupiter)


class GraphCommands(BaseCommand):
    """Класс, исполняющий команды модуля Graph"""

    def __init__(
        self, session_id: str, uuid: str, server_codes: Dict, jupiter: bool = False
    ):
        """
        Инициализация класса GraphCommands, исполняющего команды модуля Graph.
        :param session_id: идентификатор сессии.
        :param uuid: идентификатор текущего мененджера.
        :param server_codes: словарь, хранящий описание команд и состояний (файл "server_codes.json").
        :param jupiter: флаг использования в Jupyter Notebook.
        """
        super().__init__(session_id, server_codes, uuid, jupiter)
