from __future__ import annotations

from lightningchart import conf, Themes
from lightningchart.charts import GeneralMethods, TitleMethods
from lightningchart.instance import Instance
from lightningchart.series.polar_area_series import PolarAreaSeries
from lightningchart.series.polar_line_series import PolarLineSeries
from lightningchart.series.polar_point_line_series import PolarPointLineSeries
from lightningchart.series.polar_point_series import PolarPointSeries
from lightningchart.series.polar_heatmap_series import PolarHeatmapSeries
from lightningchart.series.polar_polygon_series import PolarPolygonSeries
from lightningchart.ui.polar_sector import PolarSector
from lightningchart.ui.polar_axis_amplitude import PolarAxisAmplitude
from lightningchart.ui.polar_axis_radial import PolarAxisRadial


class PolarChart(GeneralMethods, TitleMethods):
    """Chart for visualizing data in a polar coordinate system."""

    def __init__(
        self,
        theme: Themes = Themes.Light,
        theme_scale: float = 1.0,
        title: str = None,
        license: str = None,
        license_information: str = None,
        html_text_rendering: bool = False,
    ):
        """Create a polar chart.

        Args:
            theme (Themes): Theme of the chart.
            title (str): Title of the chart.
            theme_scale: To up or downscale font sizes as well as tick lengths, element paddings, etc. to make font sizes sit in nicely.
            html_text_rendering: Can be enabled for sharper text display where required with drawback of weaker performance.
        """
        instance = Instance()
        super().__init__(instance)
        self.series_list = []
        self.instance.send(
            self.id,
            'polarChart',
            {
                'theme': theme.value,
                'scaleTheme': theme_scale,
                'license': license or conf.LICENSE_KEY,
                'licenseInformation': license_information or conf.LICENSE_INFORMATION,
                'htmlTextRendering': html_text_rendering,
            },
        )
        if title:
            self.set_title(title)

    def add_area_series(self):
        """Add an Area series to the PolarChart.

        Returns:
            PolarAreaSeries instance.
        """
        area_series = PolarAreaSeries(self)
        self.series_list.append(area_series)
        return area_series

    def add_point_series(self):
        """Add a Point series to the PolarChart.

        Returns:
            PolarPointSeries instance.
        """
        point_series = PolarPointSeries(self)
        self.series_list.append(point_series)
        return point_series

    def add_line_series(self):
        """Add a Line series to the PolarChart.

        Returns:
            PolarLineSeries instance.
        """
        line_series = PolarLineSeries(self)
        self.series_list.append(line_series)
        return line_series

    def add_point_line_series(self):
        """Add a Point Line series to the PolarChart.

        Returns:
            PolarPointLineSeries instance.
        """
        series = PolarPointLineSeries(self)
        self.series_list.append(series)
        return series

    def add_polygon_series(self):
        """Add a Polygon series to the PolarChart.

        Returns:
            PolarPolygonSeries instance.
        """
        polygon_series = PolarPolygonSeries(self)
        self.series_list.append(polygon_series)
        return polygon_series

    def add_heatmap_series(
        self,
        sectors: int,
        annuli: int,
        data_order: str = 'annuli',
        amplitude_start: int | float = 0,
        amplitude_end: int | float = 1,
        amplitude_step: int | float = 0,
    ):
        """Add a Series for visualizing a Polar Heatmap with a static sector and annuli count.

        Args:
            sectors: Amount of unique data samples along Radial Axis.
            annuli: Amount of unique data samples along Amplitude Axis.
            data_order: "annuli" | "sectors" - Select order of data.
            amplitude_start: Amplitude value where Polar Heatmap originates at.
            amplitude_end: Amplitude value where Polar Heatmap ends at.
            amplitude_step: Amplitude step between each ring (annuli) of the Polar Heatmap.

        Returns:
            PolarHeatmapSeries instance.
        """
        heatmap_series = PolarHeatmapSeries(
            chart=self,
            sectors=sectors,
            annuli=annuli,
            data_order=data_order,
            amplitude_start=amplitude_start,
            amplitude_end=amplitude_end,
            amplitude_step=amplitude_step,
        )
        self.series_list.append(heatmap_series)
        return heatmap_series

    def get_amplitude_axis(self):
        """Get PolarAxisAmplitude object that represents the PolarCharts amplitude dimension,
        which is depicted as a distance away from the Charts center.

        Returns:
            PolarAxisAmplitude instance.
        """
        amplitude_axis = PolarAxisAmplitude(self)
        return amplitude_axis

    def add_sector(self):
        """Add a Sector highlighter to the PolarChart.

        Returns:
            PolarSector instance.
        """
        sector = PolarSector(self)
        return sector

    def get_radial_axis(self):
        """Get PolarAxisRadial object that represents the PolarCharts radial dimension,
        which is depicted as an angle on the Charts center.

        Returns:
            PolarAxisRadial instance.
        """
        radial_axis = PolarAxisRadial(self)
        return radial_axis


class PolarChartDashboard(PolarChart):
    """Class for PolarChart contained in Dashboard."""

    def __init__(
        self,
        instance: Instance,
        dashboard_id: str,
        column: int,
        row: int,
        colspan: int,
        rowspan: int,
    ):
        super().__init__()
        self.instance = instance

        self.instance.send(
            self.id,
            'createPolarChart',
            {
                'db': dashboard_id,
                'column': column,
                'row': row,
                'colspan': colspan,
                'rowspan': rowspan,
            },
        )
