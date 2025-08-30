
# Основные сведения
Библиотека предназначена для работы с Polymatica API.

# Работа с библиотекой
Основным модулем бизнес-логики является файл business_scenarios.py, 
импортировать который можно с помощью команды ``from polymatica import business_scenarios as sc``.

Модуль предоставляет два класса для работы с Полиматикой - ``BusinessLogic`` и ``GetDataChunk``. 
Методы этих классов можно посмотреть при помощи стандартной функции ``dir()``.

Аргументы функций и прочую docstring-документацию модуля и функций можно посмотреть 
при помощи стандартной функции ``help()``.

### Инициализация нового клиентского подключения: 
``session = sc.BusinessLogic(login="your_login", password="your_password", url="polymatica_server_url", **args)``

### Пример создания слоя и воспроизведения сценария на этом слое с использованием PolyAPI

Создадим слой:
``session.execute_manager_command(command_name="user_layer", state="create_layer")``

Запросим список сценариев:
``session.execute_manager_command(command_name="scripts", state="get_script_descriptions_list")``

Загрузим сценарий на слой, используя полученные на предыдущих шагах идентификаторы слоя и сценария:
``session.execute_manager_command(command_name="scripts", state="load_on_layer", runtime_id="d46b7075", script_id="40fc65db", on_load_action=0)``

Воспроизведем сценарий:
``session.execute_manager_command(command_name="scripts", state="play_to_position", runtime_id="d46b7075", script_id="40fc65db", play_to_position=23, clear_workspace=True)``

Получим статус воспроизведения сценария:
``session.execute_manager_command(command_name="scripts", state="get_script_status", runtime_id="d46b7075")``

Получили ответ, из которого видим, что сценарий воспроизведен успешно:
``{'state': 1, 'queries': [{'uuid': '872bdbde-20b9f734-2a5a5ad5-9b08e670', 'command': {'plm_type_code': 227, 'state': 6, 'script_status': {'id': '40fc65db', 'action_name': '', 'status': 3, 'current_step': 24, 'steps_count': 24, 'errors': []}}}]}``

Получим информацию о слое:
``session.execute_manager_command(command_name="user_layer", state="get_layer", layer_id="d46b7075")``
