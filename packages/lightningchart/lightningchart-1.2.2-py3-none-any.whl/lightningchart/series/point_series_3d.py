from __future__ import annotations

from lightningchart.charts import Chart
from lightningchart.series import (
    SeriesWithAddDataPoints,
    Series,
    SeriesWithAddDataXYZ,
    SeriesWith3DPoints,
    SeriesWith3DShading,
    SeriesWithClear,
)


class PointSeries3D(
    SeriesWithAddDataPoints,
    SeriesWithAddDataXYZ,
    SeriesWith3DPoints,
    SeriesWith3DShading,
    SeriesWithClear,
):
    """Series for visualizing 3D datapoints."""

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
            'pointSeries3D',
            {
                'chart': self.chart.id,
                'individualLookupValuesEnabled': individual_lookup_values_enabled,
                'individualPointColorEnabled': individual_point_color_enabled,
                'individualPointSizeAxisEnabled': individual_point_size_axis_enabled,
                'individualPointSizeEnabled': individual_point_size_enabled,
                'pointCloudSeries': render_2d,
            },
        )

    def set_individual_point_color_enabled(self, enabled: bool):
        """
        Enable or disable individual point color attributes for a 3D series.
        When enabled, the JS side will update the point style to use IndividualPointFill;
        otherwise, it will revert to a default SolidFill color.

        Args:
            enabled (bool): True to enable individual point coloring, False to disable.

        Returns:
            self: The instance of the series for fluent interfacing.
        """
        self.instance.send(self.id, 'setIndividualPointColorEnabled3D', {'enabled': enabled})
        return self
