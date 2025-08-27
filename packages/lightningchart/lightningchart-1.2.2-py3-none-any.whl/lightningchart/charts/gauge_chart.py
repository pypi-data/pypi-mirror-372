from __future__ import annotations

from lightningchart import conf, Themes
from lightningchart.charts import GeneralMethods, TitleMethods, Chart
from lightningchart.instance import Instance
from lightningchart.utils import convert_to_dict, convert_color_to_hex


class GaugeChart(GeneralMethods, TitleMethods):
    """Gauge charts indicate where your data point(s) falls over a particular range."""

    def __init__(
        self,
        start: int | float = None,
        end: int | float = None,
        value: int | float = None,
        angle_interval_start: int | float = 225,
        angle_interval_end: int | float = -45,
        theme: Themes = Themes.Light,
        theme_scale: float = 1.0,
        title: str = None,
        license: str = None,
        license_information: str = None,
        html_text_rendering: bool = False,
    ):
        """A Gauge Chart with a single solid colored slice.

        Args:
            start (int | float): Start scale value.
            end (int | float): End scale value.
            value (int | float): Value of the gauge.
            angle_interval_start (int | float): Start angle of the gauge in degrees.
            angle_interval_end (int | float): End angle of the gauge in degrees.
            thickness (int | float): Thickness of the gauge.
            theme (Themes): Theme of the chart.
            title (str): Title of the chart.
            license (str): License key.
            theme_scale: To up or downscale font sizes as well as tick lengths, element paddings, etc. to make font sizes sit in nicely.
            html_text_rendering: Can be enabled for sharper text display where required with drawback of weaker performance.
        """
        instance = Instance()
        Chart.__init__(self, instance)
        self.instance.send(
            self.id,
            'gaugeChart',
            {
                'theme': theme.value,
                'scaleTheme': theme_scale,
                'license': license or conf.LICENSE_KEY,
                'licenseInformation': license_information or conf.LICENSE_INFORMATION,
                'htmlTextRendering': html_text_rendering,
            },
        )
        self.set_angle_interval(angle_interval_start, angle_interval_end)
        if title:
            self.set_title(title)
        if start and end:
            self.set_interval(start, end)
        if value:
            self.set_value(value)

    def set_angle_interval(self, start: int | float, end: int | float):
        """Set angular interval of the gauge in degrees.

        Args:
            start (int | float): Start angle of the gauge in degrees.
            end (int | float): End angle of the gauge in degrees.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAngleInterval', {'start': start, 'end': end})
        return self

    def set_interval(self, start: int | float, end: int | float):
        """Set scale interval of the gauge slice.

        Args:
            start (int | float): Start scale value.
            end (int | float): End scale value.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setGaugeInterval', {'start': start, 'end': end})
        return self

    def set_value(self, value: int | float):
        """Set value of gauge slice.

        Args:
            value (int | float): Numeric value.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setGaugeValue', {'value': value})
        return self

    def set_automatic_bar_coloring(self, enabled: bool):
        """Enable or disable dynamic gauge bar coloring based on value indicators.
        If true, gauge bar is colored with the current indicator color.
        If false, gauge bar is always colored according to its "normal" color, set_bar_color

        Args:
            enabled (bool): Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAutomaticBarColoring', {'enabled': enabled})
        return self

    def set_bar_color(self, color: any):
        """Set the normal bar color, when not affected by value coloring.

        Args:
            color (Color): Color value.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setGaugeBarColor', {'color': color})
        return self

    def set_bar_effect(self, enabled: bool):
        """Set theme effect enabled on component or disabled.

        Args:
            enabled (bool): Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setBarEffect', {'enabled': enabled})
        return self

    def set_bar_gradient(self, enabled: bool):
        """Enable or disable gradient coloring for the gauge bar.
        If true, the active color of the Gauge Bar is mapped to a gradient color.
        If false, bar is always solid color.

        Args:
            enabled (bool): Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setBarGradient', {'enabled': enabled})
        return self

    def set_bar_stroke(self, thickness: int | float, color: any = None):
        """Set the stroke style of the gauge bar, i.e., the gauge bar border.

        Args:
            thickness (int | float): Thickness of the stroke.
            color (Color): Color of the stroke.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setBarStroke', {'thickness': thickness, 'color': color})
        return self

    def set_bar_thickness(self, pixels: int):
        """Set the thickness of the gauge bar.

        Args:
            pixels (int): Thickness in pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setBarThickness', {'pixels': pixels})
        return self

    def set_color_animation(self, enabled: bool, speed_multiplier: float = None):
        """Enable or disable color animations.

        Args:
            enabled (bool): Boolean flag.
            speed_multiplier (float): Optional value for adjusting the speed of the animation.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(
            self.id,
            'setColorAnimation',
            {'enabled': enabled, 'speedMultiplier': speed_multiplier},
        )
        return self

    def set_gap_between_bar_and_value_indicators(self, gap: int):
        """Set the distance between gauge bar and value indicators.

        Args:
            gap (int): Distance in pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setGapBetweenBarAndValueIndicators', {'gap': gap})
        return self

    def set_glow_color(self, arg: None | any | dict[str, any]):
        """Set the background glow color.
            arg: None = No background glow color.
            arg: Color = Use explicit glow color always.
            arg: { 'auto': true } = Automatically color with same color as gauge bar.

        Args:
            arg: None | Color | { auto: boolean, alpha: number }

        Returns:
            The instance of the class for fluent interface.
        """

        if arg is not None and not isinstance(arg, dict):
            arg = convert_color_to_hex(arg)

        self.instance.send(self.id, 'setGlowColor', {'arg': arg})
        return self

    def set_label_effect(self, enabled: bool):
        """Set theme effect enabled on component or disabled.

        Args:
            enabled (bool): Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setLabelEffect', {'enabled': enabled})
        return self

    def set_needle_alignment(self, offset: float):
        """Align the gauge needle from the gauge bar center.

        Args:
            offset (float): Numerical offset value between -1.0 and 1.0.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setNeedleAlignment', {'offset': offset})
        return self

    def set_needle_color(self, color: any):
        """Set the color of the gauge needle.

        Args:
            color (Color): Color value.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setNeedleColor', {'color': color})
        return self

    def set_needle_length(self, pixels: int):
        """Set the length of the gauge needle.

        Args:
            pixels (int): Length in pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setNeedleLength', {'pixels': pixels})
        return self

    def set_needle_stroke(self, thickness: int | float, color: any = None):
        """Set the stroke style of the needle edge.

        Args:
            thickness (int | float): Thickness of the needle stroke.
            color (Color): Color of the stroke.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(
            self.id,
            'setNeedleStroke',
            {'thickness': thickness, 'color': color},
        )
        return self

    def set_needle_thickness(self, thickness: int):
        """Set the thickness of the needle.

        Args:
            thickness (int): Thickness in pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setNeedleThickness', {'thickness': thickness})
        return self

    def set_rounded_edges(self, enabled: bool):
        """Enable or disable rounded edges for the gauge and value indicators.

        Args:
            enabled (bool): Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setRoundedEdgesEnabled', {'enabled': enabled})
        return self

    def set_tick_color(self, color: any):
        """Set the color of gauge ticks.

        Args:
            color (Color): Color value.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setTickColor', {'color': color})
        return self

    def set_tick_font(
        self,
        size: int | float,
        family: str = 'Segoe UI, -apple-system, Verdana, Helvetica',
        style: str = 'normal',
        weight: str = 'normal',
    ):
        """Set the font settings of gauge ticks.

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
            'setTickFont',
            {'family': family, 'size': size, 'weight': weight, 'style': style},
        )
        return self

    def set_tick_decimals(self, precision: int):
        """Set the decimal precision of gauge ticks.

        Args:
            precision (int): Number of decimal points.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTickDecimals', {'precision': precision})
        return self

    def set_unit_label(self, label: str):
        """Set the text of the unit label.

        Args:
            label (str): Unit label text.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setUnitLabel', {'label': label})
        return self

    def set_unit_label_color(self, color: any):
        """Set the color of the unit label.

        Args:
            color (Color): Color value.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setUnitLabelColor', {'color': color})
        return self

    def set_unit_label_font(
        self,
        size: int | float,
        family: str = 'Segoe UI, -apple-system, Verdana, Helvetica',
        style: str = 'normal',
        weight: str = 'normal',
    ):
        """Set the font settings of the unit label.

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
            'setUnitLabelFont',
            {'family': family, 'size': size, 'weight': weight, 'style': style},
        )
        return self

    def set_value_animation(self, enabled: bool, speed_multiplier: float = None):
        """Enable or disable value animations.

        Args:
            enabled (bool): Boolean flag.
            speed_multiplier (float): Optional value for adjusting the speed of the animation.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(
            self.id,
            'setValueAnimation',
            {'enabled': enabled, 'speedMultiplier': speed_multiplier},
        )
        return self

    def set_value_decimals(self, precision: int):
        """Set the decimal precision of the value label.

        Args:
            precision (int): Number of decimal points.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setValueDecimals', {'precision': precision})
        return self

    def set_value_indicator_thickness(self, pixels: int):
        """Set the thickness of the value indicators.

        Args:
            pixels (int): Thickness in pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setValueIndicatorThickness', {'pixels': pixels})
        return self

    def set_value_indicators(self, indicators: list[dict[str, any]]):
        """Set the value indicators of the gauge.

        Args:
            indicators: List of {start: number, end: number, color: Color} dictionaries.

        Returns:
            The instance of the class for fluent interface.
        """
        indicators = convert_to_dict(indicators)

        for i in indicators:
            if i['color']:
                i['color'] = convert_color_to_hex(i['color'])
        self.instance.send(self.id, 'setValueIndicators', {'indicators': indicators})
        return self

    def set_value_label_color(self, color: any):
        """Set the FillStyle of the value label.

        Args:
            color (Color): Color value.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setGaugeValueLabelColor', {'color': color})
        return self

    def set_value_label_font(
        self,
        size: int | float,
        family: str = 'Segoe UI, -apple-system, Verdana, Helvetica',
        style: str = 'normal',
        weight: str = 'normal',
    ):
        """Set the font settings of the value label.

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
            'setValueLabelFont',
            {'family': family, 'size': size, 'weight': weight, 'style': style},
        )
        return self


class GaugeChartDashboard(GaugeChart):
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
            'createGaugeChart',
            {
                'db': dashboard_id,
                'column': column,
                'row': row,
                'colspan': colspan,
                'rowspan': rowspan,
            },
        )
