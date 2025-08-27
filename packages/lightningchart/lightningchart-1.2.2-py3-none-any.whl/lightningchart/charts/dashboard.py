from __future__ import annotations

from lightningchart import conf, Themes
from lightningchart.charts import GeneralMethods, Chart
from lightningchart.charts.bar_chart import BarChartDashboard
from lightningchart.charts.chart_3d import Chart3D, Chart3DDashboard
from lightningchart.charts.chart_xy import ChartXY, ChartXYDashboard
from lightningchart.charts.funnel_chart import FunnelChart, FunnelChartDashboard
from lightningchart.charts.gauge_chart import GaugeChart, GaugeChartDashboard
from lightningchart.charts.map_chart import MapChartDashboard
from lightningchart.charts.parallel_coordinate_chart import (
    ParallelCoordinatesChartDashboard,
)
from lightningchart.charts.pie_chart import PieChart, PieChartDashboard
from lightningchart.charts.polar_chart import PolarChartDashboard
from lightningchart.charts.pyramid_chart import PyramidChart, PyramidChartDashboard
from lightningchart.charts.spider_chart import SpiderChartDashboard
from lightningchart.charts.zoom_band_chart import ZoomBandChart
from lightningchart.instance import Instance


class Dashboard(GeneralMethods):
    """Dashboard is a tool for rendering multiple charts in the same view."""

    def __init__(
        self,
        columns: int,
        rows: int,
        theme: Themes = Themes.Light,
        license: str = None,
        license_information: str = None,
        html_text_rendering: bool = False,
    ):
        """Create a dashboard, i.e., a tool for rendering multiple charts in the same view.

        Args:
            columns (int): The amount of columns in the dashboard.
            rows (int): The amount of rows in the dashboard.
            theme (Themes): Theme of the chart.
            license (str): License key.
        """
        instance = Instance()
        Chart.__init__(self, instance)
        self.charts = []
        self.columns = columns
        self.rows = rows
        instance.send(
            self.id,
            'dashboard',
            {
                'columns': columns,
                'rows': rows,
                'theme': theme.value,
                'license': license or conf.LICENSE_KEY,
                'licenseInformation': license_information or conf.LICENSE_INFORMATION,
                'htmlTextRendering': html_text_rendering,
            },
        )

    def ChartXY(
        self,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        title: str = None,
    ) -> ChartXY:
        """Create a XY Chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            title (str): The title of the chart.

        Returns:
            Reference to the XY Chart.
        """
        return ChartXYDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
            title=title,
        )

    def Chart3D(
        self,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        title: str = None,
    ) -> Chart3D:
        """Create a 3D chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            title (str): The title of the chart.

        Returns:
            Reference to the 3D Chart.
        """
        return Chart3DDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
            title=title,
        )

    def ZoomBandChart(
        self,
        chart: ChartXY,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        axis_type: 'str' = 'linear',
        orientation: str = 'x',
        use_shared_value_axis: bool = False,
    ) -> ZoomBandChart:
        """Create a Zoom Band Chart on the dashboard.

        Args:
            chart (ChartXY): Reference to XY Chart which the Zoom Band Chart will use.
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.

        Returns:
            Reference to the Zoom Band Chart.
        """
        return ZoomBandChart(
            instance=self.instance,
            dashboard_id=self.id,
            chart_id=chart.id,
            column_index=column_index,
            column_span=column_span,
            row_index=row_index,
            row_span=row_span,
            axis_type=axis_type,
            orientation=orientation,
            use_shared_value_axis=use_shared_value_axis,
        )

    def PieChart(self, column_index: int, row_index: int, column_span: int = 1, row_span: int = 1, labels_inside_slices: bool = False) -> PieChart:
        """Create a Pie Chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            labels_inside_slices (bool): If true, the labels are inside pie slices. If false, the labels are on the
                sides of the slices.

        Returns:
            Reference to the Pie Chart.
        """
        return PieChartDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
            labelsInsideSlices=labels_inside_slices,
        )

    def GaugeChart(self, column_index: int, row_index: int, column_span: int = 1, row_span: int = 1) -> GaugeChart:
        """Create a Gauge Chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.

        Returns:
            Reference to the Gauge Chart.
        """
        return GaugeChartDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
        )

    def FunnelChart(self, column_index: int, row_index: int, column_span: int = 1, row_span: int = 1, labels_inside: bool = False) -> FunnelChart:
        """Create a Funnel Chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            labels_inside: If True, labels are placed inside slices. If False, labels are on sides (default).

        Returns:
            Reference to the Funnel Chart.
        """
        return FunnelChartDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
            labelsInside=labels_inside,
        )

    def PyramidChart(self, column_index: int, row_index: int, column_span: int = 1, row_span: int = 1, labels_inside: bool = False) -> PyramidChart:
        """Create a Pyramid Chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            labels_inside: If True, labels are placed inside slices. If False, labels are on sides (default).

        Returns:
            Reference to the Pyramid Chart.
        """
        return PyramidChartDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
            labelsInside=labels_inside,
        )

    def PolarChart(self, column_index: int, row_index: int, column_span: int = 1, row_span: int = 1) -> PolarChartDashboard:
        """Create a Polar Chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.

        Returns:
            Reference to the Polar Chart.
        """
        polar_chart = PolarChartDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
        )
        self.charts.append(polar_chart)
        return polar_chart

    def BarChart(
        self,
        column_index: int,
        row_index: int,
        column_span: int = 1,
        row_span: int = 1,
        vertical: bool = True,
        axis_type: str = 'linear',
        axis_base: int = 10,
    ):
        """Create a Bar Chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            vertical (bool): If true, bars are aligned vertically. If false, bars are aligned horizontally.
            axis_type (str): "linear" | "logarithmic"
            axis_base (int): Specification of Logarithmic Base number (e.g. 10, 2, natural log).

        Returns:
            Reference to the Bar Chart.
        """
        return BarChartDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
            vertical=vertical,
            axis_type=axis_type,
            axis_base=axis_base,
        )

    def SpiderChart(self, column_index: int, row_index: int, column_span: int = 1, row_span: int = 1):
        """Create a Spider Chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.

        Returns:
            Reference to the Spider Chart
        """
        return SpiderChartDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
        )

    def MapChart(self, column_index: int, row_index: int, column_span: int = 1, row_span: int = 1, map_type: str='World'):
        """Create a Map Chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.
            map_type (str): "Africa" | "Asia" | "Australia" | "Canada" | "Europe" | "NorthAmerica" | "SouthAmerica" | "USA" | "World" |

        Returns:
            Reference to the Map Chart
        """
        return MapChartDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
            map_type=map_type,
        )

    def ParallelCoordinatesChart(self, column_index: int, row_index: int, column_span: int = 1, row_span: int = 1):
        """Create a Parallel Coordinates Chart on the dashboard.

        Args:
            column_index (int): Column index of the dashboard where the chart will be located.
            row_index (int): Row index of the dashboard where the chart will be located.
            column_span (int): How many columns the chart will take (X width). Default = 1.
            row_span (int): How many rows the chart will take (Y height). Default = 1.

        Returns:
            Reference to the Parallel Coordinates Chart
        """
        return ParallelCoordinatesChartDashboard(
            instance=self.instance,
            dashboard_id=self.id,
            column=column_index,
            row=row_index,
            colspan=column_span,
            rowspan=row_span,
        )
