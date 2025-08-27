from __future__ import annotations

from lightningchart import conf, Themes
from lightningchart.charts import GeneralMethods, TitleMethods, Chart
from lightningchart.instance import Instance
from lightningchart.series import ComponentWithPaletteColoring
from lightningchart.utils import convert_to_dict, convert_color_to_hex


class MapChart(GeneralMethods, TitleMethods, ComponentWithPaletteColoring):
    def __init__(
        self,
        map_type: str = 'World',
        theme: Themes = Themes.Light,
        theme_scale: float = 1.0,
        title: str = None,
        license: str = None,
        license_information: str = None,
        html_text_rendering: bool = False,
    ):
        """Chart class for visualizing a Map of a selected part of the world. Defaults to the entire world.

        Args:
            map_type (str): "Africa" | "Asia" | "Australia" | "Canada" | "Europe" | "NorthAmerica" | "SouthAmerica" | "USA" | "World" |
                "NorthAmerica" | "SouthAmerica" | "USA" | "World"
            theme (Themes): Overall theme of the chart.
            title (str): Title of the chart.
            license (str): License key.
            theme_scale: To up or downscale font sizes as well as tick lengths, element paddings, etc. to make font sizes sit in nicely.
            html_text_rendering: Can be enabled for sharper text display where required with drawback of weaker performance.
        """
        map_types = (
            'Africa',
            'Asia',
            'Australia',
            'Canada',
            'Europe',
            'NorthAmerica',
            'SouthAmerica',
            'USA',
            'World',
        )
        if map_type not in map_types:
            raise ValueError(f"Expected map_type to be one of {map_types}, but got '{map_type}'.")

        instance = Instance()
        Chart.__init__(self, instance)
        self.instance.send(
            self.id,
            'mapChart',
            {
                'mapType': map_type,
                'theme': theme.value,
                'scaleTheme': theme_scale,
                'license': license or conf.LICENSE_KEY,
                'licenseInformation': license_information or conf.LICENSE_INFORMATION,
                'htmlTextRendering': html_text_rendering,
            },
        )
        if title:
            self.set_title(title)

    def invalidate_region_values(self, region_values: list[dict]):
        """Invalidate numeric values associated with each region of the Map.

        Args:
            region_values (list[dict]): List of {"ISO_A3": string, "value": number} dictionaries.

        Returns:
            The instance of the class for fluent interface.
        """
        region_values = convert_to_dict(region_values)

        self.instance.send(self.id, 'invalidateRegionValues', {'values': region_values})
        return self

    def set_highlight_on_hover(self, enabled: bool):
        """Set highlight on mouse hover enabled or disabled.

        Args:
            enabled (bool): Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setHighlightOnHover', {'enabled': enabled})
        return self

    def set_outlier_region_color(self, color: any):
        """Set color of outlier regions (parts of map that are visible, but not interactable with active map type).

        Args:
            color (Color): Color of outlier regions.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setOutlierRegionFillStyle', {'color': color})
        return self

    def set_outlier_region_stroke(self, thickness: int | float, color: any = None):
        """Set stroke of outlier regions (parts of map that are visible, but not interactable with active map type).

        Args:
            thickness (int | float): Thickness of the stroke.
            color (Color): Color of the stroke.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(
            self.id,
            'setOutlierRegionStrokeStyle',
            {'thickness': thickness, 'color': color},
        )
        return self

    def set_separate_region_color(self, color: any):
        """Set color of separate regions, which are visual components surrounding areas such as Alaska and Hawaii.

        Args:
            color (Color): Color of separate regions.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setSeparateRegionFillStyle', {'color': color})
        return self

    def set_separate_region_stroke(self, thickness: int | float, color: any = None):
        """Set stroke of Separate regions, which are visual components surrounding areas such as Alaska and Hawaii.

        Args:
            thickness (int | float): Thickness of the stroke.
            color (Color): Color of the stroke.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(
            self.id,
            'setSeparateRegionStrokeStyle',
            {'thickness': thickness, 'color': color},
        )
        return self

    def set_stroke(self, thickness: int | float, color: any = None):
        """Set Stroke style of Map regions.

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


class MapChartDashboard(MapChart):
    def __init__(
        self,
        instance: Instance,
        dashboard_id: str,
        column: int,
        row: int,
        colspan: int,
        rowspan: int,
        map_type: str= 'World',
    ):
        Chart.__init__(self, instance)
        self.instance.send(
            self.id,
            'createMapChart',
            {
                'db': dashboard_id,
                'column': column,
                'row': row,
                'colspan': colspan,
                'rowspan': rowspan,
                'type': map_type
            },
        )
