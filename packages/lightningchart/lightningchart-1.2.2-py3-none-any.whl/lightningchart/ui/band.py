from __future__ import annotations

from lightningchart.ui import UIElement, UIEWithHighlight, UserInteractions
from lightningchart.utils import convert_color_to_hex


class Band(UIEWithHighlight, UserInteractions):
    def __init__(self, chart, axis, on_top: bool):
        UIElement.__init__(self, chart)
        self.instance.send(self.id, 'addBand', {'axis': axis.id, 'onTop': on_top})

    def set_value_start(self, value_start: int | float):
        """Set start value of Band. This is in values of its owning Axis.

        Args:
            value_start (int | float): Value on Axis.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setValueStart', {'valueStart': value_start})
        return self

    def set_value_end(self, value_end: int | float):
        """Set end value of Band. This is in values of its owning Axis.

        Args:
            value_end (int | float): Value on Axis.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setValueEnd', {'valueEnd': value_end})
        return self

    def set_color(self, color: any):
        """Set a color of the band.

        Args:
            color (Color): Color of the band.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setSolidFillStyle', {'color': color})
        return self

    def set_stroke(self, thickness: int | float, color: any = None):
        """Set stroke style of Band.

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

    def set_name(self, name: str):
        """Sets the name of the Component updating attached LegendBox entries.

        Args:
            name (str): Name of the component.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setName', {'name': name})
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
            band.set_user_interactions(None)

            ## Restore default interactions:
            band.set_user_interactions()
            band.set_user_interactions({})

            ## Scale interaction only:
            band.set_user_interactions({'scale': False})
        """
        return super().set_user_interactions(interactions)
