from __future__ import annotations

from lightningchart.charts import Chart
from lightningchart.series import (
    SeriesWithAddDataPoints,
    SeriesWithAddDataXYZ,
    SeriesWith3DLines,
    SeriesWith3DShading,
    Series,
    ComponentWithLinePaletteColoring,
    SeriesWithClear,
)


class LineSeries3D(
    SeriesWithAddDataPoints,
    SeriesWithAddDataXYZ,
    SeriesWith3DLines,
    SeriesWith3DShading,
    ComponentWithLinePaletteColoring,
    SeriesWithClear,
):
    """Series for visualizing 3D lines."""

    def __init__(self, chart: Chart):
        Series.__init__(self, chart)
        self.instance.send(
            self.id,
            'lineSeries3D',
            {
                'chart': self.chart.id,
            },
        )
