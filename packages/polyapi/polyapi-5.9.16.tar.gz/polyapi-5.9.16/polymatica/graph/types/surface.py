#!/usr/bin/python3
"""
Реализация графика типа "Поверхность".
"""

from ..base_graph import BaseGraph, BusinessLogic


class Surface(BaseGraph):
    """
    Реализация графика типа "Поверхность".
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
            'axis': <value>,
            'axis_notes': <value>
        }
        """
        return self.get_actual_settings(["title_show", "axis", "axis_notes"])

    def _get_other_settings(self) -> dict:
        """
        Получение прочих настроек графика.
        :return: {'show_carcass': <value>, 'opacity': <value>, 'colors': <value>}.
        """
        # получаем параметры
        show_carcass = self.other.get("show_carcass", False)
        opacity = self.other.get("opacity", 100)
        colors = self.other.get("colors", ["#eaf7fb", "#3c9bea", "#08034f"])

        # проверяем значения
        if not self.check_bool(show_carcass):
            raise ValueError('Param "show_carcass" must be bool type!')
        self.check_interval_with_step("opacity", opacity, (0, 100), 1)
        if not self.check_list(colors):
            raise ValueError('Wrong param "colors"! Excepted list type!')
        if len(colors) != 3:
            raise ValueError('Wrong param "colors"! Excepted 3 colors in list!')
        new_colors = [
            color.lower() for color in colors if self.check_color(color) or True
        ]

        # возвращаем значения
        return {"show_carcass": show_carcass, "opacity": opacity, "colors": new_colors}

    def draw(self):
        """
        Отрисовка графика. Состоит из нескольких этапов:
        1. Проверка данных для текущего типа графика;
        2. Формирование конфигурации графика;
        3. Вызов команды, отрисовывающей график.
        """
        # проверка данных и получение всех настроек
        self.check_olap_configuration(1, 1, 1, None)
        settings = self._get_settings()
        other_settings = self._get_other_settings()

        # получение базовых настроек и их дополнение на основе заданных пользователем значений
        graph_config = self.get_graph_config().copy()
        base_setting = {
            "titleShow": settings.get("title_show"),
            "axis": settings.get("axis"),
            "axisNotes": settings.get("axis_notes"),
        }
        surface_setting = {
            "colors": other_settings.get("colors"),
            "opacity": other_settings.get("opacity"),
            "wireframe": other_settings.get("show_carcass"),
        }
        graph_config["plotData"][self.graph_type]["config"].update(
            {"base": base_setting, "surface": surface_setting}
        )

        # и, наконец, сохраняя настройки, отрисовываем сам график
        self.save_graph_settings(graph_config)
