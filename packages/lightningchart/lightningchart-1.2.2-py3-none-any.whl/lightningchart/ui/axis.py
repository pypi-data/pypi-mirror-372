from __future__ import annotations

import uuid

from lightningchart.series import ComponentWithLinePaletteColoring
from lightningchart.ui import UIEWithTitle, UIElement, UserInteractions
from lightningchart.ui.band import Band
from lightningchart.ui.constant_line import ConstantLine
from lightningchart.ui.custom_tick import CustomTick
from lightningchart.ui.custom_tick import CustomTick3D
from lightningchart.utils import convert_color_to_hex


class GenericAxis(UIEWithTitle):
    def __init__(self, chart):
        UIElement.__init__(self, chart)

    def set_title(self, title: str):
        """Specifies an Axis title string

        Args:
            title: Axis title as a string

        Returns:
            Axis itself for fluent interface
        """
        self.instance.send(self.id, 'setTitle', {'title': title})
        return self

    def set_title_color(self, color: any):
        """Set the color of the Chart title.

        Args:
            color (Color): Color of the title.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setTitleColor', {'color': color})
        return self

    def set_title_effect(self, enabled: bool):
        """Set theme effect enabled on component or disabled.

        Args:
            enabled: Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTitleEffect', {'enabled': enabled})
        return self

    def set_visible(self, visible: bool = True):
        """Set element visibility.

        Args:
            visible (bool): True when element should be visible and false when element should be hidden.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setVisible', {'visible': visible})
        return self

    def set_scroll_strategy(
        self,
        strategy: str = 'scrolling',
        progressive: bool = None,
        realtime: bool | float = None,
        start: bool = None,
        end: bool = None,
        visibleonly: bool = None,
    ):
        """Specify ScrollStrategy of the Axis.
        This decides where the Axis scrolls based on current view and series boundaries.

        Args:
            strategy (str):
            - "expansion": expand to fit new data without moving view
            - "fitting": resize to fit all data
            - "scrolling" (default): scroll with incoming data
        progressive (bool, optional): Enable progressive scrolling.
        realtime (bool | float, optional): Enable realtime scrolling or set update interval (in seconds).
        start (bool, optional): Lock scroll to start of data range.
        end (bool, optional): Lock scroll to end of data range.
        visibleonly (bool, optional): Limit effect to visible series only.

        Returns:
            The instance of the class for fluent interface.
        """
        strategies = ('expansion', 'fitting', 'scrolling')

        if strategy == 'progressive':
            strategy = 'scrolling'

        if strategy not in strategies:
            raise ValueError(f"Expected strategy to be one of {strategies}, but got '{strategy}'.")

        options = {}
        if start is not None:
            options['start'] = bool(start)
        if end is not None:
            options['end'] = bool(end)
        if visibleonly is not None:
            options['visibleonly'] = bool(visibleonly)
        if progressive is not None:
            options['progressive'] = bool(progressive)
        if realtime is not None:
            options['realtime'] = bool(realtime) or float(realtime)

        self.instance.send(
            self.chart.id,
            'setScrollStrategy',
            {'strategy': strategy, 'options': options, 'axis': self.id},
        )
        return self

    def set_interval(
        self,
        start: int | float,
        end: int | float,
        stop_axis_after: bool = True,
        animate: bool = False,
    ):
        """Set axis interval.

        Args:
            start (int): Start of the axis.
            end (int): End of the axis.
            stop_axis_after (bool): If false, the axis won't stop from scrolling.
            animate (bool): Boolean for animation enabled, or number for animation duration in milliseconds.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(
            self.chart.id,
            'setAxisInterval',
            {
                'start': start,
                'end': end,
                'axis': self.id,
                'stop': stop_axis_after,
                'animate': animate,
            },
        )
        return self

    def fit(self, animate: int | bool = 0, stop_axis_after: bool = False):
        """Fit axis view to attached series.

        Args:
            animate (int | bool): Boolean for animation enabled, or number for animation duration in milliseconds.
            stop_axis_after (bool): If true, stops Axis after fitting.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'fit', {'animate': animate, 'stopAxisAfter': stop_axis_after})
        return self

    def set_animations_enabled(self, enabled: bool = True):
        """Disable/Enable all animations of the Chart.

        Args:
            enabled (bool): Boolean value to enable or disable animations.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAnimationsEnabled', {'enabled': enabled})
        return self

    def set_stroke(self, thickness: int | float, color: any = None):
        """Set the Axis line stroke.

        Args:
            thickness (int | float): Thickness of the stroke.
            color (Color): Color of the stroke.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(
            self.id,
            'setStrokeStyle',
            {'thickness': thickness, 'color': color},
        )
        return self

    def set_default_interval(self, start: int | float, end: int | float):
        """Set Axis default interval. This does the same as setInterval method, but is also applied again whenever
        fit is triggered, or the "zoom to fit" user interaction is triggered.

        Args:
            start (int | float): Interval start point.
            end (int | float): Interval end point.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setDefaultInterval', {'start': start, 'end': end})
        return self

    def set_interval_restrictions(
        self,
        interval_min: int | float = None,
        interval_max: int | float = None,
        start_min: int | float = None,
        start_max: int | float = None,
        end_min: int | float = None,
        end_max: int | float = None,
    ):
        """Set or clear restrictions on Axis interval (start/end).

        These restrictions are not applied immediately but will affect all axis scrolling
        and user interactions afterward.

        Args:
            interval_min (int | float, optional): Minimum interval length.
            interval_max (int | float, optional): Maximum interval length.
            start_min (int | float, optional): Minimum interval start value.
            start_max (int | float, optional): Maximum interval start value.
            end_min (int | float, optional): Minimum interval end value.
            end_max (int | float, optional): Maximum interval end value.

        Usage:
            - `axis.set_interval_restrictions(interval_min=10, interval_max=1000)`
            - `axis.set_interval_restrictions(start_min=0, end_max=5000)`
            - `axis.set_interval_restrictions(None)`  # Clears all restrictions

        Returns:
            The instance of the class for fluent interface.
        """

        if all(
            v is None
            for v in [
                interval_min,
                interval_max,
                start_min,
                start_max,
                end_min,
                end_max,
            ]
        ):
            self.instance.send(self.id, 'setIntervalRestrictions', None)
            return self

        self.instance.send(
            self.id,
            'setIntervalRestrictions',
            {
                'endMax': end_max,
                'endMin': end_min,
                'intervalMax': interval_max,
                'intervalMin': interval_min,
                'startMax': start_max,
                'startMin': start_min,
            },
        )

        return self


class Axis(GenericAxis, ComponentWithLinePaletteColoring, UserInteractions):
    def __init__(
        self,
        chart,
        axis: str,
        stack_index: int,
        parallel_index: int,
        opposite: bool,
        type: str,
        base: int,
    ):
        GenericAxis.__init__(self, chart)
        self.instance.send(
            self.id,
            'addAxis',
            {
                'chart': self.chart.id,
                'axis': axis,
                'opposite': opposite,
                'iStack': stack_index,
                'iParallel': parallel_index,
                'type': type,
                'base': base,
            },
        )

    def set_decimal_precision(self, decimals: int):
        """Format the axis ticks to certain number of decimal numbers.

        Args:
            decimals (int): Decimal precision.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTickStrategyFormattingRound', {'decimals': decimals})
        return self

    def set_tick_formatting(self, text: str):
        """

        Args:
            text (str):

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTickStrategyFormattingText', {'text': text})
        return self

    def set_length(self, length: int | float, relative: bool):
        """Configure length of axis. E.g. height for Y axis, width for X axis.

        Args:
            length (int | float): Length value
            relative (bool): If true, length value is interpreted as relative length across multiple axes. If false,
                length value is interpreted as length in pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setLength', {'length': length, 'relative': relative})
        return self

    def set_margins(self, start: int | float, end: int | float):
        """Add empty space at either end of the axis, without affecting the relative size of the Axis.

        Args:
            start (int | float): Start margin in pixels.
            end (int | float): End margin in pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setMargins', {'start': start, 'end': end})
        return self

    def set_scroll_margins(self, *args, **kwargs):
        """Set scroll margins for the axis.

        Args:
            start (int | float): Start margin in pixels.
            end (int | float): End margin in pixels.

                - None: Clears all scroll margins.
                - int: Sets symmetric scroll margins in pixels.
                - bool: If False, disables scroll margins entirely.
                - dict: Sets asymmetric scroll margins with keys 'start' and 'end' in pixels.

        Example:
            axis.set_scroll_margins(5)  # Sets symmetric scroll margins as 5 pixels.
            axis.set_scroll_margins(False)  # Disables scroll margins entirely.
            axis.set_scroll_margins(start = 0, end = 10})  # Sets asymmetric scroll margins.
        """
        if args:
            margins = {'arg': args[0]}
            if margins['arg'] is None:
                margins = {}
        elif 'start' in kwargs or 'end' in kwargs:
            margins = {'arg': {'start': kwargs.get('start', 0), 'end': kwargs.get('end', 0)}}

        else:
            raise ValueError("Expected either a valid positional argument or 'start', 'end' as keyword arguments")

        self.instance.send(self.id, 'setScrollMargins', margins)
        return self

    def add_band(self, on_top: bool = True):
        """Add a highlighter Band to the Axis. A Band can be used to highlight an interval on the Axis.

        Args:
            on_top (bool): Is Band rendered above Series, or below. Default to above.

        Returns:
            Reference to Band class.
        """
        return Band(self.chart, self, on_top)

    def add_constant_line(self, on_top: bool = True):
        """Add a highlighter ConstantLine to the Axis.
        A ConstantLine can be used to highlight a specific value on the Axis.

        Args:
            on_top (bool): Is ConstantLine rendered above Series, or below. Default to above.

        Returns:
            Reference to ConstantLine class.
        """
        return ConstantLine(self.chart, self, on_top)

    def add_custom_tick(self, tick_type: str = 'major'):
        """Add custom tick to Axis. Custom ticks can be used to expand on default tick placement,
        or completely override Axis ticks placement with custom logic.

        Args:
            tick_type (str): "major" | "minor" | "box"

        Returns:
            Reference to CustomTick class.
        """
        types = ('major', 'minor', 'box')
        if tick_type not in types:
            raise ValueError(f"Expected tick_type to be one of {types}, but got '{tick_type}'.")

        return CustomTick(self.chart, self, tick_type)

    def set_tick_strategy(self, strategy: str, time_origin: int | float = None, utc: bool = False):
        """Set TickStrategy of Axis. The TickStrategy defines the positioning and formatting logic of Axis ticks
        as well as the style of created ticks.

        Args:
            strategy (str): "Empty" | "Numeric" | "DateTime" | "Time"
            time_origin (int | float): Use with "DateTime" or "Time" strategy.
                If a time origin is defined, data points will be interpreted as milliseconds since time_origin.
            utc (bool): Use with DateTime strategy. By default, false, which means that tick placement is applied
                according to clients local time-zone/region and possible daylight saving cycle.
                When true, tick placement is applied in UTC which means no daylight saving adjustments &
                timestamps are displayed as milliseconds without any time-zone region offsets.

        Returns:
            The instance of the class for fluent interface.
        """
        strategies = ('Empty', 'Numeric', 'DateTime', 'Time')
        if strategy not in strategies:
            raise ValueError(f"Expected strategy to be one of {strategies}, but got '{strategy}'.")

        self.instance.send(
            self.chart.id,
            'setTickStrategy',
            {
                'strategy': strategy,
                'axis': self.id,
                'timeOrigin': time_origin,
                'utc': utc,
            },
        )
        return self

    def pan(self, amount: int | float):
        """Pan scale by pixel value delta.

        Args:
            amount (int | float): Amount to shift scale of axis in pixels

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'panAxis', {'amount': amount})
        return self

    def zoom(self, reference_position: int | float, zoom_direction: int | float):
        """Zoom scale from/to a position.

        Args:
            reference_position (int | float): Position to zoom towards or from on axis.
            zoom_direction (int | float): Amount and direction of zoom [-1, 1] as a guideline.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(
            self.id,
            'zoomAxis',
            {'referencePosition': reference_position, 'zoomDirection': zoom_direction},
        )
        return self

    def set_major_tick_font(
        self,
        size: int | float,
        family: str = 'Segoe UI, -apple-system, Verdana, Helvetica',
        style: str = 'normal',
        weight: str = 'normal',
    ):
        """Set the font of major axis tick labels.

        Args:
            size (int | float): CSS font size. For example, 16.
            family (str): CSS font family. For example, 'Arial, Helvetica, sans-serif'.
            weight (str): CSS font weight. For example, 'bold'.
            style (str): CSS font style. For example, 'italic'

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(
            self.id,
            'setMajorTickFont',
            {'family': family, 'size': size, 'weight': weight, 'style': style},
        )
        return self

    def set_minor_tick_font(
        self,
        size: int | float,
        family: str = 'Segoe UI, -apple-system, Verdana, Helvetica',
        style: str = 'normal',
        weight: str = 'normal',
    ):
        """Set the font of minor axis tick labels.

        Args:
            size (int | float): CSS font size. For example, 16.
            family (str): CSS font family. For example, 'Arial, Helvetica, sans-serif'.
            weight (str): CSS font weight. For example, 'bold'.
            style (str): CSS font style. For example, 'italic'

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(
            self.id,
            'setMinorTickFont',
            {'family': family, 'size': size, 'weight': weight, 'style': style},
        )
        return self

    def set_major_tick_color(self, color: any):
        """Set the color of major axis tick labels.

        Args:
            color (Color): Color of the labels.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setMajorTickFillStyle', {'color': color})
        return self

    def set_minor_tick_color(self, color: any):
        """Set the color of minor axis tick labels.

        Args:
            color (Color): Color of the labels.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setMinorTickFillStyle', {'color': color})
        return self

    def set_thickness(self, thickness: int | float):
        """Set Axis thickness as pixels.

        Args:
            thickness (int | float): Explicit thickness of Axis as pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setThickness', {'thickness': thickness})
        return self

    def set_title_margin(self, margin: int | float):
        """Specifies padding after chart title.

        Args:
            margin (int | float): Gap after the chart title in pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTitleMargin', {'margin': margin})
        return self

    def set_fallback_to_extreme_ticks(self, enabled: bool = True):
        """Enable or disable automatic fallback to extreme ticks when an axis becomes too small.

        Args:
            enabled (bool): If True, extreme ticks will be automatically displayed when needed.
                            If False, restores the previous behavior (hides extreme ticks).
                            This only applies for Numeric Tick Strategies.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setFallBackToExtremeTicksAutomatically', {'enabled': enabled})
        return self

    def set_great_tick_style(
        self,
        color: any = None,
        size: int | float = None,
        length: int | float = None,
        family: str = None,
        style: str = None,
        weight: str = None,
        disable: bool = False,
    ):
        """Set or disable the style of Great Ticks for a DateTime axis.

        Args:
            color (Color, optional): Tick label color.
            size (int | float, optional): Tick label font size.
            length (int | float, optional): Length of tick lines.
            family (str, optional): Font family.
            style (str, optional): Font style ('normal', 'italic').
            weight (str, optional): Font weight ('normal', 'bold').
            disable (bool, optional): Set to True to disable Great Ticks.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        config = {
            'color': color,
            'fontSize': size,
            'tickLength': length,
            'fontFamily': family,
            'fontStyle': style,
            'fontWeight': weight,
            'disable': disable,
        }
        config = {k: v for k, v in config.items() if v is not None}

        self.instance.send(self.id, 'setGreatTickStyle', config)
        return self

    def set_formatting_function(
        self,
        unit: str = None,
        precision: int = None,
        operation: str = 'none',
        scale: float = 1.0,
        format_type: str = 'standard',
    ):
        """
        Set the formatting function using structured configuration for Numeric Axis.

        Args:
            unit (str, optional): Unit to display (e.g., "μs", "ms", "kg", "%")
            precision (int, optional): Number of decimal places (None = auto)
            operation (str): Mathematical operation to apply:
                - 'none' - No operation (default)
                - 'round' - Round to nearest integer
                - 'ceil' - Round up to nearest integer
                - 'floor' - Round down to nearest integer
            scale (float): Scale factor to multiply value (default: 1.0)
                - 0.001 for milliseconds to seconds
                - 1000 for seconds to milliseconds
                - 100 for decimal to percentage
            format_type (str): Format style:
                - 'standard' - Normal number formatting
                - 'scientific' - Scientific notation
                - 'engineering' - Engineering notation (powers of 1000)
                - 'compact' - Compact notation (K, M, B suffixes)

        Examples:
            # Rounded microseconds
            axis.set_formatting_function(unit="μs", operation="round")

            # Convert milliseconds to seconds with 2 decimal places
            axis.set_formatting_function(unit="s", scale=0.001, precision=2)

            # Percentage with 1 decimal place
            axis.set_formatting_function(unit="%", scale=100, precision=1)

            # Large numbers with compact notation
            axis.set_formatting_function(format_type="compact", precision=1)

        Returns:
            The instance of the class for fluent interface.
        """

        config = {
            'unit': unit or '',
            'precision': precision,
            'operation': operation,
            'scale': scale,
            'format_type': format_type,
        }

        self.instance.send(self.id, 'setFormattingFunction', config)
        return self

    def set_user_interactions(self, interactions=...):
        """Configure user interactions from a set of preset options.

        Args:
            interactions (dict or None):
                - `None`: disable all interactions
                - `{}` or no argument: restore default interactions
                - `dict`: configure specific interactions

        Examples:
            ## Disable all interactions:
            axis.set_user_interactions(None)

            ## Restore default interactions:
            axis.set_user_interactions()
            axis.set_user_interactions({})

            ## Configure specific interactions:
            axis.set_user_interactions(
            {
                'pan': {
                    'lmb': {'drag': True},
                    'rmb': False,
                    'mmb': False,
                },
                'rectangleZoom': {
                    'lmb': False,
                    'rmb': {'drag': True},
                    'mmb': False,
                },
            }
        )
        """
        return super().set_user_interactions(interactions)


class DefaultAxis(Axis):
    def __init__(self, chart, axis: str):
        self.chart = chart
        self.dimension = axis
        self.id = str(uuid.uuid4()).split('-')[0]
        self.instance = chart.instance
        self.instance.send(
            self.chart.id,
            'getDefaultAxisReference',
            {'dimension': self.dimension, 'axisID': self.id},
        )


class DefaultAxis3D(GenericAxis):
    def __init__(self, chart, axis: str):
        self.chart = chart
        self.dimension = axis
        self.id = str(uuid.uuid4()).split('-')[0]
        self.instance = chart.instance
        self.instance.send(
            self.chart.id,
            'getDefaultAxisReference',
            {'dimension': self.dimension, 'axisID': self.id},
        )

    def set_tick_strategy(self, strategy: str, time_origin: int | float = None, utc: bool = False):
        """Set TickStrategy of Axis. The TickStrategy defines the positioning and formatting logic of Axis ticks
        as well as the style of created ticks.

        Args:
            strategy (str): "Empty" | "Numeric" | "DateTime" | "Time"
            time_origin (int | float): Define with time.time(). If a time origin is defined,
                data-points will instead be interpreted as milliseconds since time origin.
            utc (bool): Use with DateTime strategy. By default, false, which means that tick placement is applied
                according to clients local time-zone/region and possible daylight saving cycle.
                When true, tick placement is applied in UTC which means no daylight saving adjustments &
                timestamps are displayed as milliseconds without any time-zone region offsets.

        Returns:
            The instance of the class for fluent interface.
        """
        strategies = ('Empty', 'Numeric', 'DateTime', 'Time')
        if strategy not in strategies:
            raise ValueError(f"Expected strategy to be one of {strategies}, but got '{strategy}'.")

        self.instance.send(
            self.chart.id,
            'setTickStrategy',
            {
                'strategy': strategy,
                'axis': self.id,
                'timeOrigin': time_origin,
                'utc': utc,
            },
        )
        return self

    def add_custom_tick(self, tick_type: str = 'major'):
        """Add a 3D custom tick to the Axis.
        Custom ticks can be used to completely control tick placement, text, and styles in a 3D environment.

        Args:
            tick_type (str): "major" | "minor" | "box"

        Returns:
            Reference to CustomTick3D class.
        """
        types = ('major', 'minor', 'box')
        if tick_type not in types:
            raise ValueError(f"Expected tick_type to be one of {types}, but got '{tick_type}'.")

        return CustomTick3D(self.chart, self, tick_type)


class BarChartAxis(GenericAxis):
    def __init__(self, chart):
        GenericAxis.__init__(self, chart)

    def set_thickness(self, thickness: int | float):
        """Set Axis thickness as pixels.

        Args:
            thickness (int | float): Explicit thickness of Axis as pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setThickness', {'thickness': thickness})
        return self


class CategoryAxis(BarChartAxis):
    def __init__(self, chart):
        BarChartAxis.__init__(self, chart)
        self.instance.send(self.id, 'getCategoryAxisReference', {'chart': self.chart.id})


class ValueAxis(BarChartAxis):
    def __init__(self, chart):
        BarChartAxis.__init__(self, chart)
        self.instance.send(self.id, 'getValueAxisReference', {'chart': self.chart.id})

    def set_tick_strategy(self, strategy: str):
        """Set TickStrategy of Axis. The TickStrategy defines the positioning and formatting logic of Axis ticks
        as well as the style of created ticks.

        Args:
            strategy (str): "Empty" | "Numeric"

        Returns:
            The instance of the class for fluent interface.
        """
        strategies = ('Empty', 'Numeric')
        if strategy not in strategies:
            raise ValueError(f"Expected strategy to be one of {strategies}, but got '{strategy}'.")

        self.instance.send(
            self.chart.id,
            'setTickStrategy',
            {
                'strategy': strategy,
                'axis': self.id,
            },
        )
        return self

    def set_decimal_precision(self, decimals: int):
        """Format the axis ticks to certain number of decimal numbers.

        Args:
            decimals (int): Decimal precision.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTickStrategyFormattingRound', {'decimals': decimals})
        return self


class SpiderChartAxis:
    """A class containing axis-related methods for the SpiderChart."""

    def set_axis_interval(self, start: int | float, end: int | float, stop_axis_after: bool = True):
        """Set interval of Charts Axes

        Args:
            start (int | float): Value at edges of chart.
            end (int | float): Value at center of chart. Defaults to zero.
            stop_axis_after (bool): Stop axis after value.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(
            self.id,
            'setSpiderAxisInterval',
            {'start': start, 'end': end, 'stop': stop_axis_after},
        )
        return self

    def add_axis(self, tag: str):
        """Add a new axis to Spider Chart.

        Args:
            tag (str): String tag for the axis.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'addSpiderAxis', {'tag': tag})
        return self

    def set_auto_axis_creation(self, enabled: bool):
        """Specifies if auto creation of axis is turned on or not.

        Args:
            enabled (bool): State of automatic axis creation.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAutoAxis', {'enabled': enabled})
        return self

    def set_axis_label_effect(self, enabled: bool):
        """Set theme effect enabled on component or disabled.

        Args:
            enabled (bool): Theme effect enabled.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAxisLabelEffect', {'enabled': enabled})
        return self

    def set_axis_label_font(
        self,
        size: int | float,
        family: str = 'Segoe UI, -apple-system, Verdana, Helvetica',
        style: str = 'normal',
        weight: str = 'normal',
    ):
        """Set font of axis labels.

        Args:
            size (int | float): CSS font size. For example, 16.
            family (str): CSS font family. For example, 'Arial, Helvetica, sans-serif'.
            weight (str): CSS font weight. For example, 'bold'.
            style (str): CSS font style. For example, 'italic'

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(
            self.id,
            'setAxisLabelFont',
            {'family': family, 'size': size, 'weight': weight, 'style': style},
        )
        return self

    def set_axis_label_padding(self, padding: int | float):
        """Set padding of axis labels.

        Args:
            padding (int | float): Padding in pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAxisLabelPadding', {'padding': padding})
        return self

    def set_axis_label_color(self, color: any):
        """Set the color of axis labels.

        Args:
            color (Color): Color of the labels.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setAxisLabelStyle', {'color': color})
        return self

    def set_axis_scroll_strategy(self, strategy: str):
        """Sets the scroll strategy of charts axes.

        Args:
            strategy (str): "expansion" | "fitting" | "progressive" | "regressive" | "none"

        Returns:
            The instance of the class for fluent interface.
        """
        scroll_strategies = (
            'expansion',
            'fitting',
            'progressive',
            'regressive',
            'none',
        )
        if strategy not in scroll_strategies:
            raise ValueError(f"Expected strategy to be one of {scroll_strategies}, but got '{strategy}'.")
        self.instance.send(self.id, 'setAxisScrollStrategy', {'strategy': strategy})
        return self

    def set_axis_style(self, thickness: int | float, color: any = None):
        """Set the style of axis line.

        Args:
            thickness (int | float): Thickness of the axis line.
            color (Color): Color of the axis line.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setAxisStyle', {'thickness': thickness, 'color': color})
        return self

    def set_scale_label_font(
        self,
        size: int | float,
        family: str = 'Segoe UI, -apple-system, Verdana, Helvetica',
        style: str = 'normal',
        weight: str = 'normal',
    ):
        """Set font of scale labels.

        Args:
            size (int | float): CSS font size. For example, 16.
            family (str): CSS font family. For example, 'Arial, Helvetica, sans-serif'.
            weight (str): CSS font weight. For example, 'bold'.
            style (str): CSS font style. For example, 'italic'

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(
            self.id,
            'setScaleLabelFont',
            {'family': family, 'size': size, 'weight': weight, 'style': style},
        )
        return self

    def set_scale_label_padding(self, padding: int | float):
        """Set padding of scale labels.

        Args:
            padding (int | float): Padding in pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setScaleLabelPadding', {'padding': padding})
        return self

    def set_scale_label_color(self, color: any):
        """Set the color of the scale labels.

        Args:
            color (Color): Color of the scale labels.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setScaleLabelStyle', {'color': color})
        return self
