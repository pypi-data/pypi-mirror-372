#!/usr/bin/python3
"""
Реализация графика типа "Радар".
"""

from ..base_graph import BaseGraph, BusinessLogic


class Radar(BaseGraph):
    """
    Реализация графика типа "Радар".
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
            'title_show': <value>,
            'legend': <value>,
            'axis': <value>,
            'show_axis_label': <value>
        }
        """
        return self.get_actual_settings(
            ["title_show", "legend", "axis", "show_axis_label"]
        )

    def draw(self):
        """
        Отрисовка графика. Состоит из нескольких этапов:
        1. Проверка данных для текущего типа графика;
        2. Формирование конфигурации графика;
        3. Вызов команды, отрисовывающей график.
        """
        # проверка данных и получение всех настроек
        self.check_olap_configuration(1, 0, 1, None)
        settings = self._get_settings()

        # получение базовых настроек и их дополнение на основе заданных пользователем значений
        graph_config = self.get_graph_config().copy()
        base_setting = {
            "titleShow": settings.get("title_show"),
            "legend": settings.get("legend"),
            "oxValues": settings.get("axis"),
            "oyValues": settings.get("show_axis_label"),
        }
        graph_config["plotData"][self.graph_type]["config"].update(
            {"base": base_setting}
        )

        # и, наконец, сохраняя настройки, отрисовываем сам график
        self.save_graph_settings(graph_config)
