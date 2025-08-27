from __future__ import annotations
import uuid

from lightningchart import conf, Themes, charts
from lightningchart.charts import GeneralMethods, TitleMethods, Chart
from lightningchart.instance import Instance
from lightningchart.series import Series
from lightningchart.ui.axis import SpiderChartAxis
from lightningchart.utils import convert_to_dict, convert_color_to_hex


class SpiderChart(GeneralMethods, TitleMethods, SpiderChartAxis):
    def __init__(
        self,
        theme: Themes = Themes.Light,
        theme_scale: float = 1.0,
        title: str = None,
        license: str = None,
        license_information: str = None,
        html_text_rendering: bool = False,
    ):
        """Chart for visualizing data in a radial form as dissected by named axes.

        Args:
            theme (Themes): Overall theme of the chart.
            title (str): Title of the chart.
            license (str): License key.
            theme_scale: To up or downscale font sizes as well as tick lengths, element paddings, etc. to make font sizes sit in nicely.
            html_text_rendering: Can be enabled for sharper text display where required with drawback of weaker performance.
        """

        instance = Instance()
        Chart.__init__(self, instance)
        self.instance.send(
            self.id,
            'spiderChart',
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

    def add_series(self):
        """Adds a new SpiderSeries to the SpiderChart.

        Returns:
            SpiderSeries instance.
        """
        return SpiderSeries(self)

    def set_web_mode(self, mode: str = 'circle'):
        """Set mode of SpiderCharts web and background.

        Args:
            mode: "circle" | "normal"

        Returns:
            The instance of the class for fluent interface.
        """
        mode = 1 if mode == 'circle' else 0
        self.instance.send(self.id, 'setWebMode', {'mode': mode})
        return self

    def set_series_background_effect(self, enabled: bool = True):
        """Set theme effect enabled on component or disabled.

        Args:
            enabled (bool): Theme effect enabled.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setSeriesBackgroundEffect', {'enabled': enabled})
        return self

    def set_web_count(self, count: int):
        """Set count of 'webs' displayed.

        Args:
            count (int): Count of web lines.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setWebCount', {'count': count})
        return self

    def set_web_style(self, thickness: int | float, color: any = None):
        """Set style of spider charts webs as LineStyle.

        Args:
            thickness (int | float): Thickness of the web lines.
            color (Color): Color of the web.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setWebStyle', {'thickness': thickness, 'color': color})
        return self


class SpiderChartDashboard(SpiderChart):
    def __init__(
        self,
        instance: Instance,
        dashboard_id: str,
        column: int,
        row: int,
        colspan: int,
        rowspan: int,
    ):
        Chart.__init__(self, instance)
        self.instance.send(
            self.id,
            'createSpiderChart',
            {
                'db': dashboard_id,
                'column': column,
                'row': row,
                'colspan': colspan,
                'rowspan': rowspan,
            },
        )


class SpiderSeries(Series):
    def __init__(self, chart: charts.Chart):
        self.chart = chart
        self.instance = chart.instance
        self.id = str(uuid.uuid4()).split('-')[0]
        self.instance.send(self.id, 'addSpiderSeries', {'chart': self.chart.id})

    def add_points(self, points: list[dict[str, int | float]]):
        """Adds an arbitrary amount of SpiderPoints to the Series.

        Args:
            points (str): List of SpiderPoints as {'axis': string, 'value': number}

        Returns:
            The instance of the class for fluent interface.
        """
        points = convert_to_dict(points)

        self.instance.send(self.id, 'addPoints', {'points': points})
        return self

    def set_fill_color(self, color: any):
        """Set color of the polygon that represents the shape of the Series.

        Args:
            color (Color): Color of the polygon.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setSolidFillStyle', {'color': color})
        return self

    def set_point_color(self, color: any):
        """Set color of the series points.

        Args:
            color (Color): Color of the points.

        Returns:
            The instance of the class for fluent interface.
        """

        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setPointFillStyle', {'color': color})
        return self

    def set_line_color(self, color: any):
        """Set the series polygon line color.

        Args:
            color (Color): Color of the lines.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setLineFillStyle', {'color': color})
        return self

    def set_line_thickness(self, thickness: int):
        """Set the series polygon line thickness.

        Args:
            thickness (int): Thickness of the lines.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setLineThickness', {'width': thickness})
        return self

    def set_point_size(self, size: int | float):
        """Set size of point in pixels

        Args:
            size (int | float): Size of point in pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setPoint2DSize', {'size': size})
        return self
