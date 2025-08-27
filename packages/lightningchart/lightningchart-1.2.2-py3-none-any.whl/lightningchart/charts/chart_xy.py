from __future__ import annotations

from lightningchart import conf, Themes
from lightningchart.charts import (
    GeneralMethods,
    TitleMethods,
    ChartWithXYAxis,
    ChartWithSeries,
    BackgroundChartStyle,
)
from lightningchart.instance import Instance
from lightningchart.series.point_series import PointSeries
from lightningchart.series.line_series import LineSeries
from lightningchart.series.point_line_series import PointLineSeries
from lightningchart.series.spline_series import SplineSeries
from lightningchart.series.area_series import (
    AreaSeries,
    AreaSeriesPositive,
    AreaSeriesNegative,
    AreaSeriesBipolar,
)
from lightningchart.series.area_range_series import AreaRangeSeries
from lightningchart.series.step_series import StepSeries
from lightningchart.series.heatmap_grid_series import HeatmapGridSeries
from lightningchart.series.heatmap_scrolling_grid_series import (
    HeatmapScrollingGridSeries,
)
from lightningchart.series.box_series import BoxSeries
from lightningchart.series.ellipse_series import EllipseSeries
from lightningchart.series.rectangle_series import RectangleSeries
from lightningchart.series.polygon_series import PolygonSeries
from lightningchart.series.segment_series import SegmentSeries
from lightningchart.ui.axis import Axis, UserInteractions


def get_axis_id(x_axis: Axis = None, y_axis: Axis = None):
    x_id = None
    y_id = None
    if x_axis:
        x_id = x_axis.id
    if y_axis:
        y_id = y_axis.id
    return x_id, y_id


class ChartXY(
    GeneralMethods,
    TitleMethods,
    ChartWithXYAxis,
    ChartWithSeries,
    BackgroundChartStyle,
    UserInteractions,
):
    """Chart type for visualizing data between two dimensions, X and Y."""

    def __init__(
        self,
        theme: Themes = Themes.Light,
        theme_scale: float = 1.0,
        title: str = None,
        license: str = None,
        license_information: str = None,
        html_text_rendering: bool = False,
    ):
        """Create a XY Chart.

        Args:
            theme (Themes): Theme of the chart.
            title (str): A title for the chart.
            license (str): License key.
            theme_scale: To up or downscale font sizes as well as tick lengths, element paddings, etc. to make font sizes sit in nicely.
            html_text_rendering: Can be enabled for sharper text display where required with drawback of weaker performance.

        Returns:
            Reference to XY Chart class.
        """
        instance = Instance()
        ChartWithSeries.__init__(self, instance)
        self.instance.send(
            self.id,
            'chartXY',
            {
                'theme': theme.value,
                'scaleTheme': theme_scale,
                'license': license or conf.LICENSE_KEY,
                'licenseInformation': license_information or conf.LICENSE_INFORMATION,
                'htmlTextRendering': html_text_rendering,
            },
        )
        if title:
            self.instance.send(self.id, 'setTitle', {'title': title})
        ChartWithXYAxis.__init__(self)

    def set_title_position(self, position: str = 'center-top'):
        """Set position of XY Chart title.

        Args:
            position (str): "right-top" | "left-top" | "right-bottom" | "left-bottom" | "center-top" |
                "center-bottom" | "series-center-top" | "series-right-top" | "series-left-top" |
                "series-center-bottom" | "series-right-bottom" | "series-left-bottom"

        Returns:
            The instance of the class for fluent interface.
        """
        title_positions = (
            'right-top',
            'left-top',
            'right-bottom',
            'left-bottom',
            'center-top',
            'center-bottom',
            'series-center-top',
            'series-right-top',
            'series-left-top',
            'series-center-bottom',
            'series-right-bottom',
            'series-left-bottom',
        )
        if position not in title_positions:
            raise ValueError(f"Expected position to be one of {title_positions}, but got '{position}'.")

        self.instance.send(self.id, 'setTitlePosition', {'position': position})
        return self

    def add_x_axis(
        self,
        stack_index: int = None,
        parallel_index: int = None,
        opposite: bool = False,
        axis_type: str = None,
        base: int = None,
    ) -> Axis:
        """Add a new X Axis to the Chart.

        Args:
            stack_index (int): Axis index in same plane as the Axis direction.
            parallel_index (int): Axis index in direction parallel to axis.
            opposite (bool): Specify Axis position in chart. Default is bottom for X Axes, and left for Y Axes.
                Setting to true will result in the opposite side (top for X Axes, right for Y Axes).
            axis_type (str): "linear" | "linear-highPrecision" | "logarithmic"
            base (int): Specification of Logarithmic Base number (e.g. 10, 2, natural log). Defaults to 10 if omitted.
        Returns:
            Reference to Axis class.
        """
        return Axis(self, 'x', stack_index, parallel_index, opposite, axis_type, base)

    def add_y_axis(
        self,
        stack_index: int = None,
        parallel_index: int = None,
        opposite: bool = None,
        axis_type: str = None,
        base: int = None,
    ) -> Axis:
        """Add a new Y Axis to the Chart.

        Args:
            stack_index (int): Axis index in same plane as the Axis direction.
            parallel_index (int): Axis index in direction parallel to axis.
            opposite (bool): Specify Axis position in chart. Default is bottom for X Axes, and left for Y Axes.
                Setting to true will result in the opposite side (top for X Axes, right for Y Axes).
            axis_type (str): "linear" | "linear-highPrecision" | "logarithmic"
            base (int): Specification of Logarithmic Base number (e.g. 10, 2, natural log). Defaults to 10 if omitted.
        Returns:
            Reference to Axis class.
        """
        return Axis(self, 'y', stack_index, parallel_index, opposite, axis_type, base)

    def set_cursor_mode(self, mode: str):
        """Set chart Cursor behavior.

        Args:
            mode (str): "disabled" | "show-all" | "show-all-interpolated" | "show-nearest" |
                "show-nearest-interpolated" | "show-pointed" | "show-pointed-interpolated"

        Returns:
            The instance of the class for fluent interface.
        """
        cursor_modes = (
            'disabled',
            'show-all',
            'show-all-interpolated',
            'show-nearest',
            'show-nearest-interpolated',
            'show-pointed',
            'show-pointed-interpolated',
        )
        if mode not in cursor_modes:
            raise ValueError(f"Expected mode to be one of {cursor_modes}, but got '{mode}'.")

        self.instance.send(self.id, 'setCursorMode', {'mode': mode})
        return self

    def add_point_series(
        self,
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
    ) -> PointSeries:
        """Method for adding a new PointSeries to the chart. This series type visualizes a list of Points
        (pair of X and Y coordinates), with configurable markers over each coordinate.

        Args:
            data_pattern (str): "ProgressiveX" | "ProgressiveY" | "RegressiveX" | "RegressiveY" – For best practices,
                the data pattern should ALWAYS be specified, even if there is no pattern to data (scatter data).
            colors (bool): If true, the DataSetXY should allocate for Color property to be included for every sample.
                This can be used to adjust data visualization to use per sample colors. Defaults to false.
            lookup_values (bool): Flag that can be used to enable data points value property on top
                of x and y. Disabled by default.
            ids (bool): If true, user supplied ID property is allocated to be included for every sample.
                Defaults to false.
            sizes (bool): If true, user supplied individual point size properties are allocated. This means that points
                can have individual sizes,rather than each point having same size. Defaults to false.
            rotations (bool): If true, user supplied individual point rotation properties are allocated.
                This means that points can have individual rotations, rather than each point having same rotation.
                Defaults to false.
            auto_sorting_enabled (bool): Controls whether automatic sorting of data according to active data_pattern is
                enabled or disabled. If data_pattern is any kind of progressive pattern, then input data can be
                automatically sorted to remain in that progressive order. This can be useful when data is arriving in
                the application asynchronously, and it can't be guaranteed that it arrives in the correct order.
                Please note that auto sorting only sorts by BATCH, not by SAMPLE. For example, if you supply batches of
                for example 10 samples at a time, auto sorting is capable of identifying the scenario where a newer
                batch arrives before one that should be displayed first. However, auto sorting is not capable of sorting
                any samples that are in wrong order within a BATCH. This is intentional due to effects on performance,
                and since its not a realistic need scenario. Defaults to true.
            allow_data_grouping: Optional flag that can be used to disable automatic grouping of progressive data
                that is packed very tightly together.
            automatic_color_index: Optional index to use for automatic coloring of series.
            includes_nan: Optional flag that can be used to inform that data set will not include NaN values.
                By default, it is assumed that the data provided might include NaN values.
                This results in extra processing to properly handle NaN values.
            x_axis (Axis): Optional non-default X Axis to attach series to.
            y_axis (Axis): Optional non-default Y Axis to attach series to.

        Returns:
            Reference to Point Series class.
        """
        x_axis, y_axis = get_axis_id(x_axis, y_axis)
        series = PointSeries(
            chart=self,
            data_pattern=data_pattern,
            colors=colors,
            lookup_values=lookup_values,
            ids=ids,
            sizes=sizes,
            rotations=rotations,
            allow_data_grouping=allow_data_grouping,
            automatic_color_index=automatic_color_index,
            auto_sorting_enabled=auto_sorting_enabled,
            includes_nan=includes_nan,
            x_axis=x_axis,
            y_axis=y_axis,
        )
        self.series_list.append(series)
        return series

    def add_line_series(
        self,
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
    ) -> LineSeries:
        """Method for adding a new LineSeries to the chart. This series type visualizes a list of Points
        (pair of X and Y coordinates), with a continuous stroke.

        Args:
            data_pattern (str): "ProgressiveX" | "ProgressiveY" | "RegressiveX" | "RegressiveY" – For best practices,
                the data pattern should ALWAYS be specified, even if there is no pattern to data (scatter data).
            colors (bool): If true, the DataSetXY should allocate for Color property to be included for every sample.
                This can be used to adjust data visualization to use per sample colors. Defaults to false.
            lookup_values (bool): Flag that can be used to enable data points value property on top
                of x and y. Disabled by default.
            ids (bool): If true, user supplied ID property is allocated to be included for every sample.
                Defaults to false.
            sizes (bool): If true, user supplied individual point size properties are allocated. This means that points
                can have individual sizes,rather than each point having same size. Defaults to false.
            rotations (bool): If true, user supplied individual point rotation properties are allocated.
                This means that points can have individual rotations, rather than each point having same rotation.
                Defaults to false.
            auto_sorting_enabled (bool): Controls whether automatic sorting of data according to active data_pattern is
                enabled or disabled. If data_pattern is any kind of progressive pattern, then input data can be
                automatically sorted to remain in that progressive order. This can be useful when data is arriving in
                the application asynchronously, and it can't be guaranteed that it arrives in the correct order.
                Please note that auto sorting only sorts by BATCH, not by SAMPLE. For example, if you supply batches of
                for example 10 samples at a time, auto sorting is capable of identifying the scenario where a newer
                batch arrives before one that should be displayed first. However, auto sorting is not capable of sorting
                any samples that are in wrong order within a BATCH. This is intentional due to effects on performance,
                and since its not a realistic need scenario. Defaults to true.
            allow_data_grouping: Optional flag that can be used to disable automatic grouping of progressive data
                that is packed very tightly together.
            automatic_color_index: Optional index to use for automatic coloring of series.
            includes_nan: Optional flag that can be used to inform that data set will not include NaN values.
                By default, it is assumed that the data provided might include NaN values.
                This results in extra processing to properly handle NaN values.
            x_axis (Axis): Optional non-default X Axis to attach series to.
            y_axis (Axis): Optional non-default Y Axis to attach series to.

        Returns:
            Reference to Line Series class.
        """
        x_axis, y_axis = get_axis_id(x_axis, y_axis)
        series = LineSeries(
            chart=self,
            data_pattern=data_pattern,
            colors=colors,
            lookup_values=lookup_values,
            ids=ids,
            sizes=sizes,
            rotations=rotations,
            allow_data_grouping=allow_data_grouping,
            automatic_color_index=automatic_color_index,
            auto_sorting_enabled=auto_sorting_enabled,
            includes_nan=includes_nan,
            x_axis=x_axis,
            y_axis=y_axis,
        )
        self.series_list.append(series)
        return series

    def add_point_line_series(
        self,
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
    ) -> PointLineSeries:
        """Method for adding a new PointLineSeries to the chart. This series type visualizes a list of Points
        (pair of X and Y coordinates), with a continuous stroke and configurable markers over each coordinate.

        Args:
            data_pattern (str): "ProgressiveX" | "ProgressiveY" | "RegressiveX" | "RegressiveY" – For best practices,
                the data pattern should ALWAYS be specified, even if there is no pattern to data (scatter data).
            colors (bool): If true, the DataSetXY should allocate for Color property to be included for every sample.
                This can be used to adjust data visualization to use per sample colors. Defaults to false.
            lookup_values (bool): Flag that can be used to enable data points value property on top
                of x and y. Disabled by default.
            ids (bool): If true, user supplied ID property is allocated to be included for every sample.
                Defaults to false.
            sizes (bool): If true, user supplied individual point size properties are allocated. This means that points
                can have individual sizes,rather than each point having same size. Defaults to false.
            rotations (bool): If true, user supplied individual point rotation properties are allocated.
                This means that points can have individual rotations, rather than each point having same rotation.
                Defaults to false.
            auto_sorting_enabled (bool): Controls whether automatic sorting of data according to active data_pattern is
                enabled or disabled. If data_pattern is any kind of progressive pattern, then input data can be
                automatically sorted to remain in that progressive order. This can be useful when data is arriving in
                the application asynchronously, and it can't be guaranteed that it arrives in the correct order.
                Please note that auto sorting only sorts by BATCH, not by SAMPLE. For example, if you supply batches of
                for example 10 samples at a time, auto sorting is capable of identifying the scenario where a newer
                batch arrives before one that should be displayed first. However, auto sorting is not capable of sorting
                any samples that are in wrong order within a BATCH. This is intentional due to effects on performance,
                and since its not a realistic need scenario. Defaults to true.
            allow_data_grouping: Optional flag that can be used to disable automatic grouping of progressive data
                that is packed very tightly together.
            automatic_color_index: Optional index to use for automatic coloring of series.
            includes_nan: Optional flag that can be used to inform that data set will not include NaN values.
                By default, it is assumed that the data provided might include NaN values.
                This results in extra processing to properly handle NaN values.
            x_axis (Axis): Optional non-default X Axis to attach series to.
            y_axis (Axis): Optional non-default Y Axis to attach series to.

        Returns:
            Reference to Point Line Series class.
        """
        x_axis, y_axis = get_axis_id(x_axis, y_axis)
        series = PointLineSeries(
            chart=self,
            data_pattern=data_pattern,
            colors=colors,
            lookup_values=lookup_values,
            ids=ids,
            sizes=sizes,
            rotations=rotations,
            allow_data_grouping=allow_data_grouping,
            automatic_color_index=automatic_color_index,
            auto_sorting_enabled=auto_sorting_enabled,
            includes_nan=includes_nan,
            x_axis=x_axis,
            y_axis=y_axis,
        )
        self.series_list.append(series)
        return series

    def add_spline_series(
        self,
        resolution: int | float = 20,
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
    ) -> SplineSeries:
        """Method for adding a new SplineSeries to the chart. This series type visualizes a list of Points
        (pair of X and Y coordinates), with a smoothed curve stroke + point markers over each data point.

        Args:
            resolution (int | float): Number of interpolated coordinates between two real data points.
            data_pattern (str): "ProgressiveX" | "ProgressiveY" | "RegressiveX" | "RegressiveY" – For best practices,
                the data pattern should ALWAYS be specified, even if there is no pattern to data (scatter data).
            colors (bool): If true, the DataSetXY should allocate for Color property to be included for every sample.
                This can be used to adjust data visualization to use per sample colors. Defaults to false.
            lookup_values (bool): Flag that can be used to enable data points value property on top
                of x and y. Disabled by default.
            ids (bool): If true, user supplied ID property is allocated to be included for every sample.
                Defaults to false.
            sizes (bool): If true, user supplied individual point size properties are allocated. This means that points
                can have individual sizes,rather than each point having same size. Defaults to false.
            rotations (bool): If true, user supplied individual point rotation properties are allocated.
                This means that points can have individual rotations, rather than each point having same rotation.
                Defaults to false.
            auto_sorting_enabled (bool): Controls whether automatic sorting of data according to active data_pattern is
                enabled or disabled. If data_pattern is any kind of progressive pattern, then input data can be
                automatically sorted to remain in that progressive order. This can be useful when data is arriving in
                the application asynchronously, and it can't be guaranteed that it arrives in the correct order.
                Please note that auto sorting only sorts by BATCH, not by SAMPLE. For example, if you supply batches of
                for example 10 samples at a time, auto sorting is capable of identifying the scenario where a newer
                batch arrives before one that should be displayed first. However, auto sorting is not capable of sorting
                any samples that are in wrong order within a BATCH. This is intentional due to effects on performance,
                and since its not a realistic need scenario. Defaults to true.
            allow_data_grouping: Optional flag that can be used to disable automatic grouping of progressive data
                that is packed very tightly together.
            automatic_color_index: Optional index to use for automatic coloring of series.
            includes_nan: Optional flag that can be used to inform that data set will not include NaN values.
                By default, it is assumed that the data provided might include NaN values.
                This results in extra processing to properly handle NaN values.
            x_axis (Axis): Optional non-default X Axis to attach series to.
            y_axis (Axis): Optional non-default Y Axis to attach series to.

        Returns:
            Reference to Spline Series class.
        """
        x_axis, y_axis = get_axis_id(x_axis, y_axis)
        series = SplineSeries(
            chart=self,
            resolution=resolution,
            data_pattern=data_pattern,
            colors=colors,
            lookup_values=lookup_values,
            ids=ids,
            sizes=sizes,
            rotations=rotations,
            allow_data_grouping=allow_data_grouping,
            automatic_color_index=automatic_color_index,
            auto_sorting_enabled=auto_sorting_enabled,
            includes_nan=includes_nan,
            x_axis=x_axis,
            y_axis=y_axis,
        )
        self.series_list.append(series)
        return series

    def add_step_series(
        self,
        step_mode: str = 'middle',
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
    ) -> StepSeries:
        """Method for adding a new StepSeries to the chart. This series type visualizes a list of Points
        (pair of X and Y coordinates), with a stepped stroke + point markers over each data point.

        Args:
            step_mode (str): "after" | "before" | "middle"
            data_pattern (str): "ProgressiveX" | "ProgressiveY" | "RegressiveX" | "RegressiveY" – For best practices,
                the data pattern should ALWAYS be specified, even if there is no pattern to data (scatter data).
            colors (bool): If true, the DataSetXY should allocate for Color property to be included for every sample.
                This can be used to adjust data visualization to use per sample colors. Defaults to false.
            lookup_values (bool): Flag that can be used to enable data points value property on top
                of x and y. Disabled by default.
            ids (bool): If true, user supplied ID property is allocated to be included for every sample.
                Defaults to false.
            sizes (bool): If true, user supplied individual point size properties are allocated. This means that points
                can have individual sizes,rather than each point having same size. Defaults to false.
            rotations (bool): If true, user supplied individual point rotation properties are allocated.
                This means that points can have individual rotations, rather than each point having same rotation.
                Defaults to false.
            auto_sorting_enabled (bool): Controls whether automatic sorting of data according to active data_pattern is
                enabled or disabled. If data_pattern is any kind of progressive pattern, then input data can be
                automatically sorted to remain in that progressive order. This can be useful when data is arriving in
                the application asynchronously, and it can't be guaranteed that it arrives in the correct order.
                Please note that auto sorting only sorts by BATCH, not by SAMPLE. For example, if you supply batches of
                for example 10 samples at a time, auto sorting is capable of identifying the scenario where a newer
                batch arrives before one that should be displayed first. However, auto sorting is not capable of sorting
                any samples that are in wrong order within a BATCH. This is intentional due to effects on performance,
                and since its not a realistic need scenario. Defaults to true.
            allow_data_grouping: Optional flag that can be used to disable automatic grouping of progressive data
                that is packed very tightly together.
            automatic_color_index: Optional index to use for automatic coloring of series.
            includes_nan: Optional flag that can be used to inform that data set will not include NaN values.
                By default, it is assumed that the data provided might include NaN values.
                This results in extra processing to properly handle NaN values.
            x_axis (Axis): Optional non-default X Axis to attach series to.
            y_axis (Axis): Optional non-default Y Axis to attach series to.

        Returns:
            Reference to Step Series class.
        """
        x_axis, y_axis = get_axis_id(x_axis, y_axis)
        series = StepSeries(
            chart=self,
            step_mode=step_mode,
            data_pattern=data_pattern,
            colors=colors,
            lookup_values=lookup_values,
            ids=ids,
            sizes=sizes,
            rotations=rotations,
            allow_data_grouping=allow_data_grouping,
            automatic_color_index=automatic_color_index,
            auto_sorting_enabled=auto_sorting_enabled,
            includes_nan=includes_nan,
            x_axis=x_axis,
            y_axis=y_axis,
        )
        self.series_list.append(series)
        return series

    def add_area_series(
        self,
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
    ) -> AreaSeries:
        """Method for adding a new AreaSeries to the chart. This series type is used for visualizing area from
        user-supplied curve data.

        Args:
            data_pattern (str): "ProgressiveX" | "ProgressiveY" | "RegressiveX" | "RegressiveY" – For best practices,
                the data pattern should ALWAYS be specified, even if there is no pattern to data (scatter data).
            colors (bool): If true, the DataSetXY should allocate for Color property to be included for every sample.
                This can be used to adjust data visualization to use per sample colors. Defaults to false.
            lookup_values (bool): Flag that can be used to enable data points value property on top
                of x and y. Disabled by default.
            ids (bool): If true, user supplied ID property is allocated to be included for every sample.
                Defaults to false.
            sizes (bool): If true, user supplied individual point size properties are allocated. This means that points
                can have individual sizes,rather than each point having same size. Defaults to false.
            rotations (bool): If true, user supplied individual point rotation properties are allocated.
                This means that points can have individual rotations, rather than each point having same rotation.
                Defaults to false.
            auto_sorting_enabled (bool): Controls whether automatic sorting of data according to active data_pattern is
                enabled or disabled. If data_pattern is any kind of progressive pattern, then input data can be
                automatically sorted to remain in that progressive order. This can be useful when data is arriving in
                the application asynchronously, and it can't be guaranteed that it arrives in the correct order.
                Please note that auto sorting only sorts by BATCH, not by SAMPLE. For example, if you supply batches of
                for example 10 samples at a time, auto sorting is capable of identifying the scenario where a newer
                batch arrives before one that should be displayed first. However, auto sorting is not capable of sorting
                any samples that are in wrong order within a BATCH. This is intentional due to effects on performance,
                and since its not a realistic need scenario. Defaults to true.
            allow_data_grouping: Optional flag that can be used to disable automatic grouping of progressive data
                that is packed very tightly together.
            automatic_color_index: Optional index to use for automatic coloring of series.
            includes_nan: Optional flag that can be used to inform that data set will not include NaN values.
                By default, it is assumed that the data provided might include NaN values.
                This results in extra processing to properly handle NaN values.
            x_axis (Axis): Optional non-default X Axis to attach series to.
            y_axis (Axis): Optional non-default Y Axis to attach series to.

        Returns:
            Reference to Area Series class.
        """
        x_axis, y_axis = get_axis_id(x_axis, y_axis)
        series = AreaSeries(
            chart=self,
            data_pattern=data_pattern,
            colors=colors,
            lookup_values=lookup_values,
            ids=ids,
            sizes=sizes,
            rotations=rotations,
            allow_data_grouping=allow_data_grouping,
            automatic_color_index=automatic_color_index,
            auto_sorting_enabled=auto_sorting_enabled,
            includes_nan=includes_nan,
            x_axis=x_axis,
            y_axis=y_axis,
        )
        self.series_list.append(series)
        return series

    def add_positive_area_series(self, x_axis: Axis = None, y_axis: Axis = None) -> AreaSeriesPositive:
        """Method for adding a new AreaSeriesPositive to the chart.
        This series type is used for visualizing area between a static baseline and supplied curve data.

        Args:
            x_axis (Axis): Optional non-default X Axis to attach series to.
            y_axis (Axis): Optional non-default Y Axis to attach series to.

        Returns:
            Reference to Area Series class.
        """
        x_axis, y_axis = get_axis_id(x_axis, y_axis)
        series = AreaSeriesPositive(chart=self, x_axis=x_axis, y_axis=y_axis)
        self.series_list.append(series)
        return series

    def add_negative_area_series(self, x_axis: Axis = None, y_axis: Axis = None) -> AreaSeriesNegative:
        """Method for adding a new AreaSeriesNegative to the chart.
        This series type is used for visualizing area between a static baseline and supplied curve data.

        Args:
            x_axis (Axis): Optional non-default X Axis to attach series to.
            y_axis (Axis): Optional non-default Y Axis to attach series to.

        Returns:
            Reference to Area Series class.
        """
        x_axis, y_axis = get_axis_id(x_axis, y_axis)
        series = AreaSeriesNegative(chart=self, x_axis=x_axis, y_axis=y_axis)
        self.series_list.append(series)
        return series

    def add_bipolar_area_series(self, x_axis: Axis = None, y_axis: Axis = None) -> AreaSeriesBipolar:
        """Method for adding a new AreaSeriesBipolar to the chart.
        This series type is used for visualizing area between a static baseline and supplied curve data.

        Args:
            x_axis (Axis): Optional non-default X Axis to attach series to.
            y_axis (Axis): Optional non-default Y Axis to attach series to.

        Returns:
            Reference to Area Series class.
        """
        x_axis, y_axis = get_axis_id(x_axis, y_axis)
        series = AreaSeriesBipolar(chart=self, x_axis=x_axis, y_axis=y_axis)
        self.series_list.append(series)
        return series

    def add_area_range_series(self, x_axis: Axis = None, y_axis: Axis = None) -> AreaRangeSeries:
        """Method for adding a new AreaRangeSeries to the chart.
        This series type is used for visualizing bands of data between two curves of data.

        Area Range Series accepts data of form {position, low, high}

        Args:
            x_axis (Axis): Optional non-default X Axis to attach series to.
            y_axis (Axis): Optional non-default Y Axis to attach series to.

        Returns:
            Reference to Area Range Series class.
        """
        x_axis, y_axis = get_axis_id(x_axis, y_axis)
        series = AreaRangeSeries(chart=self, x_axis=x_axis, y_axis=y_axis)
        self.series_list.append(series)
        return series

    def add_heatmap_grid_series(
        self,
        columns: int,
        rows: int,
        data_order: str = 'columns',
        x_axis: Axis = None,
        y_axis: Axis = None,
    ) -> HeatmapGridSeries:
        """Add a Series for visualizing a Heatmap Grid with a _static column and grid count.

        Heatmap Grid Series accepts data in the form of two-dimensional matrix of correct size that includes
        integers or floats.

        Args:
            columns (int): Amount of columns (values on X Axis).
            rows (int): Amount of rows (values on Y Axis).
            data_order (str): "columns" | "rows" - Specify how to interpret grid matrix values supplied by user.
            x_axis (Axis): Optional non-default X Axis to attach series to.
            y_axis (Axis): Optional non-default Y Axis to attach series to.

        Returns:
            Reference to Heatmap Grid Series class.
        """
        x_axis, y_axis = get_axis_id(x_axis, y_axis)
        series = HeatmapGridSeries(
            chart=self,
            columns=columns,
            rows=rows,
            data_order=data_order,
            x_axis=x_axis,
            y_axis=y_axis,
        )
        self.series_list.append(series)
        return series

    def add_heatmap_scrolling_grid_series(
        self,
        resolution: int,
        scroll_dimension: str = 'columns',
        x_axis: Axis = None,
        y_axis: Axis = None,
    ) -> HeatmapScrollingGridSeries:
        """Add a Series for visualizing a Heatmap Grid, with API for pushing data in a scrolling manner
        (append new data on top of existing data).

        Heatmap Scrolling Grid Series accepts data in the form of two-dimensional matrix of correct size that includes
        integers or floats.

        Args:
            resolution (int): Static amount of columns (cells on X Axis) OR rows (cells on Y Axis).
            scroll_dimension (str): "columns" | "rows" -
                Select scrolling dimension, as well as how to interpret grid matrix values supplied by user.
            x_axis (Axis): Optional non-default X Axis to attach series to.
            y_axis (Axis): Optional non-default Y Axis to attach series to.

        Returns:
            Reference to Heatmap Scrolling Grid Series class.
        """
        x_axis, y_axis = get_axis_id(x_axis, y_axis)
        series = HeatmapScrollingGridSeries(
            chart=self,
            resolution=resolution,
            scroll_dimension=scroll_dimension,
            x_axis=x_axis,
            y_axis=y_axis,
        )
        self.series_list.append(series)
        return series

    def add_box_series(self, x_axis: Axis = None, y_axis: Axis = None) -> BoxSeries:
        """

        Args:
            x_axis (Axis): Optional non-default X Axis to attach series to.
            y_axis (Axis): Optional non-default Y Axis to attach series to.

        Returns:
            Reference to Box Series class.
        """
        x_axis, y_axis = get_axis_id(x_axis, y_axis)
        series = BoxSeries(chart=self, x_axis=x_axis, y_axis=y_axis)
        self.series_list.append(series)
        return series

    def pan(self, x: int | float, y: int | float):
        """Method pans axes by pixels.

        Args:
            x (int | float): Amount to pan X in pixels.
            y (int | float): Amount to pan Y in pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'pan', {'x': x, 'y': y})
        return self

    def zoom(self, location: tuple[int, int], amount: tuple[int, int]):
        """Method pans axes by pixels.

        Args:
            location (tuple[int, int]): Origin location for zooming as viewport pixels
            amount (tuple[int, int]): Amount to zoom X/Y in pixels

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(
            self.id,
            'zoom',
            {
                'location': {'x': location[0], 'y': location[1]},
                'amount': {'x': amount[0], 'y': amount[1]},
            },
        )
        return self

    def set_cursor_enabled_during_axis_animation(self, enabled: bool):
        """Disable/Enable Cursor during Axis Animations. Axis Animations are Axis Scale changes that are animated,
        such as Zooming and Scrolling done by using API (such as Axis.setInterval)
        or by using the mouse to click & drag on the Chart.

        Args:
            enabled (bool): Boolean value to enable or disable Cursor during Axis Animations.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setCursorEnabledDuringAxisAnimation', {'enabled': enabled})
        return self

    def add_ellipse_series(
        self,
        x_axis: Axis = None,
        y_axis: Axis = None,
    ):
        """Add an EllipseFigure to the Chart

        Args:
            x_axis (Axis): Optional non-default X Axis to attach series to.
            y_axis (Axis): Optional non-default Y Axis to attach series to.

        Returns:
            Reference to Ellipse Series class.
        """
        x_axis, y_axis = get_axis_id(x_axis, y_axis)
        ellipse_series = EllipseSeries(
            self,
            x_axis=x_axis,
            y_axis=y_axis,
        )
        self.series_list.append(ellipse_series)
        return ellipse_series

    def add_rectangle_series(
        self,
        x_axis: Axis = None,
        y_axis: Axis = None,
    ):
        """Add an RectangleFigure to the Chart.
        Args:
            x_axis (Axis): Optional non-default X Axis to attach series to.
            y_axis (Axis): Optional non-default Y Axis to attach series to.

        Returns:
            Reference to Rectangle Series class.
        """
        x_axis, y_axis = get_axis_id(x_axis, y_axis)
        rectangle_series = RectangleSeries(
            self,
            x_axis=x_axis,
            y_axis=y_axis,
        )
        self.series_list.append(rectangle_series)
        return rectangle_series

    def add_polygon_series(
        self,
        x_axis: Axis = None,
        y_axis: Axis = None,
    ):
        """Add an PolygonFigure to the Chart.

        Args:
            x_axis (Axis): Optional non-default X Axis to attach series to.
            y_axis (Axis): Optional non-default Y Axis to attach series to.

        Returns:
            Reference to Polygon Series class.
        """
        x_axis, y_axis = get_axis_id(x_axis, y_axis)
        polygon_series = PolygonSeries(
            self,
            x_axis=x_axis,
            y_axis=y_axis,
        )
        self.series_list.append(polygon_series)
        return polygon_series

    def add_segment_series(
        self,
        x_axis: Axis = None,
        y_axis: Axis = None,
    ):
        """Add an SegmentFigure to the Chart.

        Args:
            x_axis (Axis): Optional non-default X Axis to attach series to.
            y_axis (Axis): Optional non-default Y Axis to attach series to.

        Returns:
            Reference to Segment Series class.
        """
        x_axis, y_axis = get_axis_id(x_axis, y_axis)
        segment_series = SegmentSeries(
            self,
            x_axis=x_axis,
            y_axis=y_axis,
        )
        self.series_list.append(segment_series)
        return segment_series

    def set_user_interactions(self, interactions=...):
        """Configure user interactions from a set of preset options for XY charts.

        Args:
            interactions (dict or None):
                - `None`: disable all interactions
                - `{}` or no argument: restore default interactions
                - `dict`: configure specific interactions

        Returns:
            ChartXY: Reference to the chart object for method chaining.

        Examples:
            ## Disable all interactions:
            chart.set_user_interactions(None)

            ## Restore default interactions:
            chart.set_user_interactions()
            chart.set_user_interactions({})

            ## Configure specific interactions:
            chart.set_user_interactions({
                'pan': {
                    'lmb': {'drag': True},
                    'rmb': False,
                },
                'rectangleZoom': {
                    'lmb': False,
                    'rmb': {'drag': True},
                },
            })
        """
        return super().set_user_interactions(interactions)


class ChartXYDashboard(ChartXY):
    """Class for ChartXY contained in Dashboard."""

    def __init__(
        self,
        instance: Instance,
        dashboard_id: str,
        column: int,
        row: int,
        colspan: int,
        rowspan: int,
        title: str = None,
    ):
        ChartWithSeries.__init__(self, instance)
        self.instance.send(
            self.id,
            'createChartXY',
            {
                'db': dashboard_id,
                'column': column,
                'row': row,
                'colspan': colspan,
                'rowspan': rowspan,
            },
        )
        if title:
            self.instance.send(self.id, 'setTitle', {'title': title})
        ChartWithXYAxis.__init__(self)
