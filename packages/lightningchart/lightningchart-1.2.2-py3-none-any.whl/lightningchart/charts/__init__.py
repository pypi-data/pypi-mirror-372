from __future__ import annotations
import datetime
import uuid

from lightningchart.instance import Instance
from lightningchart.series import Series
from lightningchart.ui.axis import DefaultAxis, DefaultAxis3D, Axis
from lightningchart.ui.legend import Legend
from lightningchart.ui.text_box import TextBox
from lightningchart.utils import convert_to_base64, convert_color_to_hex


class Chart:
    def __init__(self, instance: Instance):
        self.id = str(uuid.uuid4()).split('-')[0]
        self.instance = instance

    def open(
        self,
        method: str = None,
        live=False,
        width: int | str = '100%',
        height: int | str = 600,
    ):
        """Open the rendering view.
        Method "browser" will open the chart in your browser.
        Method "notebook" will display the chart in a notebook environment with an IFrame component.
        Method "link" will return a URL of the chart that can be used to embed it in external applications.

        Args:
            method (str): "browser" | "notebook"
            live (bool): Whether to use real-time rendering or not.
            width (int): The width of the IFrame component in pixels.
            height (int): The height of the IFrame component in pixels.

        Returns:
            self | str: Returns a URL string if method is "link", otherwise returns the class instance.
        """
        return self.instance.open(method=method, live=live, width=width, height=height) or self

    def close(self):
        """Close the connection to a chart with real-time display mode.

        Note: This will terminate the current Python instance!
        """
        self.instance.close()
        return self

    def set_data_preservation(self, enabled: bool):
        """Enable or disable server-side data preservation for real-time visualization use cases.

        Enabled by default!

        Args:
            enabled (bool): Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.set_data_preservation(enabled)
        return self


class GeneralMethods(Chart):
    def save_to_file(
        self,
        file_name: str = None,
        image_format: str = 'image/png',
        image_quality: float = 0.92,
    ):
        """Save the current rendering view as a screenshot.

        Args:
            file_name (str): Name of prompted download file as string. File extension shouldn't be included as it is
                automatically detected from 'type'-argument.
            image_format (str): A DOMString indicating the image format. The default format type is image/png.
            image_quality (float): A Number between 0 and 1 indicating the image quality to use for image formats that
                use lossy compression such as image/jpeg and image/webp. If this argument is anything else,
                the default value for image quality is used. The default value is 0.92.

        Returns:
            The instance of the class for fluent interface.
        """
        if file_name is None:
            file_name = f'LightningChart_Python_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'
        self.instance.send(
            self.id,
            'saveToFile',
            {
                'fileName': file_name,
                'type': image_format,
                'encoderOptions': image_quality,
            },
        )
        return self

    def dispose(self):
        """Permanently destroy the component."""
        self.instance.send(self.id, 'dispose')

    def set_animations_enabled(self, enabled: bool = True):
        """Disable/Enable all animations of the Chart.

        Args:
            enabled (bool): Boolean value to enable or disable animations.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAnimationsEnabled', {'enabled': enabled})
        return self

    def set_padding(self, *args, **kwargs):
        """Set padding around the chart in pixels.

        Usage:
            - `set_padding(5)`: Sets uniform padding for all sides (integer or float).
            - `set_padding(left=10, top=15)`: Sets padding for specific sides only.
            - `set_padding(left=10, top=15, right=20, bottom=25)`: Fully define padding for all sides.

        Args:
            *args: A single numeric value (int or float) for uniform padding on all sides.
            **kwargs: Optional named arguments to specify padding for individual sides:
                - `left` (int or float): Padding for the left side.
                - `right` (int or float): Padding for the right side.
                - `top` (int or float): Padding for the top side.
                - `bottom` (int or float): Padding for the bottom side.

        Returns:
            The instance of the class for fluent interface.
        """
        if len(args) == 1 and isinstance(args[0], (int, float)):
            padding = args[0]
        elif kwargs:
            padding = {}
            for key in ['left', 'right', 'bottom', 'top']:
                if key in kwargs:
                    padding[key] = kwargs[key]
        else:
            raise ValueError(
                'Invalid arguments. Use one of the following formats:\n'
                '- set_padding(5): Uniform padding for all sides.\n'
                '- set_padding(left=10, top=15): Specify individual sides.\n'
                '- set_padding(left=10, top=15, right=20, bottom=25): Full padding definition.'
            )

        self.instance.send(self.id, 'setPadding', {'padding': padding})
        return self

    def set_background_color(self, color: any):
        """Set the background color of the chart.

        Args:
            color (Color): Color of the background.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setBackgroundFillStyle', {'color': color})
        return self

    def set_background_stroke(self, thickness: int | float, color: any = None):
        """Set the background stroke style of the chart.

        Args:
            thickness (int | float): Thickness of the stroke.
            color (Color): The color of the stroke.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(
            self.id,
            'setBackgroundStrokeStyle',
            {'thickness': thickness, 'color': color},
        )
        return self

    def add_legend(
        self,
        horizontal: bool = False,
        title: str = None,
        data: Chart | Series = None,
        x: int = None,
        y: int = None,
        position_scale: str = 'percentage',
    ) -> Legend:
        """Add legend box to the chart.

        Args:
            horizontal (bool): Whether the legend box is horizontally aligned or not.
            title (str): Title of the legend.
            data (Chart/Series): Reference either to Chart of Series class which the legend will display.
            x (int): X position in percentages (0-100).
            y (int): Y position in percentages (0-100).
            position_scale (str): "percentage" | "pixel" | "axis"

        Returns:
            Reference to Legend Box class.
        """
        return Legend(
            chart=self,
            horizontal=horizontal,
            title=title,
            data=data,
            x=x,
            y=y,
            position_scale=position_scale,
        )

    legend = add_legend

    def add_textbox(
        self,
        text: str = None,
        x: int = None,
        y: int = None,
        position_scale: str = 'axis',
    ):
        """Add text box to the chart.

        Args:
            text (str): Text of the text box.
            x (int): X position in percentages (0-100).
            y (int): Y position in percentages (0-100).
            position_scale (str): "percentage" | "pixel" | "axis"

        Returns:
            Reference to Text Box class.
        """
        return TextBox(chart=self, text=text, x=x, y=y, position_scale=position_scale)

    textbox = add_textbox


class TitleMethods(Chart):
    def set_title(self, title: str):
        """Set text of Chart title.

        Args:
            title (str): Chart title as a string.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTitle', {'title': title})
        return self

    def hide_title(self):
        """Hide title and remove padding around it.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'hideTitle')
        return self

    def set_title_color(self, color: any):
        """Set color of Chart title.

        Args:
            color (Color): Color of the title.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setTitleColor', {'color': color})
        return self

    def set_title_font(
        self,
        size: int | float,
        family: str = 'Segoe UI, -apple-system, Verdana, Helvetica',
        style: str = 'normal',
        weight: str = 'normal',
    ):
        """Set font of Chart title.

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
            'setTitleFont',
            {'family': family, 'size': size, 'weight': weight, 'style': style},
        )
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

    def set_title_rotation(self, degrees: int | float):
        """Set rotation of Chart title.

        Args:
            degrees (int | float): Rotation in degrees.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTitleRotation', {'value': degrees})
        return self

    def set_title_effect(self, enabled: bool = True):
        """Set theme effect enabled on component or disabled.

        Args:
            enabled (bool): Theme effect enabled.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTitleEffect', {'enabled': enabled})
        return self


class ChartWithXYAxis(Chart):
    def __init__(self):
        self.default_x_axis = DefaultAxis(self, 'x')
        self.default_y_axis = DefaultAxis(self, 'y')

    def get_default_x_axis(self) -> Axis:
        """Get the reference to the default x-axis of the chart.

        Returns:
            Reference to Axis class.
        """
        return self.default_x_axis

    def get_default_y_axis(self) -> Axis:
        """Get the reference to the default y-axis of the chart.

        Returns:
            Reference to Axis class.
        """
        return self.default_y_axis

    def synchronize_axis_intervals(self, axis_array: list[Axis]):
        """Convenience function for synchronizing the intervals of n amount of ´Axis´.

        Args:
            axis_array (list[Axis]): List of Axis to synchronize.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'synchronizeAxes', {'axes': axis_array})
        return self


class ChartWithXYZAxis(Chart):
    def __init__(self):
        self.default_x_axis = DefaultAxis3D(self, 'x')
        self.default_y_axis = DefaultAxis3D(self, 'y')
        self.default_z_axis = DefaultAxis3D(self, 'z')

    def get_default_x_axis(self) -> DefaultAxis3D:
        """Get the reference to the default x-axis of the chart.

        Returns:
            Reference to Axis3D class.
        """
        return self.default_x_axis

    def get_default_y_axis(self) -> DefaultAxis3D:
        """Get the reference to the default y-axis of the chart.

        Returns:
            Reference to Axis3D class.
        """
        return self.default_y_axis

    def get_default_z_axis(self) -> DefaultAxis3D:
        """Get the reference to the default y-axis of the chart.

        Returns:
            Reference to Axis3D class.
        """
        return self.default_z_axis


class ChartWithSeries(Chart):
    def __init__(self, instance: Instance):
        Chart.__init__(self, instance)
        self.series_list = []

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
        """Set the color of chart series background.

        Args:
            color (Color): Color of the series background.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setSeriesBackgroundFillStyle', {'color': color})
        return self


class ChartWithLUT(Chart):
    def set_lookup_table(
        self,
        steps: list[dict[str, any]],
        interpolate: bool = True,
        percentage_values: bool = False,
    ):
        """Attach lookup table (LUT) to fill the slices with Colors based on value.

        Args:
            steps (list[dict]): List of {"value": number, "color": Color} dictionaries.
            interpolate (bool): Whether color interpolation is used
            percentage_values (bool): Whether values represent percentages or explicit values.

        Returns:
            The instance of the class for fluent interface.
        """
        for i in steps:
            if 'color' in i:
                i['color'] = convert_color_to_hex(i['color'])

        self.instance.send(
            self.id,
            'setLUT',
            {
                'steps': steps,
                'interpolate': interpolate,
                'percentageValues': percentage_values,
            },
        )
        return self


class ChartWithLabelStyling(Chart):
    def set_label_formatter(self, formatter: str = 'NamePlusValue'):
        """Set formatter of Slice Labels.

        Args:
            formatter: "Name" | "NamePlusValue" | "NamePlusRelativeValue"

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setLabelFormatter', {'formatter': formatter})
        return self

    def set_label_color(self, color: any):
        """Set the color of Slice Labels.

        Args:
            color (Color): Color of the labels.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setLabelColor', {'color': color})
        return self

    def set_label_font(
        self,
        size: int | float,
        family: str = 'Segoe UI, -apple-system, Verdana, Helvetica',
        style: str = 'normal',
        weight: str = 'normal',
    ):
        """Set font of Slice Labels.

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
            'setLabelFont',
            {'family': family, 'size': size, 'weight': weight, 'style': style},
        )
        return self

    def set_label_effect(self, enabled: bool):
        """Set theme effect enabled on label or disabled. A theme can specify an Effect to add extra visual
        oomph to chart applications, like Glow effects around data or other components.

        Args:
            enabled (bool): Theme effect enabled.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setLabelEffect', {'enabled': enabled})
        return self

    def set_slice_effect(self, enabled: bool):
        """Set theme effect enabled on slice or disabled. A theme can specify an Effect to add extra visual
        oomph to chart applications, like Glow effects around data or other components.

        Args:
            enabled (bool): Theme effect enabled.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setSliceEffect', {'enabled': enabled})
        return self

    def set_slice_colors(self, color_list: list[any]):
        """Set the colors of all slices at once.

        Args:
            color_list (list[Color]): list of Colors. The length must match the current number of slices!

        Returns:
            The instance of the class for fluent interface.
        """
        hex_array = []
        for color in color_list:
            hex_array.append(convert_color_to_hex(color))

        self.instance.send(self.id, 'setSliceFuncFillStyle', {'hexArray': hex_array})
        return self

    def set_slice_sorter(self, sorter: str):
        """Define the sorting logic for slices.

        Args:
            sorter (str): "name" | "valueAscending" | "valueDescending" | "none"

        Returns:
            The instance of the class for fluent interface.
        """
        slice_sorters = ('name', 'valueAscending', 'valueDescending', 'none')
        if sorter not in slice_sorters:
            raise ValueError(f"Expected sorter to be one of {slice_sorters}, but got '{sorter}'.")

        self.instance.send(self.id, 'setSliceSorter', {'sorter': sorter})
        return self

    def set_label_connector_gap(self, gap: int | float):
        """Set gap between Slice / start of label connector, and end of label connector / Label.

        Args:
            gap (int | float): Gap as pixels.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setLabelConnectorGap', {'gap': gap})
        return self

    def set_label_connector_style(self, style: str, thickness: int | float, color: any = None):
        """Set style of Label connector lines.

        Args:
            style (str): "solid" | "dashed" | "empty"
            thickness (int | float): Thickness of the connector line.
            color (Color): Color of the connector line.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        styles = ('solid', 'dashed', 'empty')
        if style not in styles:
            raise ValueError(f"Expected sorter to be one of {styles}, but got '{style}'.")

        self.instance.send(
            self.id,
            'setLabelConnectorStyle',
            {'style': style, 'thickness': thickness, 'color': color},
        )
        return self


class BackgroundChartStyle(Chart):
    def set_chart_background_image(
        self,
        source: str,
        fit_mode: str = 'Stretch',
        surrounding_color=None,
        source_missing_color=None,
    ):
        """
        Set the chart background image.

        Args:
            source (str): The image source. This can be:
                - A URL (remote image).
                - A local file path.
                - An already Base64-encoded image string.
            fit_mode (str, optional): Fit mode for the image. Options:
                - "Stretch" (default)
                - "Fill"
                - "Fit"
                - "Tile"
                - "Center"
            surrounding_color (Color, optional): Color for areas outside the image.
            source_missing_color (Color, optional): Color when the image fails to load.

        Returns:
            self: The instance of the class for method chaining.

        Raises:
            ValueError: If the source is invalid.

        Example:
            >>> chart.set_chart_background_image("D:/path/to/local_image.png")
            >>> chart.set_chart_background_image("https://example.com/image.jpg")
        """

        if not source:
            raise ValueError('Image source is required.')
        if not source.startswith('data:'):
            source = convert_to_base64(source)

        args = {
            'source': source,
            'fitMode': fit_mode,
            'surroundingColor': convert_color_to_hex(surrounding_color) if surrounding_color else None,
            'sourceMissingColor': convert_color_to_hex(source_missing_color) if source_missing_color else None,
        }

        self.instance.send(self.id, 'setChartBackgroundImage', args)
        return self

    def set_chart_background_video(
        self,
        video_source: str,
        fit_mode: str = 'fit',
        surrounding_color: any = None,
        source_missing_color: any = None,
    ):
        """
        Sets the chart background to a video.

        Args:
            video_source (str): Path to the video file (MP4 or WEBM).
            fit_mode (str): Fit mode ('fit', 'stretch', 'fill', 'center', etc.).
            surrounding_color (Color, optional): Color for areas outside the video.
            source_missing_color (Color, optional): Color when video fails to load.

        Returns:
            The instance of the class for method chaining.

        Example:
            >>> chart.set_chart_background_video("D:/path/to/local_video.mp4")
            >>> chart.set_chart_background_video("https://example.com/video.mp4")
        """

        if not video_source:
            raise ValueError('Video source is required.')
        video_data_uri = convert_to_base64(video_source)

        surrounding_color = convert_color_to_hex(surrounding_color) if surrounding_color is not None else None
        source_missing_color = convert_color_to_hex(source_missing_color) if source_missing_color is not None else None

        args = {
            'videoSource': video_data_uri,
            'fitMode': fit_mode,
            'surroundingColor': surrounding_color if surrounding_color else None,
            'sourceMissingColor': source_missing_color if source_missing_color else None,
        }
        self.instance.send(self.id, 'setChartBackgroundVideo', args)
        return self

    def set_series_background_image(
        self,
        source: str,
        fit_mode: str = 'Stretch',
        surrounding_color=None,
        source_missing_color=None,
    ):
        """
        Set the series background image.

        Args:
            source (str): The image source. This can be:
                - A URL (remote image).
                - A local file path.
                - An already Base64-encoded image string.
            fit_mode (str, optional): Fit mode for the image. Options:
                - "Stretch" (default)
                - "Fill"
                - "Fit"
                - "Tile"
                - "Center"
            surrounding_color (Color, optional): Color for areas outside the image.
            source_missing_color (Color, optional): Color when the image fails to load.

        Returns:
            self: The instance of the class for method chaining.

        Raises:
            ValueError: If the source is invalid.

        Example:
            >>> chart.set_series_background_image("D:/path/to/local_image.png")
            >>> chart.set_series_background_image("https://example.com/image.jpg")
        """
        if not source:
            raise ValueError('Image source is required.')
        if not source.startswith('data:'):
            source = convert_to_base64(source)

        args = {
            'source': source,
            'fitMode': fit_mode,
            'surroundingColor': convert_color_to_hex(surrounding_color) if surrounding_color else None,
            'sourceMissingColor': convert_color_to_hex(source_missing_color) if source_missing_color else None,
        }
        self.instance.send(self.id, 'setSeriesBackgroundImage', args)
        return self

    def set_series_background_video(
        self,
        video_source: str,
        fit_mode: str = 'fit',
        surrounding_color: any = None,
        source_missing_color: any = None,
    ):
        """
        Sets the series background to a video.

        Args:
            video_source (str): Path to the video file (MP4 or WEBM).
            fit_mode (str): Fit mode ('fit', 'stretch', 'fill', 'center', etc.).
            surrounding_color (Color, optional): Color for areas outside the video.
            source_missing_color (Color, optional): Color when video fails to load.

        Returns:
            The instance of the class for method chaining.

        Example:
            >>> chart.set_series_background_video("D:/path/to/local_video.mp4")
            >>> chart.set_series_background_video("https://example.com/video.mp4")
        """
        if not video_source:
            raise ValueError('Video source is required.')
        video_data_uri = convert_to_base64(video_source)

        surrounding_color = convert_color_to_hex(surrounding_color) if surrounding_color is not None else None
        source_missing_color = convert_color_to_hex(source_missing_color) if source_missing_color is not None else None

        args = {
            'videoSource': video_data_uri,
            'fitMode': fit_mode,
            'surroundingColor': surrounding_color if surrounding_color else None,
            'sourceMissingColor': source_missing_color if source_missing_color else None,
        }
        self.instance.send(self.id, 'setSeriesBackgroundVideo', args)
        return self
