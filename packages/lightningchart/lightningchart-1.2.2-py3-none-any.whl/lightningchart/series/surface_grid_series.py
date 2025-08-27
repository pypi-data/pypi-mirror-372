from __future__ import annotations

from lightningchart.charts import Chart
from lightningchart.series import (
    ComponentWithPaletteColoring,
    SeriesWithInvalidateIntensity,
    SeriesWithWireframe,
    SeriesWithInvalidateHeight,
    SeriesWithIntensityInterpolation,
    SeriesWithCull,
    SeriesWith3DShading,
    Series,
    SeriesWithClear,
)


class SurfaceGridSeries(
    ComponentWithPaletteColoring,
    SeriesWithInvalidateIntensity,
    SeriesWithWireframe,
    SeriesWithInvalidateHeight,
    SeriesWithIntensityInterpolation,
    SeriesWithCull,
    SeriesWith3DShading,
    SeriesWithClear,
):
    """Series for visualizing 3D surface data in a grid."""

    def __init__(
        self,
        chart: Chart,
        columns: int,
        rows: int,
        data_order: str = 'columns',
    ):
        Series.__init__(self, chart)
        self.columns = columns
        self.rows = rows
        self.instance.send(
            self.id,
            'surfaceGridSeries',
            {
                'chart': self.chart.id,
                'columns': columns,
                'rows': rows,
                'dataOrder': data_order,
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

    def set_end(self, x: int | float, z: int | float):
        """Set end coordinate of surface on its X and Z axis where the last surface sample will be positioned.

        Args:
            x: x-coordinate.
            z: z-coordinate.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setEndXZ', {'x': x, 'z': z})
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
