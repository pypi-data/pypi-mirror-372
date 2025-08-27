from __future__ import annotations

from lightningchart.charts import Chart
from lightningchart.series import (
    ComponentWithPaletteColoring,
    SeriesWithWireframe,
    SeriesWithIntensityInterpolation,
    SeriesWithCull,
    SeriesWithAddValues,
    SeriesWith3DShading,
    Series,
    SeriesWithClear,
)


class SurfaceScrollingGridSeries(
    ComponentWithPaletteColoring,
    SeriesWithWireframe,
    SeriesWithIntensityInterpolation,
    SeriesWithCull,
    SeriesWithAddValues,
    SeriesWith3DShading,
    SeriesWithClear,
):
    """Series for visualizing 3D surface data in a grid with automatic scrolling features."""

    def __init__(
        self,
        chart: Chart,
        columns: int,
        rows: int,
        scroll_dimension: str = 'columns',
    ):
        Series.__init__(self, chart)
        self.instance.send(
            self.id,
            'surfaceScrollingGridSeries',
            {
                'chart': self.chart.id,
                'columns': columns,
                'rows': rows,
                'scrollDimension': scroll_dimension,
            },
        )

    def set_start(self, x: int | float, z: int | float):
        """Set start coordinate of surface on its X and Z axis where the first surface sample will be positioned

        Args:
            x: x-coordinate.
            z: z-coordinate.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setStartXZ', {'x': x, 'z': z})
        return self

    def set_step(self, x: int | float, z: int | float):
        """Set Step between each consecutive surface value on the X and Z Axes.

        Args:
            x: x-coordinate.
            z: z-coordinate.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setStepXZ', {'x': x, 'z': z})
        return self
