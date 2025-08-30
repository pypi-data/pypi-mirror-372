#!/usr/bin/python3
"""
Реализация графика типа "Пироги".
"""

from ..base_graph import BaseGraph, BusinessLogic


class Pies(BaseGraph):
    """
    Реализация графика типа "Пироги".
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
            'show_notes': <value>
        }
        """
        return self.get_actual_settings(["title_show", "legend", "show_notes"])

    def _get_other_settings(self) -> dict:
        """
        Получение прочих настроек графика.
        :return: {
            'show_sector_values': <value>,
            'min_sector': <value>,
            'restrict_signature': <value>,
            'size_of_signatures': <value>
        }
        """
        # получаем значения
        show_sector_values = self.other.get("show_sector_values", False)
        min_sector = self.other.get("min_sector", 0)
        restrict_signature = self.other.get("restrict_signature", 10)
        size_of_signatures = self.other.get("size_of_signatures", 12)

        # проверка на типы и диапазоны
        if not self.check_bool(show_sector_values):
            raise ValueError('Param "show_sector_values" must be bool type!')
        self.check_interval_with_step("min_sector", min_sector, (0, 100), 1)
        self.check_interval_with_step(
            "restrict_signature", restrict_signature, (0, 100), 1
        )
        self.check_interval_with_step(
            "size_of_signatures", size_of_signatures, (7, 15), 1
        )

        return {
            "show_sector_values": show_sector_values,
            "min_sector": min_sector,
            "restrict_signature": restrict_signature,
            "size_of_signatures": size_of_signatures,
        }

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
        other_settings = self._get_other_settings()

        # получение базовых настроек и их дополнение на основе заданных пользователем значений
        graph_config = self.get_graph_config().copy()
        base_setting = {
            "titleShow": settings.get("title_show"),
            "legend": settings.get("legend"),
            "notes": settings.get("show_notes"),
        }
        pie_setting = {
            "hintsShowPercent": other_settings.get("restrict_signature"),
            "labelFontSize": other_settings.get("size_of_signatures"),
            "min": 0,
            "piePercent": other_settings.get("min_sector"),
            "sectorValues": other_settings.get("show_sector_values"),
        }
        graph_config["plotData"][self.graph_type]["config"].update(
            {"base": base_setting, "pieData": pie_setting}
        )
        graph_config["plotData"][self.graph_type]["query"].update(
            {"pie_percent": other_settings.get("min_sector")}
        )

        # и, наконец, сохраняя настройки, отрисовываем сам график
        self.save_graph_settings(graph_config)
