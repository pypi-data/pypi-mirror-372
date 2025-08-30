#!/usr/bin/python3
""" Модуль исполнения команд к серверу Полиматики """

import ast
import json
import logging
from typing import Dict, Union

import requests

from polymatica.common import responce
from polymatica.error_handler import request_asserts
from polymatica.exceptions import PolymaticaException

# Недопустимые управляюещие символы в json (взято из RFC 1345, начиная с символа 0000)
INVALID_CONTROL_CHARACTERS = [
    "\u0000",
    "\u0001",
    "\u0002",
    "\u0003",
    "\u0004",
    "\u0005",
    "\u0006",
    "\u0007",
    "\u0008",
    "\u0009",
    "\u0010",
    "\u0011",
    "\u0012",
    "\u0013",
    "\u0014",
    "\u0015",
    "\u0016",
    "\u0017",
    "\u0018",
    "\u0019",
    "\u001a",
    "\u001b",
    "\u001c",
    "\u001d",
    "\u001e",
    "\u001f",
    "\u007f",
    "\u0080",
    "\u0081",
    "\u0082",
    "\u0083",
    "\u0084",
    "\u0085",
    "\u0086",
    "\u0087",
    "\u0088",
    "\u0089",
    "\u008a",
    "\u008b",
    "\u008c",
    "\u008d",
    "\u008e",
    "\u008f",
    "\u0090",
    "\u0091",
    "\u0092",
    "\u0093",
    "\u0094",
    "\u0095",
    "\u0096",
    "\u0097",
    "\u0098",
    "\u0099",
    "\u009a",
    "\u009b",
    "\u009c",
    "\u009d",
    "\u009e",
    "\u009f",
    "\ue000",
    "\ue001",
    "\ue002",
    "\ue003",
    "\ue004",
    "\ue005",
    "\ue006",
    "\ue007",
    "\ue008",
    "\ue009",
    "\ue010",
    "\ue011",
    "\ue012",
    "\ue013",
    "\ue014",
    "\ue015",
    "\ue016",
    "\ue017",
    "\ue018",
    "\ue019",
    "\ue01a",
    "\ue01b",
    "\ue01c",
    "\ue01d",
    "\ue01e",
    "\ue01f",
    "\ue020",
    "\ue021",
    "\ue022",
    "\ue023",
    "\ue024",
    "\ue025",
    "\ue026",
    "\ue027",
    "\ue027",
    "\u080f",
    "\ufeff",
]


# ************* RFC 1345 *********************
#
#  NU     0000    NULL (NUL)
#  SH     0001    START OF HEADING (SOH)
#  SX     0002    START OF TEXT (STX)
#  EX     0003    END OF TEXT (ETX)
#  ET     0004    END OF TRANSMISSION (EOT)
#  EQ     0005    ENQUIRY (ENQ)
#  AK     0006    ACKNOWLEDGE (ACK)
#  BL     0007    BELL (BEL)
#  BS     0008    BACKSPACE (BS)
#  HT     0009    CHARACTER TABULATION (HT)
#  LF     000a    LINE FEED (LF)
#  VT     000b    LINE TABULATION (VT)
#  FF     000c    FORM FEED (FF)
#  CR     000d    CARRIAGE RETURN (CR)
#  SO     000e    SHIFT OUT (SO)
#  SI     000f    SHIFT IN (SI)
#  DL     0010    DATALINK ESCAPE (DLE)
#  D1     0011    DEVICE CONTROL ONE (DC1)
#  D2     0012    DEVICE CONTROL TWO (DC2)
#  D3     0013    DEVICE CONTROL THREE (DC3)
#  D4     0014    DEVICE CONTROL FOUR (DC4)
#  NK     0015    NEGATIVE ACKNOWLEDGE (NAK)
#  SY     0016    SYNCRONOUS IDLE (SYN)
#  EB     0017    END OF TRANSMISSION BLOCK (ETB)
#  CN     0018    CANCEL (CAN)
#  EM     0019    END OF MEDIUM (EM)
#  SB     001a    SUBSTITUTE (SUB)
#  EC     001b    ESCAPE (ESC)
#  FS     001c    FILE SEPARATOR (IS4)
#  GS     001d    GROUP SEPARATOR (IS3)
#  RS     001e    RECORD SEPARATOR (IS2)
#  US     001f    UNIT SEPARATOR (IS1)
#  DT     007f    DELETE (DEL)
#  PA     0080    PADDING CHARACTER (PAD)
#  HO     0081    HIGH OCTET PRESET (HOP)
#  BH     0082    BREAK PERMITTED HERE (BPH)
#  NH     0083    NO BREAK HERE (NBH)
#  IN     0084    INDEX (IND)
#  NL     0085    NEXT LINE (NEL)
#  SA     0086    START OF SELECTED AREA (SSA)
#  ES     0087    END OF SELECTED AREA (ESA)
#  HS     0088    CHARACTER TABULATION SET (HTS)
#  HJ     0089    CHARACTER TABULATION WITH JUSTIFICATION (HTJ)
#  VS     008a    LINE TABULATION SET (VTS)
#  PD     008b    PARTIAL LINE FORWARD (PLD)
#  PU     008c    PARTIAL LINE BACKWARD (PLU)
#  RI     008d    REVERSE LINE FEED (RI)
#  S2     008e    SINGLE-SHIFT TWO (SS2)
#  S3     008f    SINGLE-SHIFT THREE (SS3)
#  DC     0090    DEVICE CONTROL STRING (DCS)
#  P1     0091    PRIVATE USE ONE (PU1)
#  P2     0092    PRIVATE USE TWO (PU2)
#  TS     0093    SET TRANSMIT STATE (STS)
#  CC     0094    CANCEL CHARACTER (CCH)
#  MW     0095    MESSAGE WAITING (MW)
#  SG     0096    START OF GUARDED AREA (SPA)
#  EG     0097    END OF GUARDED AREA (EPA)
#  SS     0098    START OF STRING (SOS)
#  GC     0099    SINGLE GRAPHIC CHARACTER INTRODUCER (SGCI)
#  SC     009a    SINGLE CHARACTER INTRODUCER (SCI)
#  CI     009b    CONTROL SEQUENCE INTRODUCER (CSI)
#  ST     009c    STRING TERMINATOR (ST)
#  OC     009d    OPERATING SYSTEM COMMAND (OSC)
#  PM     009e    PRIVACY MESSAGE (PM)
#  AC     009f    APPLICATION PROGRAM COMMAND (APC)
#         e000    indicates unfinished (Mnemonic)
#  /c     e001    JOIN THIS LINE WITH NEXT LINE (Mnemonic)
#  UA     e002    Unit space A (ISO-IR-8-1 064)
#  UB     e003    Unit space B (ISO-IR-8-1 096)
#  "3     e004    NON-SPACING UMLAUT (ISO-IR-38 201) (character part)
#  "1     e005    NON-SPACING DIAERESIS WITH ACCENT (ISO-IR-70 192)
#                 (character part)
#  "!     e006    NON-SPACING GRAVE ACCENT (ISO-IR-103 193) (character part)
#  "'     e007    NON-SPACING ACUTE ACCENT (ISO-IR-103 194) (character
#                 part)
#  ">     e008    NON-SPACING CIRCUMFLEX ACCENT (ISO-IR-103 195)
#                 (character part)
#  "?     e009    NON-SPACING TILDE (ISO-IR-103 196) (character part)
#  "-     e00a    NON-SPACING MACRON (ISO-IR-103 197) (character part)
#  "(     e00b    NON-SPACING BREVE (ISO-IR-103 198) (character part)
#  ".     e00c    NON-SPACING DOT ABOVE (ISO-IR-103 199) (character part)
#  ":     e00d    NON-SPACING DIAERESIS (ISO-IR-103 200) (character part)
#  "0     e00e    NON-SPACING RING ABOVE (ISO-IR-103 202) (character part)
#  ""     e00f    NON-SPACING DOUBLE ACCUTE (ISO-IR-103 204) (character
#                 part)
#  "<     e010    NON-SPACING CARON (ISO-IR-103 206) (character part)
#  ",     e011    NON-SPACING CEDILLA (ISO-IR-103 203) (character part)
#  ";     e012    NON-SPACING OGONEK (ISO-IR-103 206) (character part)
#  "_     e013    NON-SPACING LOW LINE (ISO-IR-103 204) (character
#                 part)
#  "=     e014    NON-SPACING DOUBLE LOW LINE (ISO-IR-38 217) (character
#                 part)
#  "/     e015    NON-SPACING LONG SOLIDUS (ISO-IR-128 201) (character
#                 part)
#  "i     e016    GREEK NON-SPACING IOTA BELOW (ISO-IR-55 39) (character
#                 part)
#  "d     e017    GREEK NON-SPACING DASIA PNEUMATA (ISO-IR-55 38)
#                 (character part)
#  "p     e018    GREEK NON-SPACING PSILI PNEUMATA (ISO-IR-55 37)
#                 (character part)
#  ;;     e019    GREEK DASIA PNEUMATA (ISO-IR-18 92)
#  ,,     e01a    GREEK PSILI PNEUMATA (ISO-IR-18 124)
#  b3     e01b    GREEK SMALL LETTER MIDDLE BETA (ISO-IR-18 99)
#  Ci     e01c    CIRCLE (ISO-IR-83 0294)
#  f(     e01d    FUNCTION SIGN (ISO-IR-143 221)
#  ed     e01e    LATIN SMALL LETTER EZH (ISO-IR-158 142)
#  am     e01f    ANTE MERIDIAM SIGN (ISO-IR-149 0267)
#  pm     e020    POST MERIDIAM SIGN (ISO-IR-149 0268)
#  Tel    e021    TEL COMPATIBILITY SIGN (ISO-IR-149 0269)
#  a+:    e022    ARABIC LETTER ALEF FINAL FORM COMPATIBILITY (IBM868 144)
#  Fl     e023    DUTCH GUILDER SIGN (IBM437 159)
#  GF     e024    GAMMA FUNCTION SIGN (ISO-10646-1DIS 032/032/037/122)
#  >V     e025    RIGHTWARDS VECTOR ABOVE (ISO-10646-1DIS 032/032/038/046)
#  !*     e026    GREEK VARIA (ISO-10646-1DIS 032/032/042/164)
#  ?*     e027    GREEK PERISPOMENI (ISO-10646-1DIS 032/032/042/165)
#  J<     e028    LATIN CAPITAL LETTER J WITH CARON (lowercase: 000/000/001/240)


class Executor:
    """Класс, выполняющий запросы к серверу Полиматики"""

    def __init__(
        self,
        session_id: str,
        manager_uuid: str,
        base_url: str,
        command_url: str,
        timeout: Union[float, int],
        poly_version: str,
    ):
        """
        Инициализация класса Executor.
        :param session_id: идентификатор сессии.
        :param manager_uuid: UUID мененджера (UUID авторизации).
        :param base_url: базовый (основной) URL стенда Полиматики.
        :param command_url: URL стенда Полиматики, использующийся для исполнения серверных команд.
        :param timeout: тайм-аут выполнения запросов.
        :param poly_version: базовая (мажорная) версия Полиматики ('5.7', ...)
        """
        self.session_id = session_id
        self.manager_uuid = manager_uuid
        self.base_url = base_url
        self.command_url = command_url
        self.timeout = timeout
        self.version = poly_version

    def _convert_to_utf_8(self, pattern: str) -> str:
        """
        Конвертация заданной строки в кодировку utf-8.
        """
        return pattern.encode("utf-8")

    @staticmethod
    def get_server_codes(base_url: str) -> Dict:
        """
        Получение GET-запросом списка команд и состояний, которые используются в Полиматике.
        :param base_url: (str) базовый URL-адрес стенда Полиматики.
        :return: словарь списков и состояний, расположенный по пути base_url/server-codes.json.
        """
        r = requests.get(f"{base_url}server-codes.json")
        assert r.status_code == 200, f"Response code == {r.status_code}!"
        return r.json()

    def execute_request(
        self, params: Union[Dict, str], method: str = "POST"
    ) -> responce:
        """
        Непосредственно отправка запроса на сервер Полиматики.
        :param params: (Dict) параметры запроса для метода POST
                        (str) URL файла для методов GET/PUT
        :param method: (str) Тип HTTP-метода ("POST"/"GET"/"PUT").
        :return: (Dict) Ответ сервера на заданный запрос.
        """
        cookies = {"session": self.session_id}

        if method == "GET":
            return requests.get(url=params, cookies=cookies, timeout=self.timeout)
        elif method == "PUT":
            headers = {
                "content-type": "application/octet-stream",
                "X-Requested-With": "XMLHttpRequest",
                "Upload-Position": "0",
                "Last-Part": "1",
            }
            with open(params, "rb") as file:
                r = requests.put(
                    f"{self.base_url}query/upload.php?",
                    data=file,
                    cookies=cookies,
                    headers=headers,
                )
            return r
        else:
            # получаем текущую пару (команда, состояние)
            request_queries = params.get("queries")
            request_queries = next(iter(request_queries))
            request_command = request_queries.get("command")
            command_state = (
                request_command.get("plm_type_code"),
                request_command.get("state"),
            )

            # для некоторых команд необходимо передавать запрос в виде строки с кодировкой utf-8, т.к. в запросе
            # могут быть русские символы (кириллица)
            if (
                command_state
                in ((210, 7), (210, 14), (502, 5), (503, 6), (503, 24), (505, 4))
                or self.version >= "5.7"
                and command_state in ((207, 21))
            ):
                # command: 207 (user_iface), state: 21 (rename_module) [only 5.7]
                # command: 210 (user_layer), state: 7 (save_layer)
                # command: 210 (user_layer), state: 14 (rename_layer)
                # command: 502 (dimension), state: 5 (rename)
                # command: 503 (fact), state: 6 (create_group)
                # command: 503 (fact), state: 24 (rename)
                # command: 505 (group), state: 4 (set_name)
                # к этой группе относятся команды создания/изменения имени
                params = str(params)
                params = params.replace("'", '"')
                headers = {
                    "Content-Type": "text/plain; charset=utf-8",
                    "Accept": "text/plain",
                }
                if command_state == (502, 5):
                    headers.update(
                        {
                            "Accept": "application/json, text/javascript, */*; q=0.01",
                            "Accept-Encoding": "gzip, deflate",
                            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                            "X-Requested-With": "XMLHttpRequest",
                        }
                    )
                r = requests.post(
                    url=self.command_url,
                    headers=headers,
                    data=self._convert_to_utf_8(params),
                )
            elif (
                command_state
                in (
                    (207, 13),
                    (208, 12),
                    (208, 14),
                    (208, 58),
                    (502, 11),
                    (503, 4),
                    (504, 2),
                )
                or self.version >= "5.7"
                and command_state in ((208, 28), (208, 40), (208, 42))
            ):
                # command: 207 (user_iface), state: 13 (save_settings)
                # command: 208 (user_cube), state: 12 (test_source_connection_request)
                # command: 208 (user_cube), state: 14 (data_preview_request)
                # command: 208 (user_cube), state: 30 (save_ext_info_several_sources_request)
                # command: 208 (user_cube), state: 42 (get_fields_request)
                # command: 208 (user_cube), state: 44 (create_cube_request)
                # command: 502 (dimension), state: 11 (create_union)
                # command: 503 (fact), state: 4 (create_calc)
                # command: 504 (filter), state: 2 (pattern_change)
                # TODO разобраться с этим при рефакторинге
                if command_state in ((208, 14), (208, 58)):
                    new_param = json.dumps(params, ensure_ascii=False)
                else:
                    params, new_param = str(params), ""
                    for elem in params:
                        if elem == "'":
                            new_param += '"'
                            continue
                        if elem == '"':
                            new_param += "'"
                            continue
                        new_param += elem
                    new_param = (
                        new_param.replace("False", "false")
                        .replace("True", "true")
                        .replace("None", "null")
                    )

                # определяем заголовки
                if (
                    command_state in ((208, 14), (208, 58))
                    or self.version >= "5.7"
                    and command_state in ((208, 40), (208, 42))
                ):
                    headers = {
                        "Accept": "application/json, text/javascript, */*; q=0.01",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                        "X-Requested-With": "XMLHttpRequest",
                    }
                else:
                    headers = {
                        "Content-Type": "text/plain; charset=utf-8",
                        "Accept": "text/plain",
                    }

                r = requests.post(
                    url=self.command_url,
                    headers=headers,
                    data=self._convert_to_utf_8(new_param),
                    timeout=self.timeout,
                )
            else:
                headers = {
                    "Content-Type": "application/json; charset=utf-8",
                    "Accept": "text/plain",
                }
                r_params = json.dumps(params)
                r = requests.post(
                    url=self.command_url,
                    headers=headers,
                    data=self._convert_to_utf_8(r_params),
                    timeout=self.timeout,
                )

            # парсинг ответа и проверка его корректности
            if not r.ok:
                msg = 'Invalid server response (URL: {}, Code: {}, Reason: "{}", Text: {})'.format(
                    self.command_url,
                    r.status_code,
                    r.reason,
                    "<empty>" if not r.text else r.text,
                )
                raise PolymaticaException(msg)
            else:
                try:
                    response = json.loads(r.text)
                except ValueError as ex:
                    logging.exception(f"Error converting response to JSON: {ex}")

                    # избавляемся от управляющих символов, если они есть
                    str_response = r.text
                    for icc in INVALID_CONTROL_CHARACTERS:
                        if icc in str_response:
                            str_response = str_response.replace(icc, "")
                    # str_response = str_response.replace("'", "\"") # нужна ли эта строчка вообще?!

                    # попытка снова преобразовать в json, но уже другим способом
                    json_str = (
                        str_response.replace("true", "True")
                        .replace("false", "False")
                        .replace("null", "None")
                    )
                    try:
                        response = ast.literal_eval(json_str)
                    except Exception:
                        raise PolymaticaException(
                            f"Cannot convert request response to JSON: {ex}"
                        )

            request_asserts(response, r)
            return response
