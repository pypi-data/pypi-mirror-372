#!/usr/bin/python3
"""
Реализация графика типа "Области с накоплениями".
"""

from ..base_graph import BaseGraph, BusinessLogic


class CumulativeAreas(BaseGraph):
    """
    Реализация графика типа "Области с накоплениями".
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
        :return: {'graph_type': <value>}.
        """
        graph_type = self.other.get("graph_type", "values")
        if graph_type not in ["values", "percents"]:
            raise ValueError('Param "graph_type" must be or "values" or "percents"!')
        return {"graph_type": graph_type}

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
        cum_areas_setting = {"typeStacked": other_settings.get("graph_type")}
        graph_config["plotData"][self.graph_type]["config"].update(
            {"base": base_setting, "area": cum_areas_setting}
        )

        # и, наконец, сохраняя настройки, отрисовываем сам график
        self.save_graph_settings(graph_config)
