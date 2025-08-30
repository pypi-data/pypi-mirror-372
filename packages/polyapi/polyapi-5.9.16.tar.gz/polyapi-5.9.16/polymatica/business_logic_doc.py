#!/usr/bin/python3
"""
Базовый класс, описывающий бизнес-сценарии использования Полиматики.
Используемые переменные класса:

# Флаг работы в Jupiter Notebook
self.jupiter

# Флаг гостевого пользователя при беспарольной авторизации
self.is_guest

# Текст ошибки присваивается в случае аварийного завершения работы; может быть удобно при работе в Jupiter Notebook
self.current_exception

# Версия сервера Полиматики; например, '5.6'
self.polymatica_version

# Полная версия сервера Полиматики; например, '5.6.14-ab9def0-7799123f-x86_64-centos'
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

# Вспомогательный класс, перенаправляющий вызовы методов на нужные реализации (в зависимости от версии)
self.version_redirect
"""

__name__ = "BusinessLogic"
