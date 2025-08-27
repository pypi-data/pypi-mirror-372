from __future__ import annotations

from lightningchart.charts import Chart
from lightningchart.ui.axis import Axis
from lightningchart.series import (
    SeriesWithAddDataPoints,
    SeriesWithAddDataXY,
    SeriesWith2DPoints,
    SeriesWith2DLines,
    SeriesWithIndividualPoint,
    Series,
    PointLineAreaSeries,
    PointSeriesStyle,
    SeriesWithClear,
    SeriesWithDrawOrder,
)


class PointLineSeries(
    SeriesWithAddDataPoints,
    SeriesWithAddDataXY,
    SeriesWith2DPoints,
    SeriesWith2DLines,
    SeriesWithIndividualPoint,
    PointLineAreaSeries,
    PointSeriesStyle,
    SeriesWithClear,
    SeriesWithDrawOrder,
):
    """Series for visualizing 2D lines with datapoints."""

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
        allow_data_grouping=None,
        automatic_color_index=None,
        includes_nan=None,
        x_axis: Axis = None,
        y_axis: Axis = None,
    ):
        Series.__init__(self, chart)
        self.instance.send(
            self.id,
            'pointLineSeries2D',
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
