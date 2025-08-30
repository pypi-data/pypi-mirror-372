#!/usr/bin/python3
"""
Реализация графика типа "Санкей".
"""

from ..base_graph import BaseGraph, BusinessLogic


class Sankey(BaseGraph):
    """
    Реализация графика типа "Санкей".
    """

    def __init__(
        self,
        base_bl: BusinessLogic,
        settings: str,
        grid: str,
        labels: dict,
        other: dict,
        common_params: dict,
        plot_type: str,
    ):
        super().__init__(
            base_bl, settings, grid, labels, other, common_params, plot_type, -1
        )

    def _get_settings(self) -> dict:
        """
        Получение актуальных настроек по заданному битмапу.
        :return: {
            'title_show': <value>
        }
        """
        return self.get_actual_settings(["title_show"])

    def draw(self):
        """
        Отрисовка графика. Состоит из нескольких этапов:
        1. Проверка данных для текущего типа графика;
        2. Формирование конфигурации графика;
        3. Вызов команды, отрисовывающей график.
        """
        # проверка данных и получение всех настроек
        self.check_olap_configuration(2, 0, 1, True)
        settings = self._get_settings()

        # получение базовых настроек и их дополнение на основе заданных пользователем значений
        graph_config = self.get_graph_config().copy()
        graph_config["plotData"][self.graph_type]["config"].update(
            {"base": {"titleShow": settings.get("title_show")}}
        )

        # и, наконец, сохраняя настройки, отрисовываем сам график
        self.save_graph_settings(graph_config)
