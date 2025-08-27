from __future__ import annotations

from lightningchart.charts import Chart
from lightningchart import Themes
from lightningchart.series import Series, SeriesWith2DPoints, PolarPointStyle
from lightningchart.utils import convert_to_dict, convert_color_to_hex


class PolarPointSeries(SeriesWith2DPoints, PolarPointStyle):
    """Series type for visualizing polar point data."""

    def __init__(
        self,
        chart: Chart,
        theme: Themes = Themes.Light,
        name: str = None,
    ):
        Series.__init__(self, chart)
        self.instance.send(
            self.id,
            'addPointSeries',
            {
                'chart': self.chart.id,
                'theme': theme.value,
                'name': name,
            },
        )

    def set_data(self, data: list[dict]):
        """Set the data for the series.

        Args:
            data (list[dict]): A list of dictionaries, each containing:
                - 'angle' (float): The angle in degrees.
                - 'amplitude' (float): The amplitude at that angle.
                - optional 'color' (Color): color property

        Example:
            series.set_data([
                {'angle': 0, 'amplitude': 5},
                {'angle': 90, 'amplitude': 10},
                {'angle': 180, 'amplitude': 7.5},
                {'angle': 270, 'amplitude': 3},
            ])

        Returns:
            The instance of the class for fluent interface.
        """
        data = convert_to_dict(data)

        for i in data:
            if 'color' in i:
                i['color'] = convert_color_to_hex(i['color'])

        self.instance.send(self.id, 'setDataPolarPoint', {'data': data})
        return self

    def enable_individual_point_colors(self):
        """Enable individual point coloring.
        Required for using 'color' properties in data points with set_data.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setIndividualPointFillStyle', {})
        return self

    def set_auto_scrolling_enabled(self, enabled: bool = True):
        """Set whether series is taken into account with automatic scrolling and fitting of attached axes.

        Args:
            enabled: Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAutoScrollingEnabled', {'enabled': enabled})
        return self

    def set_point_alignment(self, x: float, y: float):
        """Set alignment of points. Defaults to center { x: 0, y: 0 }.

        Args:
            x: x-axis alignment in range [-1, 1]
            y: y-axis alignment in range [-1, 1]

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setPointAlignment', {'x': x, 'y': y})
        return self
