from __future__ import annotations

import uuid
from lightningchart.charts import Chart
from lightningchart import Themes
from lightningchart.series import Series
from lightningchart.utils import convert_to_dict, convert_color_to_hex


class PolarPolygonSeries(Series):
    """Series type for visualizing a collection of polygons inside the Polar coordinate system."""

    def __init__(
        self,
        chart: Chart,
        theme: Themes = Themes.Light,
        name: str = None,
    ):
        Series.__init__(self, chart)
        self.instance.send(
            self.id,
            'addPolygonSeries',
            {
                'chart': self.chart.id,
                'theme': theme.value,
                'name': name,
            },
        )

    def add_polygon(self):
        """Create new polygon to the Series.

        Returns:
            PolarPolygon instance.
        """
        polygon = PolarPolygon(self)
        self.instance.send(self.id, 'addPolygon', {'polygonId': polygon.id})
        return polygon

    def set_color(self, color: any):
        """Set a color of the series.

        Args:
            color (Color): Color of the band.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setSolidFillStyle', {'color': color})
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


class PolarPolygon:
    """Polygon object in the PolarPolygonSeries."""

    def __init__(self, series: PolarPolygonSeries):
        self.series = series
        self.id = str(uuid.uuid4()).split('-')[0]

    def set_geometry(self, points: list[dict]):
        """Set polygon geometry as a list of PolarPoints.
        NOTE: points have to be in either clockwise or counter-clockwise order.
        The polygon coordinates should also not intersect with themselves.

        Args:
            points (list[dict]): A list of dictionaries, each containing:
                - 'angle' (float): The angle in degrees.
                - 'amplitude' (float): The amplitude at that angle.

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
        points = convert_to_dict(points)

        self.series.instance.send(self.id, 'setGeometry', {'points': points})
        return self

    def dispose(self):
        """Permanently destroy the component."""
        self.series.instance.send(self.id, 'dispose')

    def set_visible(self, visible: bool):
        """Set element visibility.

        Args:
            visible: Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.series.instance.send(self.id, 'setVisible', {'visible': visible})
        return self
