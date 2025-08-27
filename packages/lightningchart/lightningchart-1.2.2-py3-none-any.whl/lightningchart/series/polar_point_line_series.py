from __future__ import annotations

from lightningchart.charts import Chart
from lightningchart import Themes
from lightningchart.series import Series, SeriesWith2DLines, SeriesWith2DPoints
from lightningchart.utils import convert_to_dict, convert_color_to_hex


class PolarPointLineSeries(SeriesWith2DLines, SeriesWith2DPoints):
    def __init__(
        self,
        chart: Chart,
        theme: Themes = Themes.Light,
        name: str = None,
    ):
        Series.__init__(self, chart)
        self.instance.send(
            self.id,
            'addPointLineSeries',
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

    def set_stroke(self, thickness: int | float, color: any = None):
        """Set Stroke style of the series.

        Args:
            thickness (int | float): Thickness of the stroke.
            color (Color): Color of the stroke.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(
            self.id,
            'setStrokeStyle',
            {'thickness': thickness, 'color': color},
        )
        return self
