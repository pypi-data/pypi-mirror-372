from __future__ import annotations

import uuid
from lightningchart.series import (
    ComponentWithPaletteColoring,
    SeriesWithoutCursorEnabel,
)
from lightningchart.utils import convert_color_to_hex


class PolarSector(ComponentWithPaletteColoring, SeriesWithoutCursorEnabel):
    """Class representing a sector in a polar chart."""

    def __init__(self, chart):
        self.id = str(uuid.uuid4()).split('-')[0]
        self.instance = chart.instance
        self.chart = chart
        self.instance.send(self.id, 'addSector', {'chart': self.chart.id})

    def set_amplitude_start(self, amplitude_start: int | float | None):
        """Set Sectors start amplitude.

        Args:
            amplitude_start: Start amplitude. Setting to None results in tracking the PolarAxes start value.
                This doesn't have to be less than amplitude end value.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAmplitudeStart', {'amplitudeStart': amplitude_start})
        return self

    def set_amplitude_end(self, amplitude_end: int | float | None):
        """Set Sectors end amplitude.

        Args:
            amplitude_end: End amplitude. Setting to None results in tracking the PolarAxes end value.
                This doesn't have to be greater than amplitude start value.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAmplitudeEnd', {'amplitudeEnd': amplitude_end})
        return self

    def set_angle_start(self, angle_start: int):
        """Set Sectors start angle in degrees.

        Args:
            angle_start: Start angle in degrees, restricted to [0, 360].
                This doesn't have to be less than angle end value.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAngleStart', {'angleStart': angle_start})
        return self

    def set_angle_end(self, angle_end: int | float):
        """Set Sectors end angle in degrees.

        Args:
            angle_end: End angle in degrees, restricted to [0, 360].
                This doesn't have to be greater than angle start value.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAngleEnd', {'angleEnd': angle_end})
        return self

    def set_stroke(self, thickness: int | float, color: any = None):
        """Set Stroke style of the sector.

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
