#!/usr/bin/python3
"""
Реализация графика типа "Хордовая".
"""

from ..base_graph import BaseGraph, BusinessLogic


class Chord(BaseGraph):
    """
    Реализация графика типа "Хордовая".
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
            'legend': <value>
        }
        """
        return self.get_actual_settings(["title_show", "legend"])

    def _get_other_settings(self) -> dict:
        """
        Получение прочих настроек графика.
        :return: {'show_title': <value>}.
        """
        show_title = self.other.get("show_title", True)
        if not self.check_bool(show_title):
            raise ValueError('Param "show_title" must be bool type!')
        return {"show_title": show_title}

    def draw(self):
        """
        Отрисовка графика. Состоит из нескольких этапов:
        1. Проверка данных для текущего типа графика;
        2. Формирование конфигурации графика;
        3. Вызов команды, отрисовывающей график.
        """
        # проверка данных и получение всех настроек
        self.check_olap_configuration(1, 1, 1, True)
        settings = self._get_settings()
        other_settings = self._get_other_settings()

        # получение базовых настроек и их дополнение на основе заданных пользователем значений
        graph_config = self.get_graph_config().copy()
        graph_config["plotData"][self.graph_type]["config"].update(
            {
                "base": {
                    "titleShow": settings.get("title_show"),
                    "legend": settings.get("legend"),
                },
                "chord": {"notes": other_settings.get("show_title")},
            }
        )

        # и, наконец, сохраняя настройки, отрисовываем сам график
        self.save_graph_settings(graph_config)
