#!/usr/bin/python3
"""
Реализация графика типа "3D бассейны".
"""

from ..base_graph import BaseGraph, BusinessLogic


class Pools3D(BaseGraph):
    """
    Реализация графика типа "3D бассейны".
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
            'axis_notes': <value>
        }
        """
        return self.get_actual_settings(["title_show", "legend", "axis", "axis_notes"])

    def _get_other_settings(self) -> dict:
        """
        Получение прочих настроек графика.
        :return: {'diameter_range': <value>, 'diameter': <value>, 'show_shadows': <value>, "shadows_color": <value>}.
        """
        diameter_range, diameter = self.other.get(
            "diameter_range", (4, 48)
        ), self.other.get("diameter", 4)
        self.check_range_with_step("diameter_range", diameter_range, (4, 48), 1)
        self.check_interval_with_step("diameter", diameter, (4, 48), 1)
        return {
            "diameter_range": list(diameter_range),
            "diameter": diameter,
            "show_shadows": True,
            "shadows_color": "#cccccc",
        }

    def draw(self):
        """
        Отрисовка графика. Состоит из нескольких этапов:
        1. Проверка данных для текущего типа графика;
        2. Формирование конфигурации графика;
        3. Вызов команды, отрисовывающей график.
        """
        # проверка данных и получение всех настроек
        self.check_olap_configuration(2, 0, 3, True)
        settings = self._get_settings()
        labels_settings = self.get_labels_settings("three_axis")
        other_settings = self._get_other_settings()

        # получение базовых настроек и их дополнение на основе заданных пользователем значений
        graph_config = self.get_graph_config().copy()
        base_setting = {
            "titleShow": settings.get("title_show"),
            "legend": settings.get("legend"),
            "axis": settings.get("axis"),
            "axisNotes": settings.get("axis_notes"),
            "shadowsColor": other_settings.get("shadows_color"),
        }
        base_setting.update(labels_settings)
        spheres_setting = {
            "defaultSize": other_settings.get("diameter"),
            "shadowsVisible": other_settings.get("show_shadows"),
            "size": other_settings.get("diameter_range"),
        }
        graph_config["plotData"][self.graph_type]["config"].update(
            {"base": base_setting, "spheres": spheres_setting}
        )

        # и, наконец, сохраняя настройки, отрисовываем сам график
        self.save_graph_settings(graph_config)
