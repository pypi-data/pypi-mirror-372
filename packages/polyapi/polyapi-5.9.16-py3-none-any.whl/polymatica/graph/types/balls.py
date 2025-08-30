#!/usr/bin/python3
"""
Реализация графика типа "Шары".
"""

from ..base_graph import BaseGraph, BusinessLogic


class Balls(BaseGraph):
    """
    Реализация графика типа "Шары".
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
        :return: {'shadowsVisible': <value>, 'size': <value>, 'defaultSize': <value>[, 'colors': <value>]}.
        """
        show_shadows = self.other.get("show_shadows", True)
        diameter_range, diameter = self.other.get(
            "diameter_range", (4, 48)
        ), self.other.get("diameter", 4)

        if not self.check_bool(show_shadows):
            raise ValueError('Param "show_shadows" must be bool type!')
        self.check_range_with_step("diameter_range", diameter_range, (4, 48), 1)
        self.check_interval_with_step("diameter", diameter, (4, 48), 1)

        settings = {
            "shadowsVisible": show_shadows,
            "size": list(diameter_range),
            "defaultSize": diameter,
        }
        colors = self.other.get("colors", ["#ffff00", "#3c9bea"])
        if len(colors) != 2:
            raise ValueError('Wrong param "colors"! Excepted 2 colors in list!')
        settings.update(
            {
                "colors": [
                    color.lower() for color in colors if self.check_color(color) or True
                ]
            }
        )
        return settings

    def draw(self):
        """
        Отрисовка графика. Состоит из нескольких этапов:
        1. Проверка данных для текущего типа графика;
        2. Формирование конфигурации графика;
        3. Вызов команды, отрисовывающей график.
        """
        # проверка данных и получение всех настроек
        self.check_olap_configuration(1, 0, 3, True)
        settings = self._get_settings()
        labels_settings = self.get_labels_settings("three_axis")

        # получение базовых настроек и их дополнение на основе заданных пользователем значений
        graph_config = self.get_graph_config().copy()
        base_setting = {
            "titleShow": settings.get("title_show"),
            "legend": settings.get("legend"),
            "axis": settings.get("axis"),
            "axisNotes": settings.get("axis_notes"),
        }
        base_setting.update(labels_settings)
        graph_config["plotData"][self.graph_type]["config"].update(
            {"base": base_setting, "spheres": self._get_other_settings()}
        )

        # и, наконец, сохраняя настройки, отрисовываем сам график
        self.save_graph_settings(graph_config)
