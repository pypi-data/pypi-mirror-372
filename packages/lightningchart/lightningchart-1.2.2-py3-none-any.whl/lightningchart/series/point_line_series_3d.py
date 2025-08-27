from __future__ import annotations

from lightningchart.charts import Chart
from lightningchart.series import (
    SeriesWithAddDataPoints,
    SeriesWithAddDataXYZ,
    SeriesWith3DPoints,
    SeriesWith3DLines,
    SeriesWith3DShading,
    Series,
    ComponentWithLinePaletteColoring,
    SeriesWithClear,
)


class PointLineSeries3D(
    SeriesWithAddDataPoints,
    SeriesWithAddDataXYZ,
    SeriesWith3DPoints,
    SeriesWith3DLines,
    SeriesWith3DShading,
    ComponentWithLinePaletteColoring,
    SeriesWithClear,
):
    """Series for visualizing 3D lines with datapoints."""

    def __init__(
        self,
        chart: Chart,
        render_2d: bool = False,
        individual_lookup_values_enabled: bool = False,
        individual_point_color_enabled: bool = False,
        individual_point_size_axis_enabled: bool = False,
        individual_point_size_enabled: bool = False,
    ):
        Series.__init__(self, chart)
        self.instance.send(
            self.id,
            'pointLineSeries3D',
            {
                'chart': self.chart.id,
                'individualLookupValuesEnabled': individual_lookup_values_enabled,
                'individualPointColorEnabled': individual_point_color_enabled,
                'individualPointSizeAxisEnabled': individual_point_size_axis_enabled,
                'individualPointSizeEnabled': individual_point_size_enabled,
                'type': render_2d,
            },
        )
