from __future__ import annotations

from lightningchart.ui.polar_axis import PolarAxis


class PolarAxisAmplitude(PolarAxis):
    def __init__(self, chart):
        super().__init__(chart)
        self.instance.send(self.id, 'getAmplitudeAxis', {'chart': self.chart.id})

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
