from __future__ import annotations

from lightningchart.charts import Chart
from lightningchart.ui.axis import Axis
from lightningchart.series import (
    ComponentWithPaletteColoring,
    SeriesWithInvalidateIntensity,
    SeriesWithIntensityInterpolation,
    SeriesWithWireframe,
    Series,
    SeriesWithClear,
    SeriesWithDrawOrder,
)


class HeatmapGridSeries(
    ComponentWithPaletteColoring,
    SeriesWithInvalidateIntensity,
    SeriesWithIntensityInterpolation,
    SeriesWithWireframe,
    SeriesWithClear,
    SeriesWithDrawOrder,
    Series,
):
    """Series for visualizing 2D heatmap data in a grid."""

    def __init__(
        self,
        chart: Chart,
        columns: int,
        rows: int,
        data_order: str = 'columns',
        x_axis: Axis = None,
        y_axis: Axis = None,
    ):
        Series.__init__(self, chart)
        self.instance.send(
            self.id,
            'heatmapGridSeries',
            {
                'chart': self.chart.id,
                'columns': columns,
                'rows': rows,
                'dataOrder': data_order,
                'xAxis': x_axis,
                'yAxis': y_axis,
            },
        )

    def set_start(self, x: int | float, y: int | float):
        """Set start coordinate of Heatmap on its X and Y axis where the first heatmap sample will be positioned

        Args:
            x: x-coordinate.
            y: y-coordinate.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setStartXY', {'x': x, 'y': y})
        return self

    def set_end(self, x: int | float, y: int | float):
        """Set end coordinate of Heatmap on its X and Y axis where the last heatmap sample will be positioned.

        Args:
            x: x-coordinate.
            y: y-coordinate.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setEndXY', {'x': x, 'y': y})
        return self

    def set_step(self, x: int | float, y: int | float):
        """Set Step between each consecutive heatmap value on the X and Y Axes.

        Args:
            x: x-coordinate.
            y: y-coordinate.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setStepXY', {'x': x, 'y': y})
        return self
