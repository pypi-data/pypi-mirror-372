#!/usr/bin/python3
"""
Реализация графика типа "Коридоры".
"""

from ..base_graph import BaseGraph, BusinessLogic


class Corridors(BaseGraph):
    """
    Реализация графика типа "Коридоры".
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
        :return: {'show_points': <value>, 'hints': <value>}.
        """
        show_points, hints = self.other.get("show_points", True), self.other.get(
            "hints", False
        )
        if not self.check_bool(show_points):
            raise ValueError('Param "show_points" must be bool type!')
        if not self.check_bool(hints):
            raise ValueError('Param "hints" must be bool type!')
        return {"show_points": show_points, "hints": hints}

    def draw(self):
        """
        Отрисовка графика. Состоит из нескольких этапов:
        1. Проверка данных для текущего типа графика;
        2. Формирование конфигурации графика;
        3. Вызов команды, отрисовывающей график.
        """
        # проверки
        self.check_olap_configuration(2, 1, 1, True)

        # получение всех настроек
        settings = self._get_settings()
        labels_settings = self.get_labels_settings("two_axis")
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
        lines_setting = {
            "showPoints": other_settings.get("show_points"),
            "hints": other_settings.get("hints"),
        }
        graph_config["plotData"][self.graph_type]["config"].update(
            {"base": base_setting, "lines": lines_setting}
        )

        # и, наконец, сохраняя настройки, отрисовываем сам график
        self.save_graph_settings(graph_config)
