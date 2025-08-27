from __future__ import annotations

import uuid
from lightningchart.series import SeriesWithClear, SeriesWithDrawOrder, Series
from lightningchart.ui.axis import Axis
from lightningchart.utils import convert_color_to_hex


class EllipseSeries(SeriesWithClear, SeriesWithDrawOrder, Series):
    """Series for visualizing ellipses in a 2D space."""

    def __init__(
        self,
        chart,
        x_axis: Axis = None,
        y_axis: Axis = None,
    ):
        Series.__init__(self, chart)
        self.instance.send(
            self.id,
            'addEllipseSeries',
            {
                'chart': self.chart.id,
                'xAxis': x_axis,
                'yAxis': y_axis,
            },
        )

    def add(
        self,
        x: int | float,
        y: int | float,
        radius_x: int | float,
        radius_y: int | float,
    ):
        """Add new figure to the series.

        Args:
            x: x-axis coordinate.
            y: y-axis coordinate.
            radius_x: x-axis radius.
            radius_y: y-axis radius.

        Returns:
            The instance of the class for fluent interface.
        """
        ellipse_figure = EllipseFigure(self, {'x': x, 'y': y, 'radiusX': radius_x, 'radiusY': radius_y})
        return ellipse_figure

    def set_animation_highlight(self, enabled: bool):
        """Set component highlight animations enabled or not.

        Args:
            enabled: Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAnimationHighlight', {'enabled': enabled})
        return self

    def set_auto_scrolling_enabled(self, enabled: bool):
        """Set whether series is taken into account with automatic scrolling and fitting of attached axes.

        Args:
            enabled: Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAutoScrollingEnabled', {'enabled': enabled})
        return self

    def set_highlight_on_hover(self, enabled: bool):
        """Set highlight on mouse hover enabled or disabled.

        Args:
            enabled: Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setHighlightOnHover', {'enabled': enabled})
        return self


class EllipseFigure:
    """Class representing a visual ellipse figure in the EllipseSeries."""

    def __init__(self, series: EllipseSeries, dimensions: dict):
        self.series = series
        self.dimensions = dimensions
        self.instance = series.instance
        self.id = str(uuid.uuid4())
        self.instance.send(
            self.id,
            'addEllipseFigure',
            {'series': self.series.id, 'dimensions': dimensions},
        )

    def set_stroke(self, thickness: int | float, color: any = None):
        """Set Stroke style of the ellipse

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

    def set_visible(self, visible: bool):
        """Set element visibility.

        Args:
            visible: Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setVisible', {'visible': visible})
        return self

    def set_dimensions(
        self,
        x: int | float,
        y: int | float,
        radius_x: int | float,
        radius_y: int | float,
    ):
        """Set new dimensions for figure.

        Args:
            x: x coordinate.
            y: y coordinate.
            radius_x: x radius.
            radius_y: y radius.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(
            self.id,
            'setDimensionsEllipse',
            {'x': x, 'y': y, 'radiusX': radius_x, 'radiusY': radius_y},
        )
        return self

    def set_color(self, color: any):
        """Set a color of the ellipse figure.

        Args:
            color (Color): Color of the band.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setSolidFillStyle', {'color': color})
        return self
