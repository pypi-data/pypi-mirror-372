#!/usr/bin/python3
"""
Реализация графика типа "Круги".
"""

from ..base_graph import BaseGraph, BusinessLogic


class Circles(BaseGraph):
    """
    Реализация графика типа "Круги".
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
            'axis_notes': <value>,
            'vertical_right_axix': <value>
        }
        """
        return self.get_actual_settings(
            ["title_show", "legend", "axis", "axis_notes", "vertical_right_axix"]
        )

    def _get_other_settings(self) -> dict:
        """
        Получение прочих настроек графика.
        :return: {'diameter_range': <value>, 'diameter': <value>, 'show_trend_line': <value>, 'default_color': <value>}.
        """
        diameter_range, diameter = self.other.get(
            "diameter_range", (3, 15)
        ), self.other.get("diameter", 10)
        show_trend_line = self.other.get("show_trend_line", False)
        self.check_range_with_step("diameter_range", diameter_range, (1, 50), 1)
        self.check_interval_with_step("diameter", diameter, (1, 50), 1)
        if not self.check_bool(show_trend_line):
            raise ValueError('Param "show_trend_line" must be bool type!')
        return {
            "diameter_range": list(diameter_range),
            "diameter": diameter,
            "show_trend_line": show_trend_line,
            "default_color": self.default_color,
        }

    def draw(self):
        """
        Отрисовка графика. Состоит из нескольких этапов:
        1. Проверка данных для текущего типа графика;
        2. Формирование конфигурации графика;
        3. Вызов команды, отрисовывающей график.
        """
        self.check_olap_configuration(1, 0, 2, True)

        # получение всех настроек
        settings = self._get_settings()
        labels_settings = self.get_labels_settings("two_axis", add_short_format=False)
        other_settings = self._get_other_settings()

        # получение базовых настроек и их дополнение на основе заданных пользователем значений
        graph_config = self.get_graph_config().copy()
        base_setting = {
            "titleShow": settings.get("title_show"),
            "legend": settings.get("legend"),
            "axis": settings.get("axis"),
            "axisNotes": settings.get("axis_notes"),
            "axisPosition": settings.get("vertical_right_axix"),
            "wireShow": self.grid,
        }
        base_setting.update(labels_settings)
        bubble_setting = {
            "defSize": other_settings.get("diameter"),
            "size": other_settings.get("diameter_range"),
            "trendLine": other_settings.get("show_trend_line"),
            "defaultColor": other_settings.get("default_color"),
        }
        graph_config["plotData"][self.graph_type]["config"].update(
            {"base": base_setting, "bubbleBase": bubble_setting}
        )

        # и, наконец, сохраняя настройки, отрисовываем сам график
        self.save_graph_settings(graph_config)
