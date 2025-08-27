from __future__ import annotations
from lightningchart.charts import Chart
from lightningchart.instance import Instance
from lightningchart.series import Series
from lightningchart.ui import UserInteractions


class ZoomBandChart(Chart, UserInteractions):
    """Chart that is attached to a single Axis of a ChartXY."""

    def __init__(
        self,
        instance: Instance,
        chart_id: str,
        dashboard_id: str,
        column_index: int,
        column_span: int,
        row_index: int,
        row_span: int,
        axis_type: str,
        orientation: str,
        use_shared_value_axis,
        html_text_rendering: bool = False,
    ):
        Chart.__init__(self, instance)
        self.instance.send(
            self.id,
            'zoomBandChart',
            {
                'db': dashboard_id,
                'chart': chart_id,
                'column_index': column_index,
                'column_span': column_span,
                'row_index': row_index,
                'row_span': row_span,
                'axisType': axis_type,
                'orientation': orientation,
                'useSharedValueAxis': use_shared_value_axis,
                'htmlTextRendering': html_text_rendering,
            },
        )

    def add_series(self, series: Series):
        """Add a series to the ZoomBandChart.

        Args:
            series (Series): Series to attach.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'zbcAdd', {'series': series.id})
        return self

    def set_title(self, title: str):
        """Set text of Chart title.

        Args:
            title (str): Chart title as a string.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setTitle', {'title': title})
        return self

    def dispose(self):
        """Permanently destroy the component.

        Returns:
            True
        """
        self.instance.send(self.id, 'dispose')
        return True

    def set_user_interactions(self, interactions=...):
        """Configure user interactions from a set of preset options.

        Args:
            interactions (dict or None):
                - `None`: disable all interactions
                - `{}` or no argument: restore default interactions
                - `dict`: configure specific interactions

        Examples:
            ## Disable all interactions:
            zbc.set_user_interactions(None)

            ## Restore default interactions:
            zbc.set_user_interactions()
            zbc.set_user_interactions({})

            ## Configure specific interactions:
            zbc.set_user_interactions(
                {
                    'pan': {'drag': False, 'click': True},
                    'zoom': {'wheel': 'undefined', 'dragKnob': False},
                }
            )
        """
        return super().set_user_interactions(interactions)

    def set_stop_axis_on_interaction(self, state: bool = False):
        """Set whether to stop axis on interaction.

        Args:
            state (bool): Whether to stop axis on interaction.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setStopAxisOnInteraction', {'state': state})
        return self
