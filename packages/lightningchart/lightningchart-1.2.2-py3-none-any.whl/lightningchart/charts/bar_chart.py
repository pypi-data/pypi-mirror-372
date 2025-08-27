from __future__ import annotations

import lightningchart
from lightningchart import conf, Themes
from lightningchart.charts import GeneralMethods, TitleMethods, Chart
from lightningchart.instance import Instance
from lightningchart.ui.axis import CategoryAxis, ValueAxis
from lightningchart.utils import convert_to_dict, convert_to_list, convert_color_to_hex


class BarChart(GeneralMethods, TitleMethods):
    """Chart type for visualizing categorical data as Bars."""

    def __init__(
        self,
        data: list[dict] = None,
        vertical: bool = True,
        axis_type: str = 'linear',
        axis_base: int = 10,
        title: str = None,
        theme: Themes = Themes.Light,
        theme_scale: float = 1.0,
        license: str = None,
        license_information: str = None,
        html_text_rendering: bool = False,
    ):
        """Create a bar chart.

        Args:
            data: List of {category, value} entries.
            vertical (bool): If true, bars are aligned vertically. If false, bars are aligned horizontally.
            axis_type (str): "linear" | "logarithmic"
            axis_base (int): Specification of Logarithmic Base number (e.g. 10, 2, natural log).
            title (str): The title of the chart.
            theme (Themes): The theme of the chart.
            license (str): License key.
            theme_scale: To up or downscale font sizes as well as tick lengths, element paddings, etc. to make font sizes sit in nicely.
            html_text_rendering: Can be enabled for sharper text display where required with drawback of weaker performance.
        """
        instance = Instance()
        Chart.__init__(self, instance)

        self.instance.send(
            self.id,
            'barChart',
            {
                'theme': theme.value,
                'scaleTheme': theme_scale,
                'vertical': vertical,
                'license': license or conf.LICENSE_KEY,
                'licenseInformation': license_information or conf.LICENSE_INFORMATION,
                'axisType': axis_type,
                'axisBase': axis_base,
                'htmlTextRendering': html_text_rendering,
            },
        )
        self.category_axis = CategoryAxis(self)
        self.value_axis = ValueAxis(self)
        if title:
            self.set_title(title)
        if data:
            self.set_data(data)

    def set_label_rotation(self, degrees: int):
        """Rotate the category labels.

        Args:
            degrees (int): Degree of the label rotation.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setBarChartLabelRotation', {'degrees': degrees})
        return self

    def set_data(self, data: list[dict]):
        """Set BarChart data, or update existing bars.

        Args:
            data (list[dict]): List of {category, value} entries.

        Returns:
            The instance of the class for fluent interface.
        """
        data = convert_to_dict(data)
        for i in data:
            if 'color' in i:
                i['color'] = convert_color_to_hex(i['color'])

        self.instance.send(self.id, 'setBarData', {'data': data})
        return self

    def set_data_grouped(self, categories: list[str], data: list[dict]):
        """Set BarChart data, updating the visible bars.
        This method accepts data for a Grouped Bar Chart, displaying it as such.

        Args:
            categories (list[str]): List of categories as strings.
            data: List of { "subCategory": str, "values" list[int | float] } dictionaries.

        Returns:
            The instance of the class for fluent interface.
        """
        categories = convert_to_list(categories)
        data = convert_to_dict(data)
        for i in data:
            if 'color' in i:
                i['color'] = convert_color_to_hex(i['color'])

        self.instance.send(self.id, 'setDataGrouped', {'categories': categories, 'data': data})
        return self

    def set_data_stacked(self, categories: list[str], data: list[dict]):
        """Set BarChart data, updating the visible bars.
        This method accepts data for a Stacked Bar Chart, displaying it as such.

        Args:
            categories (list[str]): List of categories as strings.
            data: List of { "subCategory": str, "values" list[int | float] } dictionaries.

        Returns:
            The instance of the class for fluent interface.
        """
        categories = convert_to_list(categories)
        data = convert_to_dict(data)
        for i in data:
            if 'color' in i:
                i['color'] = convert_color_to_hex(i['color'])

        self.instance.send(self.id, 'setDataStacked', {'categories': categories, 'data': data})
        return self

    def set_value_labels(
        self,
        enabled: bool = True,
        position: str = None,
        color: any = None,
        font_size: int = None,
        font_family: str = None,
        font_weight: str = None,
        font_style: str = None,
        rotation: float = None,
        format_type: str = 'standard',
        precision: int = None,
        unit: str = None,
        scale: float = 1.0,
        currency_symbol: str = None,
        show_category: bool = False,
        display_stacked_sum: bool = None,
        display_stacked_individuals: bool = None,
    ):
        """
        Configure how value labels are displayed in the BarChart.

        Args:
            enabled (bool): Whether to show value labels. If False, hides all labels.
            position (str, optional): Label position: 'after-bar', 'inside-bar', 'inside-bar-centered', 'before-bar'
            color (Color, optional): Label text color
            font_size (int, optional): Font size in pixels
            font_family (str, optional): Font family name
            font_weight (str, optional): Font weight ('normal', 'bold')
            font_style (str, optional): Font style ('normal', 'italic')
            rotation (float, optional): Label rotation in degrees
            format_type (str): Format style:
                - 'standard': Normal number formatting (default)
                - 'currency': Currency formatting with symbol
                - 'percentage': Percentage formatting (value * 100 + %)
                - 'thousands': Compact notation (K, M, B, T)
                - 'integer': Rounded integer values
            precision (int, optional): Number of decimal places (None = auto)
            unit (str, optional): Unit to append (e.g., "kg", "ms", "items")
            scale (float): Scale factor to multiply value (default: 1.0)
            currency_symbol (str, optional): Currency symbol for currency format (default: "$")
            show_category (bool): Whether to include category name in label
            display_stacked_sum (bool, optional): Show sum labels for stacked bars
            display_stacked_individuals (bool, optional): Show individual labels for stacked bars

        Examples:
            # Rotated labels
            chart.set_value_labels(position='after-bar', rotation=45, format_type='currency', precision=0))

            # Stacked bar labels
            chart.set_value_labels(position='inside-bar', display_stacked_individuals=True, display_stacked_sum=True, format_type='currency', precision=2)

            # Currency formatting
            chart.set_value_labels(format_type='currency', currency_symbol='€', precision=0)

            # Percentage formatting
            chart.set_value_labels(format_type='percentage', precision=1)

        Returns:
            The instance of the class for fluent interface.
        """

        config = {
            'enabled': enabled,
            'position': position,
            'color': convert_color_to_hex(color) if color else None,
            'fontSize': font_size,
            'fontFamily': font_family,
            'fontWeight': font_weight,
            'fontStyle': font_style,
            'rotation': rotation,
            'formatType': format_type,
            'precision': precision,
            'unit': unit,
            'scale': scale,
            'currencySymbol': currency_symbol,
            'showCategory': show_category,
            'displayStackedSum': display_stacked_sum,
            'displayStackedIndividuals': display_stacked_individuals,
        }

        config = {k: v for k, v in config.items() if v is not None}

        self.instance.send(self.id, 'setValueLabels', config)
        return self

    def set_category_axis_labels(
        self,
        size: int | float,
        family: str = None,
        style: str = None,
        weight: str = None,
        color: any = None,
        rotation: float = None,
    ):
        """Set font of Chart category axis labels (X-axis labels in vertical bar charts).

        Args:
            size (int | float): CSS font size in pixels. For example, 16.
            family (str, optional): CSS font family. For example, 'Arial, Helvetica, sans-serif'.
            style (str, optional): CSS font style. Options: 'normal', 'italic', 'oblique'.
            weight (str, optional): CSS font weight. Options: 'normal', 'bold', 'bolder', 'lighter'.
            color (Color, optional): Label text color. Default: None (uses chart theme default).
            rotation (float, optional): Label rotation in degrees. Positive values rotate clockwise.

        Returns:
            The instance of the class for fluent interface.

        Examples:
            # Basic usage - set font size
            chart.category_axis.set_category_axis_label_font(size=14)

            # Bold labels with custom color
            chart.category_axis.set_category_axis_label_font(
                size=12,
                weight='bold',
                color='darkblue'
            )

            # Rotated labels for long category names
            chart.category_axis.set_category_axis_label_font(
                size=10,
                rotation=45,
                weight='bold'
            )

            # Complete customization
            chart.category_axis.set_category_axis_label_font(
                size=16,
                family='Arial',
                style='italic',
                weight='bold',
                color='#ff6600',
                rotation=30
            )
        """
        config = {'family': family, 'size': size, 'weight': weight, 'style': style}

        if color is not None:
            config['color'] = convert_color_to_hex(color)

        if rotation is not None:
            config['degrees'] = rotation

        self.instance.send(self.id, 'setCategoryAxisLabelFont', config)
        return self

    def set_value_axis_labels(
        self,
        major_size: int | float = None,
        minor_size: int | float = None,
        family: str = None,
        style: str = None,
        weight: str = None,
        major_color: lightningchart.Color = None,
        minor_color: lightningchart.Color = None,
        major_rotation: float = None,
        minor_rotation: float = None,
    ):
        """Set font of value axis tick labels (Y-axis labels in vertical bar charts).

        Args:
            major_size (int | float, optional): Font size for major tick labels in pixels.
            minor_size (int | float, optional): Font size for minor tick labels in pixels.
            family (str, optional): CSS font family for both major and minor tick labels.
            style (str, optional): CSS font style for both major and minor tick labels.
            weight (str, optional): CSS font weight for both major and minor tick labels.
            major_color (Color, optional): Text color for major tick labels.
            minor_color (Color, optional): Text color for minor tick labels.
            major_rotation (float, optional): Rotation angle in degrees for major tick labels.
                Positive values rotate clockwise. Useful for long numeric formats or units.
            minor_rotation (float, optional): Rotation angle in degrees for minor tick labels.

        Returns:
            The instance of the class for fluent interface.

        Examples:
            # Different sizes for major and minor ticks
            chart.value_axis.set_value_axis_label_font(major_size=12, minor_size=10)

            # Rotate major tick labels (useful for long numbers/units)
            chart.value_axis.set_value_axis_label_font(
                major_size=12,
                major_rotation=45,
                major_color=lc.Color('black')
            )

            # Different rotations for major and minor ticks
            chart.value_axis.set_value_axis_label_font(
                major_size=12,
                minor_size=9,
                major_rotation=30,
                minor_rotation=15,
                major_color=lc.Color('darkblue'),
                minor_color=lc.Color('gray')
            )

            # Professional look with rotated labels
            chart.value_axis.set_value_axis_label_font(
                major_size=12,
                minor_size=9,
                weight='bold',
                major_color=lc.Color('#2c3e50'),
                minor_color=lc.Color('#7f8c8d'),
                major_rotation=0,    # No rotation for major
                minor_rotation=90    # Vertical minor labels
            )

            # Rotated labels for currency or percentage values
            chart.value_axis.set_value_axis_label_font(
                major_size=11,
                minor_size=8,
                major_rotation=45,
                minor_rotation=45,
                major_color=lc.Color('darkgreen'),
                minor_color=lc.Color('green')
            )

            # Scientific notation with rotation
            chart.value_axis.set_value_axis_label_font(
                major_size=10,
                minor_size=8,
                family='monospace',
                major_rotation=30,
                minor_rotation=30,
                major_color=lc.Color('navy'),
                minor_color=lc.Color('blue')
            )
        """
        config = {}

        if family is not None:
            config['family'] = family
        if style is not None:
            config['style'] = style
        if weight is not None:
            config['weight'] = weight
        if major_size is not None:
            config['majorSize'] = major_size
        if minor_size is not None:
            config['minorSize'] = minor_size
        if major_rotation is not None:
            config['majorRotation'] = major_rotation
        if minor_rotation is not None:
            config['minorRotation'] = minor_rotation
        if major_color is not None:
            config['majorColor'] = convert_color_to_hex(major_color)
        if minor_color is not None:
            config['minorColor'] = convert_color_to_hex(minor_color)

        self.instance.send(self.id, 'setBarValueAxisLabelFont', config)
        return self

    def set_value_label_color(self, color: any):
        """Set the color of value labels.

        Args:
            color (Color): Color of the labels.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setValueLabelColor', {'color': color})
        return self

    def set_value_label_font_size(self, size: int | float):
        """Set the font size of value labels.

        Args:
            size (int | float): Font size of the labels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setValueLabelFontSize', {'size': size})
        return self

    def set_sorting(self, mode: str):
        """Configure automatic sorting of bars.

        Args:
            mode: "disabled" | "ascending" | "descending" | "alphabetical"

        Returns:
            The instance of the class for fluent interface.
        """
        sorting_modes = ('disabled', 'ascending', 'descending', 'alphabetical')
        if mode not in sorting_modes:
            raise ValueError(f"Expected mode to be one of {sorting_modes}, but got '{mode}'.")

        self.instance.send(self.id, 'setSorting', {'mode': mode})
        return self

    def set_label_fitting(self, enabled: bool):
        """Enable or disable automatic label fitting.

        Args:
            enabled (bool): If true, labels will not overlap.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setLabelFitting', {'enabled': enabled})
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

    def set_series_background_color(self, color: any):
        """Set chart series background color.

        Args:
            color (Color): Color of the series background.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setSeriesBackgroundFillStyle', {'color': color})
        return self

    def set_animation_category_position(self, enabled: bool):
        """Enable/disable animation of bar category positions. This is enabled by default.

        Args:
            enabled (bool): Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAnimationCategoryPosition', {'enabled': enabled})
        return self

    def set_animation_values(self, enabled: bool):
        """Enable/disable animation of bar values. This is enabled by default.

        Args:
            enabled (bool): Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAnimationValues', {'enabled': enabled})
        return self

    def set_bars_effect(self, enabled: bool):
        """Set theme effect enabled on component or disabled.

        Args:
            enabled (bool): Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setBarsEffect', {'enabled': enabled})
        return self

    def set_bars_margin(self, margin: int | float):
        """Set margin around each bar along category axis as percentage of the bar thickness.
        For example, 0.1 = on both left and right side of bar there is a 10% margin.
        Actual thickness of bar depends on chart size, but for 100 px bar that would be 10 px + 10 px margin.
        Valid value range is between [0, 0.49].

        Args:
            margin (int | float): Margin around each bar along category axis as percentage of bar thickness.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setBarsMargin', {'margin': margin})
        return self

    def set_bar_color(self, category: str, color: any):
        """Set the color value of a single category bar.

        Args:
            category (str): Category name.
            color (Color): Color value.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setBarColor', {'category': category, 'color': color})
        return self

    def set_subcategory_color(self, category: str, subcategory: str, color: any):
        """Set the color value of a single category bar.

        Args:
            category (str): Category name.
            subcategory (str): Subcategory name.
            color (Color): Color value.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(
            self.id,
            'setSubCategoryColor',
            {
                'category': category,
                'subCategory': subcategory,
                'color': color,
            },
        )
        return self

    def set_bars_color(self, color: any):
        """Set the color value of all bars.

        Args:
            color: Color value.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setBarsColor', {'color': color})
        return self

    def set_palette_colors(
        self,
        steps: list[dict[str, any]],
        percentage_values: bool = True,
        interpolate: bool = True,
        look_up_property: str = 'y',
    ):
        """Define a palette coloring for the bars.

        Args:
            steps (list[dict]): List of {"value": number, "color": Color} dictionaries.
            interpolate (bool): Enables automatic linear interpolation between color steps.
            percentage_values (bool): Whether values represent percentages or explicit values.
            look_up_property (str): "value" | "x" | "y" | "z"

        Returns:
            The instance of the class for fluent interface.
        """
        for i in steps:
            if 'color' in i:
                i['color'] = convert_color_to_hex(i['color'])

        self.instance.send(
            self.id,
            'setPalettedBarColor',
            {
                'steps': steps,
                'lookUpProperty': look_up_property,
                'interpolate': interpolate,
                'percentageValues': percentage_values,
            },
        )
        return self


class BarChartDashboard(BarChart):
    def __init__(
        self,
        instance: Instance,
        dashboard_id: str,
        column: int,
        row: int,
        colspan: int,
        rowspan: int,
        vertical: bool,
        axis_type: str,
        axis_base: int,
    ):
        Chart.__init__(self, instance)
        self.instance.send(
            self.id,
            'createBarChart',
            {
                'db': dashboard_id,
                'column': column,
                'row': row,
                'colspan': colspan,
                'rowspan': rowspan,
                'vertical': vertical,
                'axisType': axis_type,
                'axisBase': axis_base,
            },
        )
        self.category_axis = CategoryAxis(self)
        self.value_axis = ValueAxis(self)
