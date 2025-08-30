#!/usr/bin/python3
"""
Реализация графика типа "Цилиндры".
"""

from ..base_graph import BaseGraph, BusinessLogic


class Cylinders(BaseGraph):
    """
    Реализация графика типа "Цилиндры".
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
        :return: {'hints': <value>, 'enableIndentation': <value>, 'indentation': <value>[, 'round': <value>]}.
        """
        hints = self.other.get("hints", False)
        ident, ident_value = self.other.get("ident", True), self.other.get(
            "ident_value", 0.9
        )
        if not self.check_bool(hints):
            raise ValueError('Param "hints" must be bool type!')
        if not self.check_bool(ident):
            raise ValueError('Param "ident" must be bool type!')
        self.check_interval_with_step("ident_value", ident_value, (0, 1), 0.05)
        settings = {
            "hints": hints,
            "enableIndentation": ident,
            "indentation": ident_value,
        }

        hints_round = self.other.get("round", False)
        if not self.check_bool(hints_round):
            raise ValueError('Param "round" must be bool type!')
        settings.update({"round": hints_round})
        return settings

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
            "axis": settings.get("axis"),
            "axisNotes": settings.get("axis_notes"),
            "axisPosition": settings.get("vertical_right_axix"),
            "wireShow": self.grid,
        }
        base_setting.update(self.get_labels_settings("two_axis"))
        graph_config["plotData"][self.graph_type]["config"].update(
            {"base": base_setting, "cylinder": self._get_other_settings()}
        )

        # и, наконец, сохраняя настройки, отрисовываем сам график
        self.save_graph_settings(graph_config)
