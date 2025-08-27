from __future__ import annotations

from lightningchart.charts import Chart
from lightningchart.series import (
    SeriesWithInvalidateData,
    SeriesWith3DShading,
    ComponentWithPaletteColoring,
    Series,
)


class BoxSeries3D(SeriesWithInvalidateData, SeriesWith3DShading, ComponentWithPaletteColoring):
    """Series for visualizing 3D boxes."""

    def __init__(self, chart: Chart):
        Series.__init__(self, chart)
        self.instance.send(self.id, 'boxSeries3D', {'chart': self.chart.id})

    def set_rounded_edges(self, roundness: int | float | None):
        """Set rounded edges of Boxes.
        NOTE: Rounded edges result in increased geometry precision, which in turn uses more rendering resources.

        Args:
            roundness: Either a number in range [0, 1] describing the amount of rounding
                or None to disable rounded edges.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setRoundedEdges', {'roundness': roundness})
        return self
