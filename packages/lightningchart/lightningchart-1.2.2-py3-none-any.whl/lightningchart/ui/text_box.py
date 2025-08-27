from __future__ import annotations

from lightningchart.ui import UIEWithPosition, UIElement
from lightningchart.utils import convert_to_base64, convert_color_to_hex


class TextBox(UIEWithPosition):
    """UI Element for adding text annotations on top of the chart."""

    def __init__(
        self,
        chart,
        text: str = None,
        x: int = None,
        y: int = None,
        position_scale: str = 'axis',
    ):
        UIElement.__init__(self, chart)
        self.instance.send(
            self.id,
            'textBox',
            {'chart': self.chart.id, 'positionScale': position_scale},
        )

        if text:
            self.set_text(text)
        if x is not None and y is not None:
            self.set_position(x, y)

    def set_text(self, text: str):
        """Set the content of the text box.

        Args:
            text (str): Text string.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setText', {'text': text})
        return self

    def set_padding(self, *args, **kwargs):
        """Set padding around object in pixels.

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

    def set_text_fill_style(self, color: any):
        """Set the color of the text.

        Args:
            color (Color): Color of the text.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setTextFillStyle', {'color': color})
        return self

    def set_text_font(
        self,
        size: int | float,
        family: str = 'Segoe UI, -apple-system, Verdana, Helvetica',
        style: str = 'normal',
        weight: str = 'normal',
    ):
        """Set the font style of the text.

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
            'setTextFont',
            {'family': family, 'size': size, 'weight': weight, 'style': style},
        )
        return self

    def set_text_rotation(self, rotation: int | float):
        """Set the rotation of the text.

        Args:
            rotation (int | float): Rotation in degrees.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTextRotation', {'rotation': rotation})
        return self

    def set_background_color(self, color: any):
        """Set the background color of the text box.

        Args:
            color (Color): Color of the background.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setBackgroundFill', {'color': color})
        return self

    def set_stroke(self, thickness: int | float, color: any = None):
        """Set the text box stroke style.

        Args:
            thickness (int | float): Thickness of the stroke.
            color (Color): Color of the stroke.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(
            self.id,
            'setBackgroundStroke',
            {'thickness': thickness, 'color': color},
        )
        return self

    def add_video(
        self,
        video_source: str,
        fit_mode: str = 'fit',
        size: dict = None,
    ):
        """
        Updates the background of the current TextBox UI element to use a video
        (provided as a Base64-encoded data URI) as its fill.

        Args:
            video_source (str): Path to the video file (MP4 or WEBM) or URL.
            fit_mode (str): How the video should fit ('fit', 'stretch', etc.).
            size (dict, optional): Desired size of the video display, e.g. {"width": 150, "height": 150}.
                                   This controls the UI element's padding. Defaults to 100x100.

        Returns:
            self: The instance for fluent interfacing.

        Example:
            >>> textbox.add_video("D:/path/to/local_video.mp4")
            >>> textbox.add_video("https://example.com/video.mp4")
        """

        if not video_source:
            raise ValueError('Video source is required.')

        video_data_uri = convert_to_base64(video_source)

        args = {
            'videoSource': video_data_uri,
            'fitMode': fit_mode,
            'size': size or {'width': 100, 'height': 100},
        }
        self.instance.send(self.id, 'addCustomVideo', args)
        return self

    def add_image(
        self,
        source: str,
        fit_mode: str = 'Stretch',
        size: dict = None,
    ):
        """
        Updates the background of the current TextBox UI element to use an image
        (provided as a Base64-encoded data URI) as its fill.

        Args:
            source (str): Path to the image file or URL.
            fit_mode (str): How the image should fit ('Stretch', 'Fill', 'Fit', etc.).
            size (dict, optional): Desired size of the image display, e.g. {"width": 100, "height": 100}.
                                   Defaults to 100x100.

        Returns:
            self: The instance for fluent interfacing.

        Example:
            >>> textbox.add_image("D:/path/to/local_image.png")
            >>> textbox.add_image("https://example.com/image.jpg")
        """
        if not source:
            raise ValueError('Image source is required.')

        image_data_uri = convert_to_base64(source)

        args = {
            'source': image_data_uri,
            'fitMode': fit_mode,
            'size': size or {'width': 100, 'height': 100},
        }

        self.instance.send(self.id, 'addCustomImage', args)
        return self

    def set_effect(self, enabled: bool):
        """Set theme effect enabled on component or disabled.

        Args:
            enabled: Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setEffect', {'enabled': enabled})
        return self
