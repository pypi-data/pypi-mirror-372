from lightningchart import Themes, conf
from lightningchart.series.parallel_coordinate_series import ParallelCoordinateSeries
from lightningchart.charts import ChartWithSeries, TitleMethods, GeneralMethods
from lightningchart.instance import Instance
from lightningchart.ui.axis import GenericAxis
from lightningchart.ui import UserInteractions
from lightningchart.utils import convert_color_to_hex
import uuid


class ParallelCoordinateChart(ChartWithSeries, TitleMethods, GeneralMethods, UserInteractions):
    """Chart for visualizing data in a parallel coordinate system."""

    def __init__(
        self,
        theme: Themes = Themes.Light,
        theme_scale: float = 1.0,
        title: str = None,
        license: str = None,
        license_information: str = None,
        html_text_rendering: bool = False,
    ):
        """Initialize a Parallel Coordinate Chart with a theme and optional title.

        Args:
            theme (Themes): Theme for the chart. Defaults to `Themes.White`.
            title (str, optional): Title of the chart. Defaults to None.
            license (str, optional): License key for the chart. Defaults to None.
            license_information (str, optional): Additional license information. Defaults to None.
            theme_scale: To up or downscale font sizes as well as tick lengths, element paddings, etc. to make font sizes sit in nicely.
            html_text_rendering: Can be enabled for sharper text display where required with drawback of weaker performance.
        """

        instance = Instance()
        super().__init__(instance)
        self.theme = theme
        self.axes = []
        self.series_list = []
        self.instance.send(
            self.id,
            'ParallelCoordinateChart',
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

    def set_axes(self, axes: list):
        """Set axes of the parallel coordinate chart as a list of strings.

        Args:
            axes (list): List of axis names or identifiers.

        Returns:
            The instance of the chart for fluent interface.
        """
        self.axes = axes
        self.instance.send(self.id, 'setAxes', {'axes': axes})
        return self

    def get_axis(self, axis_key: str):
        """Retrieve a specific axis by its name or ID.

        Args:
            axis_key (str): The key or name of the axis.

        Returns:
            The corresponding axis object.

        Raises:
            ValueError: If the axis with the given key is not found.
        """

        if axis_key in self.axes:
            axis_name = axis_key
        else:
            raise ValueError(f"Axis with key '{axis_key}' not found.")

        return ParallelCoordinateAxis(self, axis_name)

    def add_series(self):
        """Add a new data series to the chart.

        Returns:
            The created series instance.
        """
        series = ParallelCoordinateSeries(self)
        self.series_list.append(series)
        return series

    def get_series(self) -> list[ParallelCoordinateSeries]:
        """Get all data series in the chart.

        Returns:
            A list of all series in the chart.
        """
        return self.series_list

    def set_lut(self, axis_key: str, interpolate: bool, steps: list):
        """Configure series coloring by a Value-Color Table (LUT) based on a specific axis.

        Args:
            axis_key (str): The key of the axis for which to apply LUT.
            interpolate (bool): Whether to interpolate between LUT steps.
            steps (list): List of LUT steps, each with a value and color.

        Returns:
            The instance of the chart for fluent interface.
        """
        for step in steps:
            step['color'] = convert_color_to_hex(step['color'])

        lut_config = {'interpolate': interpolate, 'steps': steps}
        self.instance.send(self.id, 'setParallelAxisLUT', {'axisId': axis_key, 'lut': lut_config})
        return self

    def set_spline(self, enabled: bool):
        """Enable or disable spline interpolation for the chart.

        Args:
            enabled (bool): True to enable spline interpolation, False to disable.

        Returns:
            The instance of the chart for fluent interface.
        """
        self.instance.send(self.id, 'setSpline', {'enabled': enabled})
        return self

    def set_series_stroke_thickness(self, thickness: int | float):
        """Set the thickness of series lines.

        Args:
            thickness (int | float): Thickness of the lines in pixels.

        Returns:
            The instance of the chart for fluent interface.
        """
        self.instance.send(self.id, 'setSeriesStrokeThickness', {'thickness': thickness})
        return self

    def set_highlight_on_hover(self, state: bool):
        """Enable or disable highlight on hover for series.

        Args:
            state (bool): True to enable highlight on hover, False to disable.

        Returns:
            The instance of the chart for fluent interface.
        """
        self.instance.send(self.id, 'setSeriesHighlightOnHover', {'state': state})
        return self

    def set_unselected_series_color(self, color: any):
        """Set the color for unselected series.

        Args:
            Color: Color to apply to unselected series.

        Returns:
            The instance of the chart for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setUnselectedSeriesColor', {'color': color})
        return self

    def set_user_interactions(self, interactions=...):
        """Configure user interactions from a set of preset options.

        Args:
            interactions (dict or None):
                - `None`: disable all interactions
                - `{}` or no argument: restore default interactions
                - `dict`: configure specific interactions

        Examples:
            ### Disable all interactions:
            chart.set_user_interactions(None)

            ### Restore default interactions:
            chart.set_user_interactions()
            chart.set_user_interactions({})

            ### Remove select range selector interactions
            chart.set_user_interactions(
                {
                    'rangeSelectors': {
                        'create': {
                            'doubleClickAxis': True,
                        },
                        'dispose': {
                            'doubleClick': True,
                        },
                    },
                }
            )
        """
        return super().set_user_interactions(interactions)


class ParallelCoordinateAxis(GenericAxis):
    def __init__(self, chart, axis_key):
        """Initialize a parallel coordinate axis.

        Args:
            chart (ParallelCoordinateChart): The parent chart.
            axis_key (str): The identifier or name of the axis.
        """
        self.chart = chart
        self.axis_key = axis_key
        self.instance = Instance()
        self.id = str(uuid.uuid4()).split('-')[0]

    def add_range_selector(self):
        """Add a range selector to this axis.

        Returns:
            The created range selector object.
        """
        selector_id = str(uuid.uuid4()).split('-')[0]
        self.chart.instance.send(
            self.chart.id,
            'addRangeSelector',
            {'axisId': self.axis_key, 'selectorId': selector_id},
        )
        return ParallelCoordinateAxisRangeSelector(self.chart, self.axis_key, selector_id)

    def set_title(self, title: str):
        """Set the title for the axis.

        Args:
            title (str): Title text for the axis.

        Returns:
            The instance of the axis for fluent interface.
        """
        self.chart.instance.send(
            self.chart.id,
            'setParallelAxisTitle',
            {'axisId': self.axis_key, 'title': title},
        )
        self.title = title
        return self

    def set_visible(self, visible: bool):
        """Set the visibility of the axis.

        Args:
            visible (bool): True to make the axis visible, False to hide.

        Returns:
            The instance of the axis for fluent interface.
        """
        self.chart.instance.send(
            self.chart.id,
            'setParallelAxisVisibility',
            {'axisId': self.axis_key, 'visible': visible},
        )
        return self

    def get_title(self) -> str:
        """Retrieve the title of the axis.

        Returns:
            str: The title of the axis.
        """
        return self.title

    def set_palette_stroke(self, thickness: int | float, interpolate: bool, steps: list):
        """Set the stroke style of the axis with a palette.

        Args:
            thickness (int | float): Thickness of the stroke in pixels.
            interpolate (bool): Whether to interpolate between palette steps.
            steps (list): List of palette steps, each containing value and color.

        Returns:
            The instance of the axis for fluent interface.
        """
        for step in steps:
            step['color'] = convert_color_to_hex(step['color'])
        self.chart.instance.send(
            self.chart.id,
            'setParallelAxisStrokeStyle',
            {
                'axisId': self.axis_key,
                'thickness': thickness,
                'lut': {'interpolate': interpolate, 'steps': steps},
            },
        )
        return self

    def set_solid_stroke(self, thickness: int | float, color: any = None):
        """Set a solid stroke style for the axis.

        Args:
            thickness (int | float): Thickness of the stroke in pixels.
            color: Solid color for the stroke.

        Returns:
            The instance of the axis for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.chart.instance.send(
            self.chart.id,
            'setSolidStroke',
            {'axisId': self.axis_key, 'thickness': thickness, 'color': color},
        )
        return self

    def set_tick_strategy(self, strategy: str, time_origin: int | float = None, utc: bool = False):
        """Set the tick strategy for the axis.

        Args:
            strategy (str): Tick strategy ("Empty", "Numeric", "DateTime", "Time").
            time_origin (int | float, optional): Time origin for the strategy. Defaults to None.
            utc (bool, optional): Whether to use UTC for DateTime strategy. Defaults to False.

        Returns:
            The instance of the axis for fluent interface.
        """
        strategies = ('Empty', 'Numeric', 'DateTime', 'Time')
        if strategy not in strategies:
            raise ValueError(f"Expected strategy to be one of {strategies}, but got '{strategy}'.")

        self.chart.instance.send(
            self.chart.id,
            'setParellelAxisTickStrategy',
            {
                'strategy': strategy,
                'axisId': self.axis_key,
                'timeOrigin': time_origin,
                'utc': utc,
            },
        )
        return self


class ParallelCoordinateAxisRangeSelector:
    def __init__(self, chart, axis_key, selector_id):
        """Initialize a range selector for a parallel coordinate axis.

        Args:
            chart (ParallelCoordinateChart): The parent chart.
            axis_key (str): The key or name of the axis.
            selector_id (str): Unique identifier for the selector.
        """
        self.chart = chart
        self.axis_key = axis_key
        self.selector_id = selector_id

    def set_interval(self, a: float, b: float, stop_axis_after: bool = False, animate: bool = False):
        """Set the range interval for the selector.

        Args:
            a (float): Start of the interval.
            b (float): End of the interval.
            stop_axis_after (bool, optional): Stop axis after the range. Defaults to False.
            animate (bool, optional): Animate the range update. Defaults to False.

        Returns:
            The instance of the selector for fluent interface.
        """
        self.chart.instance.send(
            self.chart.id,
            'setRangeSelectorInterval',
            {
                'selectorId': self.selector_id,
                'axisId': self.axis_key,
                'start': a,
                'end': b,
                'stop': stop_axis_after,
                'animate': animate,
            },
        )
        return self

    def dispose(self):
        """Remove the range selector permanently.

        Returns:
            The instance of the class for fluent interface.
        """
        self.chart.instance.send(
            self.chart.id,
            'dispose',
            {
                'selectorId': self.selector_id,
            },
        )
        return self


class ParallelCoordinatesChartDashboard(ParallelCoordinateChart):
    """Class for ParallelCoordinatesChart contained in Dashboard."""

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
            'createParallelCoordinateChart',
            {
                'db': dashboard_id,
                'column': column,
                'row': row,
                'colspan': colspan,
                'rowspan': rowspan,
            },
        )
