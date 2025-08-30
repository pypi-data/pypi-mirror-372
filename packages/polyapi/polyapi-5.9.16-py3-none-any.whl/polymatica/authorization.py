#!/usr/bin/python3
""" Модуль авторизации в Полиматике """

import json
from typing import Dict, List, Tuple

import requests

from .common import request_with_undefined_suffix_url
from .exceptions import AuthError


class Authorization:
    """Предоставляет возможность авторизации в Полиматике"""

    def login(
        self,
        user_name: str,
        base_url: str,
        server_codes: Dict,
        timeout: float,
        language: str,
        suffixes_url: List,
        is_guest: bool,
        password: str,
    ) -> Tuple:
        """
        Авторизация (парольная/беспарольная).
        :param user_name: имя пользователя.
        :param url: базовый URL стенда Полиматики.
        :param server_codes: значение файла "server_codes.json", хранящего коды команд и их состояний.
        :param timeout: тайм-аут выполнения запроса авторизации.
        :param language: язык локализации; возможны значения: "en" / "ru" / "de" / "fr".
        :param is_guest: флаг гостевого пользователя при беспарольной авторизации.
        :param password: пароль пользователя; может быть не задан (None).
        :param suffixes_url: список возможных суффиксов URL-адреса стенда Полиматики.
        :return: (Tuple) идентификатор сессии, uuid, полная версия Полиматики.
        """
        self._check_language(language)
        session = ""

        if not isinstance(suffixes_url, list):
            raise AuthError('Incorrect "suffixes_url" param: expected list type!')
        suffixes_url.insert(0, "")

        auth_manager_command = (
            server_codes.get("manager", {}).get("command", {}).get("authenticate", {})
        )
        auth_command = auth_manager_command.get("id")
        auth_check = auth_manager_command.get("state", {}).get("check")
        auth_login = auth_manager_command.get("state", {}).get("login")
        locale_value = server_codes.get("locale", {}).get(language)

        # для авторизации без пароля формируем id сессии для беспарольного пользователя
        if password is None:
            is_guest_str = self._check_guest(is_guest)
            login_url = f"{base_url}login?login={user_name}&is_guest={is_guest_str}"
            r = requests.get(url=login_url)
            if not r.ok:
                msg = (
                    'Stand "{}" not supporting non-password authorization. Please, specify the password! '
                    'Details: Code: {}, Reason: "{}", Text: {}'.format(
                        base_url,
                        r.status_code,
                        r.reason,
                        "<empty>" if not r.text else r.text,
                    )
                )
                raise AuthError(msg)
            else:
                try:
                    response = r.json()
                except json.decoder.JSONDecodeError:
                    msg = 'Invalid server response! Details: URL: {}, Code: {}, Reason: "{}", Text: {}'.format(
                        login_url,
                        r.status_code,
                        r.reason,
                        "<empty>" if not r.text else r.text,
                    )
                    raise AuthError(msg)
            session = response.get("session")

        # формирование поля command
        command = {"plm_type_code": auth_command}
        if password is None:
            command.update({"state": auth_check})
        else:
            command.update(
                {
                    "state": auth_login,
                    "login": user_name,
                    "passwd": password,
                    "locale": locale_value,
                }
            )

        # формирование тела и заголовка запроса
        params = {
            "state": 0,
            "session": session,
            "queries": [
                {"uuid": "00000000-00000000-00000000-00000000", "command": command}
            ],
        }
        headers = {"Content-Type": "text/plain; charset=utf-8", "Accept": "text/plain"}

        # отправляем запрос аутентификации на заданный URL
        r, suffix_url = request_with_undefined_suffix_url(
            suffixes_url, base_url, self._get_prepare_query(params), timeout, headers
        )

        # проверки и вывод результата
        status_code = r.status_code
        if not r.ok:
            error_msg = 'Invalid server response (URL: {}, Code: {}, Reason: "{}", Text: {})'.format(
                r.url, status_code, r.reason, "<empty>" if not r.text else r.text
            )
            raise AuthError(error_msg)

        try:
            json_response = r.json()
        except json.decoder.JSONDecodeError:
            raise AuthError("Server response cannot be converted to the JSON format")
        return self._authorization_checks(
            params, json_response, status_code, suffix_url
        )

    def _get_command(self, data: Dict) -> Dict:
        """
        Возвращает команду запроса/ответа.
        """
        queries = next(iter(data.get("queries")))
        return queries.get("command")

    def _authorization_checks(
        self, request: Dict, response: Dict, response_code: int, url_suffix: str
    ) -> Tuple:
        """
        Проверка успешности авторизации. Возвращает идентификатор сессии и manager uuid.
        :param request: (Dict) запрос.
        :param response: (Dict) ответ.
        :param response_code: (int) код ответа.
        :param url_suffix: (str) верное окончание URL-адреса стенда Полиматики.
        :return: (Tuple) идентификатор сессии, uuid, полная версия Полиматики
        """
        # получаем команды и коды запроса/ответа
        request_command = self._get_command(request)
        request_code = request_command.get("plm_type_code")
        resp_command = self._get_command(response)
        resp_code = resp_command.get("plm_type_code")

        # проверки полученных кодов
        assert "error" not in resp_command, resp_command.get(
            "error", "No error description!"
        )
        assert response_code == 200, "Response code != 200"
        assert (
            request_code == resp_code
        ), f"Request plm_type_code ({request_code}) is not equal response plm_type_code ({resp_code})!"

        # проверки идентификаторов session_id и uuid
        session_id, uuid = resp_command.get("session_id"), resp_command.get(
            "manager_uuid"
        )
        assert session_id != "", "session_id is empty!"
        assert session_id is not None, "session_id is None!"
        assert uuid != "", "manager_id is empty!"
        assert uuid is not None, "manager_id is None!"

        return session_id, uuid, resp_command.get("version"), url_suffix

    def _check_language(self, language: str):
        """
        Проверка пользовательского значения языка локализации.
        Если проверка пройдена - ничего не вернёт, в противном случае будет сгенерирована ошибка AuthError.
        :param locale: (str) пользовательское значение языка.
        """
        if language not in ("ru", "en"):
            error_msg = f'Invalid language! Expected: "ru"/"en", found: "{language}"'
            raise AuthError(error_msg)

    def _check_guest(self, guest_param: bool) -> str:
        """
        Проверка параметра "is_guest": должны быть только булевы значения. В противном случае сгенерируется ошибка.
        Возвращает строковое значение параметра.
        """
        if not isinstance(guest_param, bool):
            error_msg = f'Invalid "is_guest" param! Expected: True/False, found: "{guest_param}"'
            raise AuthError(error_msg)
        return "true" if guest_param else "false"

    def _get_prepare_query(self, query: Dict) -> str:
        """
        Подготовка тела запроса для дальнейшей отправки POST-запросом: обработка кириллицы в логине/пароле.
        :param query: (Dict) параметры запроса в формате JSON.
        :return: (str) параметры запроса в формате строки.
        """
        params = str(query)
        return (
            params.replace("'", '"')
            .replace("False", "false")
            .replace("True", "true")
            .replace("None", "null")
            .encode("utf-8")
        )
