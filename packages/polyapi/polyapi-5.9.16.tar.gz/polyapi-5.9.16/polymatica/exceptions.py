#!/usr/bin/python3
""" Описание всех исключений, генерируемых питоновской библиотекой Полиматики. """


# Иерархия исключений
#
# BaseException
#    |- ... default Python exceptions ...
#    |- Exception
#        |- ... default Python exceptions ...
#        |- PolymaticaException
#            |- NotFoundError
#                |- OLAPModuleNotFoundError
#                |- CubeNotFoundError
#                |- UserNotFoundError
#            |- CommandError
#                |- ManagerCommandError
#                |- OLAPCommandError
#                |- GraphCommandError
#            |- ParseError
#            |- AuthError
#            |- ScenarioError
#            |- ExportError
#            |- RightsError
#            |- GraphError
#            |- FilterError
#            |- CubeError
#            |- DecodeError
#            |- DBConnectionError


class PolymaticaException(Exception):
    """
    Ошибки, генерируемые библиотекой полиматики (Python Lib Polymatica).
    Параметры конструктора:
        user_msg - пользовательское сообщение об ошибке, должно быть максимально понятно конечному пользователю.
        extend_msg - расширенное сообщение об ошибке, может быть полезно при отладке.
        code - код ошибки (по-умолчанию 0).
    """

    def __init__(self, user_msg, extend_msg="", code=0):
        self._user_msg = user_msg
        self._extend_msg = extend_msg
        self._code = code

    @property
    def user_msg(self):
        """Возвращает пользовательское сообщение"""
        return self._user_msg

    @property
    def extend_msg(self):
        """Возвращает расширенное сообщение"""
        return self._extend_msg

    @property
    def code(self):
        """Возвращает код ошибки"""
        return self._code

    def __str__(self):
        return "{}{}".format(
            self.user_msg,
            f" (extend: {self.extend_msg})" if self.extend_msg else "",
        )


class NotFoundError(PolymaticaException):
    """Не найдена заданная составляющая Полиматики (например, куб, OLAP или любой другой модуль и тд)"""

    pass


class OLAPModuleNotFoundError(NotFoundError):
    """Не найден OLAP-модуль с заданным параметром (например, названием или идентификатором)"""

    pass


class CubeNotFoundError(NotFoundError):
    """Не найден куб с заданным именем/идентификатором"""

    pass


class UserNotFoundError(NotFoundError):
    """Не найден пользователь с заданным логином/идентификатором"""

    pass


class ParseError(PolymaticaException):
    """Невозможно распарсить ответ от API"""

    pass


class AuthError(PolymaticaException):
    """Ошибки аутентификации"""

    pass


class CommandError(PolymaticaException):
    """Ошибки исполнения команд"""

    pass


class ManagerCommandError(CommandError):
    """Ошибки исполнения команд модуля Manager"""

    pass


class OLAPCommandError(CommandError):
    """Ошибки исполнения команд модуля OLAP"""

    pass


class GraphCommandError(CommandError):
    """Ошибки исполнения команд модуля Graph"""

    pass


class ScenarioError(PolymaticaException):
    """Ошибки сценариев"""

    pass


class ExportError(PolymaticaException):
    """Ошибки экспорта файла"""

    pass


class RightsError(PolymaticaException):
    """Ошибки, связанные с системой прав и доступов"""

    pass


class GraphError(PolymaticaException):
    """Ошибки, связанные с созданием/изменением графиков"""

    pass


class FilterError(PolymaticaException):
    """Ошибки фильтрации"""

    pass


class CubeError(PolymaticaException):
    """Ошибки кубов (мультисфер)"""

    pass


class DecodeError(PolymaticaException):
    """Ошибки кодировки/декодирования"""

    pass


class DBConnectionError(PolymaticaException):
    """Ошибки соединения с БД"""

    pass
