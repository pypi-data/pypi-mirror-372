from __future__ import annotations

from lightningchart.charts import Chart
from lightningchart.ui.axis import Axis
from lightningchart.series import (
    SeriesWithAddDataPoints,
    SeriesWithAddDataXY,
    SeriesWith2DPoints,
    SeriesWithIndividualPoint,
    Series,
    PointLineAreaSeries,
    PointSeriesStyle,
    SeriesWithClear,
    SeriesWithDrawOrder,
)


class PointSeries(
    SeriesWithAddDataPoints,
    SeriesWithAddDataXY,
    SeriesWith2DPoints,
    SeriesWithIndividualPoint,
    PointLineAreaSeries,
    PointSeriesStyle,
    SeriesWithClear,
    SeriesWithDrawOrder,
):
    """Series for visualizing 2D datapoints."""

    def __init__(
        self,
        chart: Chart,
        data_pattern: str = None,
        colors: bool = None,
        lookup_values: bool = None,
        ids: bool = None,
        sizes: bool = None,
        rotations: bool = None,
        auto_sorting_enabled: bool = None,
        allow_data_grouping: bool = None,
        automatic_color_index: bool = None,
        includes_nan: bool = None,
        x_axis: Axis = None,
        y_axis: Axis = None,
    ):
        Series.__init__(self, chart)
        self.instance.send(
            self.id,
            'pointSeries2D',
            {
                'chart': self.chart.id,
                'allowDataGrouping': allow_data_grouping,
                'autoSortingEnabled': auto_sorting_enabled,
                'automaticColorIndex': automatic_color_index,
                'colors': colors,
                'dataPattern': data_pattern,
                'ids': ids,
                'includesNaN': includes_nan,
                'lookupValues': lookup_values,
                'rotations': rotations,
                'sizes': sizes,
                'xAxis': x_axis,
                'yAxis': y_axis,
            },
        )
