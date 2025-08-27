from __future__ import annotations

from lightningchart.ui.axis import GenericAxis
from lightningchart.utils import convert_color_to_hex


class PolarAxis(GenericAxis):
    def __init__(self, chart):
        GenericAxis.__init__(self, chart)

    def set_stroke(self, thickness: int | float, color: any = None):
        """Set Stroke style of the axis.

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
