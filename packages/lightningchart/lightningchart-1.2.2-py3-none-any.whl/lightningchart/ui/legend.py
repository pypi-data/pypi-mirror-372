from __future__ import annotations

from lightningchart.ui import UIEWithPosition, UIEWithTitle, UIElement
from lightningchart.utils import convert_color_to_hex


class Legend(UIEWithPosition, UIEWithTitle):
    """Class for legend boxes in a chart."""

    def __init__(
        self,
        chart,
        horizontal: bool = False,
        title: str = None,
        data=None,
        x: int = None,
        y: int = None,
        position_scale: str = 'percentage',
    ):
        UIElement.__init__(self, chart)
        self.instance.send(
            self.id,
            'legend',
            {
                'chart': chart.id,
                'horizontal': horizontal,
                'positionScale': position_scale,
            },
        )
        if title:
            self.set_title(title)
        if data:
            self.add(data)
        if x and y:
            self.set_position(x, y)

    def add(self, data):
        """Add a dynamic value to LegendBox, creating a group and entries for it depending on type of value.
        Supports series, charts and dashboards.

        Args:
            data: Series | Chart | Dashboard | UIElement

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'legendAdd', {'chart': data.id})
        return self

    def set_font_size(self, font_size: int | float):
        """Set the font size of legend entries.

        Args:
            font_size (int | float): Font size of the entries.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setLegendFontSize', {'size': font_size})
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

    def set_stroke(self, thickness: int | float, color: any = None):
        """Set the LegendBox stroke style.

        Args:
            thickness (int | float): Thickness of the stroke.
            color (Color): Color of the stroke.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(
            self.id,
            'setLegendBackgroundStrokeStyle',
            {'thickness': thickness, 'color': color},
        )
        return self

    def set_background_color(self, color: any):
        """Set the background color of the LegendBox.

        Args:
            color (Color): Color of the background.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setLegendBackgroundFillStyle', {'color': color})
        return self
