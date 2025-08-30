#!/usr/bin/python3
"""
Реализация графика типа "Граф".
"""

from ..base_graph import BaseGraph, BusinessLogic


class Graph(BaseGraph):
    """
    Реализация графика типа "Граф".
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
            'highlight_nodes': <value>
        }
        """
        return self.get_actual_settings(["title_show", "highlight_nodes"])

    def _get_other_settings(self) -> dict:
        """
        Получение прочих настроек графика.
        :return: {
            'node_colors': <value>,
            'node_min_size': <value>,
            'node_max_size': <value>,
            'edge_colors': <value>,
            'edge_min_thickness': <value>,
            'edge_max_thickness': <value>,
            'neighboring_nodes_count': <value>,
            'min_thickness_on_hover': <value>,
            'opacity_of_unselected': <value>
        }
        """
        other_settings = dict()
        first_color_default, second_color_default = "#1f77b4", "#17becf"

        # получаем и проверяем параметры узлов
        node_settings = self.other.get("node_settings", dict())
        if not self.check_dict(node_settings):
            raise ValueError('Param "node_settings" must be dict type!')
        # переход цвета узлов
        node_colors = node_settings.get("colors", dict())
        if not self.check_dict(node_colors):
            raise ValueError('Param "node_settings.colors" must be dict type!')
        first_node_color = node_colors.get("first", first_color_default)
        self.check_color(first_node_color)
        second_node_color = node_colors.get("second", second_color_default)
        self.check_color(second_node_color)
        # минимальный и максимальный размер узла
        min_size, max_size = node_settings.get("min_size", 1), node_settings.get(
            "max_size", 10
        )
        self.check_interval_with_step("node_settings.min_size", min_size, (1, 10), 0.1)
        self.check_interval_with_step("node_settings.max_size", max_size, (5, 15), 0.1)
        if max_size < min_size:
            raise ValueError(
                'Value of "node_settings.max_size" must be greater than value of "node_settings.min_size"!'
            )
        # если проверки все пройдены - добавляем в словарь
        other_settings.update(
            {
                "node_colors": {
                    "first": first_node_color.lower(),
                    "second": second_node_color.lower(),
                },
                "node_min_size": min_size,
                "node_max_size": max_size,
            }
        )

        # получаем и проверяем параметры рёбер
        edge_settings = self.other.get("edge_settings", dict())
        if not self.check_dict(edge_settings):
            raise ValueError('Param "edge_settings" must be dict type!')
        # переход цвета узлов
        edge_colors = edge_settings.get("colors", dict())
        if not self.check_dict(edge_colors):
            raise ValueError('Param "edge_settings.colors" must be dict type!')
        first_edge_color = edge_colors.get("first", first_color_default)
        self.check_color(first_edge_color)
        second_edge_color = edge_colors.get("second", second_color_default)
        self.check_color(second_edge_color)
        # минимальная и максимальная толщина узла
        min_thickness, max_thickness = edge_settings.get(
            "min_thickness", 1
        ), edge_settings.get("max_thickness", 5)
        self.check_interval_with_step(
            "edge_settings.min_thickness", min_thickness, (1, 5), 0.1
        )
        self.check_interval_with_step(
            "edge_settings.max_thickness", max_thickness, (5, 10), 0.1
        )
        if max_thickness < min_thickness:
            raise ValueError(
                'Value of "edge_settings.max_thickness" must be greater than value of "edge_settings.min_thickness"!'
            )
        # если проверки все пройдены - добавляем в словарь
        other_settings.update(
            {
                "edge_colors": {
                    "first": first_edge_color.lower(),
                    "second": second_edge_color.lower(),
                },
                "edge_min_thickness": min_thickness,
                "edge_max_thickness": max_thickness,
            }
        )

        # остальные параметры
        neighboring_nodes_count = self.other.get("neighboring_nodes_count", 3)
        self.check_interval_with_step(
            "neighboring_nodes_count", neighboring_nodes_count, (0, 5), 1
        )
        min_thickness_on_hover = self.other.get("min_thickness_on_hover", (1, 3))
        self.check_range_with_step(
            "min_thickness_on_hover", min_thickness_on_hover, (0.5, 5), 0.1
        )
        opacity_of_unselected = self.other.get("opacity_of_unselected", 0.7)
        self.check_interval_with_step(
            "opacity_of_unselected", opacity_of_unselected, (0, 1), 0.01
        )
        # если проверки все пройдены - добавляем в словарь
        other_settings.update(
            {
                "neighboring_nodes_count": neighboring_nodes_count,
                "min_thickness_on_hover": list(min_thickness_on_hover),
                "opacity_of_unselected": round(1 - opacity_of_unselected, 2),
            }
        )
        return other_settings

    def draw(self):
        """
        Отрисовка графика. Состоит из нескольких этапов:
        1. Проверка данных для текущего типа графика;
        2. Формирование конфигурации графика;
        3. Вызов команды, отрисовывающей график.
        """
        # проверка данных и получение всех настроек
        self.check_olap_configuration(2, 0, 1, None)
        settings = self._get_settings()
        other_settings = self._get_other_settings()

        # получение базовых настроек и их дополнение на основе заданных пользователем значений
        graph_config = self.get_graph_config().copy()
        base_setting = {
            "titleShow": settings.get("title_show"),
            "highlightFirstDimension": settings.get("highlight_nodes"),
            "colorPoints": other_settings.get("node_colors"),
            "hintOverCount": other_settings.get("neighboring_nodes_count"),
            "hintOverOpacity": other_settings.get("opacity_of_unselected"),
            "hintOverWidth": other_settings.get("min_thickness_on_hover"),
            "rPointsMax": other_settings.get("node_max_size"),
            "rPointsMin": other_settings.get("node_min_size"),
        }
        edges_setting = {
            "colorEdges": other_settings.get("edge_colors"),
            "weightEdgesMax": other_settings.get("edge_max_thickness"),
            "weightEdgesMin": other_settings.get("edge_min_thickness"),
        }
        graph_config["plotData"][self.graph_type]["config"].update(
            {
                "base": base_setting,
                "edges": edges_setting,
                "order": [0, 1, 2, 3],
            }
        )

        # и, наконец, сохраняя настройки, отрисовываем сам график
        self.save_graph_settings(graph_config)
