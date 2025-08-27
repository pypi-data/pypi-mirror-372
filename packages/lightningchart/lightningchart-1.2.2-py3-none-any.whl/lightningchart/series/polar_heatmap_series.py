from __future__ import annotations

from lightningchart.charts import Chart
from lightningchart.series import (
    ComponentWithPaletteColoring,
    SeriesWithIntensityInterpolation,
    Series,
)
from lightningchart.utils import convert_to_matrix


class PolarHeatmapSeries(
    ComponentWithPaletteColoring,
    SeriesWithIntensityInterpolation,
):
    """Series for visualizing a Polar Heatmap with a static sector and annuli count."""

    def __init__(
        self,
        chart: Chart,
        sectors: int,
        annuli: int,
        data_order: str,
        amplitude_start: int | float = 0,
        amplitude_end: int | float = 1,
        amplitude_step: int | float = 0,
    ):
        Series.__init__(self, chart)
        self.instance.send(
            self.id,
            'addHeatmapSeries',
            {
                'chart': self.chart.id,
                'sectors': sectors,
                'annuli': annuli,
                'dataOrder': data_order,
                'amplitudeStart': amplitude_start,
                'amplitudeEnd': amplitude_end,
                'amplitudeStep': amplitude_step,
            },
        )

    def invalidate_intensity_values(
        self,
        values: list[list[int | float]],
        i_annulus: int = None,
        i_sector: int = None,
    ):
        """Invalidate range of heatmap intensity values starting from first sector and annulus.

        Args:
            values: Intensity value matrix.
            i_annulus: First affected annulus.
            i_sector: First affected sector.

        Returns:
            The instance of the class for fluent interface.
        """
        values = convert_to_matrix(values)

        self.instance.send(
            self.id,
            'invalidateIntensityValuesPolar',
            {'iAnnulus': i_annulus, 'iSector': i_sector, 'values': values},
        )
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

    def set_auto_scrolling_enabled(self, enabled: bool = True):
        """Set whether series is taken into account with automatic scrolling and fitting of attached axes.

        Args:
            enabled: Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAutoScrollingEnabled', {'enabled': enabled})
        return self

    def set_highlight_on_hover(self, enabled: bool):
        """Set highlight on mouse hover enabled or disabled.

        Args:
            enabled: Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setHighlightOnHover', {'enabled': enabled})
        return self
