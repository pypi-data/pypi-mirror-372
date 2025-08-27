from __future__ import annotations

from lightningchart.charts import Chart
from lightningchart.ui.axis import Axis
from lightningchart.series import (
    ComponentWithPaletteColoring,
    SeriesWithWireframe,
    SeriesWithPixelInterpolation,
    SeriesWithDataCleaning,
    SeriesWithAddIntensityValues,
    Series,
    SeriesWithClear,
    SeriesWithDrawOrder,
)


class HeatmapScrollingGridSeries(
    ComponentWithPaletteColoring,
    SeriesWithWireframe,
    SeriesWithPixelInterpolation,
    SeriesWithDataCleaning,
    SeriesWithAddIntensityValues,
    SeriesWithClear,
    SeriesWithDrawOrder,
    Series,
):
    """Series for visualizing 2D heatmap data in a grid with automatic scrolling features."""

    def __init__(
        self,
        chart: Chart,
        resolution: int,
        scroll_dimension: str = 'columns',
        x_axis: Axis = None,
        y_axis: Axis = None,
    ):
        Series.__init__(self, chart)
        self.instance.send(
            self.id,
            'heatmapScrollingGridSeries',
            {
                'chart': self.chart.id,
                'scrollDimension': scroll_dimension,
                'resolution': resolution,
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
