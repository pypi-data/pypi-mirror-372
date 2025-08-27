from __future__ import annotations

from lightningchart import conf, Themes
from lightningchart.charts import (
    GeneralMethods,
    ChartWithXYZAxis,
    TitleMethods,
    ChartWithSeries,
)
from lightningchart.instance import Instance
from lightningchart.series.point_series_3d import PointSeries3D
from lightningchart.series.line_series_3d import LineSeries3D
from lightningchart.series.point_line_series_3d import PointLineSeries3D
from lightningchart.series.box_series_3d import BoxSeries3D
from lightningchart.series.surface_grid_series import SurfaceGridSeries
from lightningchart.series.surface_scrolling_grid_series import (
    SurfaceScrollingGridSeries,
)
from lightningchart.series.mesh_model_3d import MeshModel3D
from lightningchart.ui import UserInteractions
from lightningchart.utils import convert_color_to_hex


class Chart3D(GeneralMethods, TitleMethods, ChartWithXYZAxis, ChartWithSeries, UserInteractions):
    """Chart for visualizing data in a 3-dimensional scene, with camera and light source(s)."""

    def __init__(
        self,
        theme: Themes = Themes.Light,
        theme_scale: float = 1.0,
        title: str = None,
        license: str = None,
        license_information: str = None,
        html_text_rendering: bool = False,
    ):
        """Create a 3D Chart.

        Args:
            theme (Themes): Theme of the chart.
            title (str): A title for the chart.
            license (str): License key.
            theme_scale: To up or downscale font sizes as well as tick lengths, element paddings, etc. to make font sizes sit in nicely.
            html_text_rendering: Can be enabled for sharper text display where required with drawback of weaker performance.

        Returns:
            Reference to 3D Chart class.
        """

        instance = Instance()
        ChartWithSeries.__init__(self, instance)
        self.instance.send(
            self.id,
            'chart3D',
            {
                'theme': theme.value,
                'scaleTheme': theme_scale,
                'license': license or conf.LICENSE_KEY,
                'licenseInformation': license_information or conf.LICENSE_INFORMATION,
                'htmlTextRendering': html_text_rendering,
            },
        )
        if title:
            self.instance.send(self.id, 'setTitle', {'title': title})
        ChartWithXYZAxis.__init__(self)

    def set_animation_zoom(self, enabled: bool = True):
        """Set Chart3D zoom animation enabled.
        When enabled, zooming with mouse wheel or trackpad will include a short animation. This is enabled by default.

        Args:
            enabled (bool): Boolean.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAnimationZoom', {'enabled': enabled})
        return self

    def set_bounding_box(self, x: int | float = 1.0, y: int | float = 1.0, z: int | float = 1.0):
        """Set the dimensions of the Scenes bounding box. The bounding box is a visual reference that all the data of
        the Chart is depicted inside. The Axes of the 3D chart are always positioned along the sides of the bounding
        box.

        Args:
            x (int | float): Relative ratio of x dimension.
            y (int | float): Relative ratio of y dimension.
            z (int | float): Relative ratio of z dimension.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setBoundingBox', {'x': x, 'y': y, 'z': z})
        return self

    def set_bounding_box_stroke(self, thickness: int | float, color: any = None):
        """Set style of 3D bounding box.

        Args:
            thickness (int | float): Thickness of the bounding box.
            color (Color): Color of the bounding box.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(
            self.id,
            'setBoundingBoxStrokeStyle',
            {'thickness': thickness, 'color': color},
        )
        return self

    def add_point_series(
        self,
        render_2d: bool = False,
        individual_lookup_values_enabled: bool = False,
        individual_point_color_enabled: bool = False,
        individual_point_size_axis_enabled: bool = False,
        individual_point_size_enabled: bool = False,
    ) -> PointSeries3D:
        """Method for adding a new PointSeries3D to the chart. This series type for visualizing a collection of
        { x, y, z } coordinates by different markers.

        Point Series 3D accepts data of form {x,y,z}

        Args:
            render_2d (bool): Defines the rendering type of Point Series. When true, points are rendered by 2D markers.
            individual_lookup_values_enabled (bool): Flag that can be used to enable data points value property on
                top of x, y and z. By default, this is disabled.
            individual_point_color_enabled (bool): Flag that can be used to enable data points color property on top of
                x, y and z. By default, this is disabled.
            individual_point_size_axis_enabled (bool): Flag that can be used to enable data points 'sizeAxisX',
                'sizeAxisY' and 'sizeAxisZ' properties on top of x, y and z. By default, this is disabled.
            individual_point_size_enabled (bool): Flag that can be used to enable data points size property on top of
                x, y and z. By default, this is disabled.

        Returns:
            Reference to Point Series class.
        """
        series = PointSeries3D(
            chart=self,
            render_2d=render_2d,
            individual_lookup_values_enabled=individual_lookup_values_enabled,
            individual_point_color_enabled=individual_point_color_enabled,
            individual_point_size_axis_enabled=individual_point_size_axis_enabled,
            individual_point_size_enabled=individual_point_size_enabled,
        )
        self.series_list.append(series)
        return series

    def add_line_series(
        self,
    ) -> LineSeries3D:
        """Method for adding a new LineSeries3D to the chart. This Series type for visualizing a collection of
        { x, y, z } coordinates by a continuous line stroke.

        Line Series 3D accepts data of form {x,y,z}

        Returns:
            Reference to Line Series class.
        """
        series = LineSeries3D(chart=self)
        self.series_list.append(series)
        return series

    def add_point_line_series(
        self,
        render_2d: bool = False,
        individual_lookup_values_enabled: bool = False,
        individual_point_color_enabled: bool = False,
        individual_point_size_axis_enabled: bool = False,
        individual_point_size_enabled: bool = False,
    ) -> PointLineSeries3D:
        """Method for adding a new PointLineSeries3D to the chart. This Series type for visualizing a collection of
        { x, y, z } coordinates by a continuous line stroke and markers.

        Point Line Series 3D accepts data of form {x,y,z}

        Args:
            render_2d (bool): Defines the rendering type of Point Series. When true, points are rendered by 2D markers.
            individual_lookup_values_enabled (bool): Flag that can be used to enable data points value property on
                top of x, y and z. By default, this is disabled.
            individual_point_color_enabled (bool): Flag that can be used to enable data points color property on top of
                x, y and z. By default, this is disabled.
            individual_point_size_axis_enabled (bool): Flag that can be used to enable data points 'sizeAxisX',
                'sizeAxisY' and 'sizeAxisZ' properties on top of x, y and z. By default, this is disabled.
            individual_point_size_enabled (bool): Flag that can be used to enable data points size property on top of
                x, y and z. By default, this is disabled.

        Returns:
            Reference to Point Line Series class.
        """
        series = PointLineSeries3D(
            chart=self,
            render_2d=render_2d,
            individual_lookup_values_enabled=individual_lookup_values_enabled,
            individual_point_color_enabled=individual_point_color_enabled,
            individual_point_size_axis_enabled=individual_point_size_axis_enabled,
            individual_point_size_enabled=individual_point_size_enabled,
        )
        self.series_list.append(series)
        return series

    def add_box_series(self) -> BoxSeries3D:
        """Create Series for visualization of large sets of individually configurable 3D Boxes.

        Box Series 3D accepts data of form { xCenter, yCenter, zCenter, xSize, ySize, zSize}

        Returns:
            Reference to Box Series class.
        """
        series = BoxSeries3D(chart=self)
        self.series_list.append(series)
        return series

    def add_surface_grid_series(
        self,
        columns: int,
        rows: int,
        data_order: str = 'columns',
    ) -> SurfaceGridSeries:
        """Add a Series for visualizing a Surface Grid with a _static column and grid count.

        Surface Grid Series accepts data in the form of two-dimensional matrix of correct size that includes
        integers or floats.

        Args:
            columns (int): Amount of cells along X axis.
            rows (int): Amount of cells along Y axis.
            data_order (str): "columns" | "rows" - Specify how to interpret surface grid values supplied by user.

        Returns:
            Reference to Surface Grid Series class.
        """
        series = SurfaceGridSeries(chart=self, columns=columns, rows=rows, data_order=data_order)
        self.series_list.append(series)
        return series

    def add_surface_scrolling_grid_series(
        self,
        columns: int,
        rows: int,
        scroll_dimension: str = 'columns',
    ) -> SurfaceScrollingGridSeries:
        """Add a Series for visualizing a Surface Grid with API for pushing data in a scrolling manner
        (append new data on top of existing data).

        Surface Scrolling Grid Series accepts data in the form of two-dimensional matrix of correct size that includes
        integers or floats.

        Args:
            columns (int): Amount of cells along X axis.
            rows (int): Amount of cells along Y axis.
            scroll_dimension (str): "columns" | "rows" - Select scrolling dimension,
                as well as how to interpret grid matrix values supplied by user.

        Returns:
            Reference to Surface Scrolling Grid Series class.
        """
        series = SurfaceScrollingGridSeries(chart=self, columns=columns, rows=rows, scroll_dimension=scroll_dimension)
        self.series_list.append(series)
        return series

    def set_camera_automatic_fitting_enabled(self, enabled: bool):
        """Set automatic camera fitting enabled. This is enabled as the default configuration.
        Note that zooming in or out disables it automatically.

        Args:
            enabled (bool): Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setCameraAutomaticFittingEnabled', {'enabled': enabled})
        return self

    def set_camera_location(self, x: int, y: int, z: int):
        """Set the location of camera in World Space, a coordinate system that is not tied to 3D Axes.
        The camera always faces (0, 0, 0) coordinate.
        The light source is always a set distance behind the camera.

        Args:
            x (int): x-coordinate in the range [1, 5]
            y (int): y-coordinate in the range [1, 5]
            z (int): z-coordinate in the range [1, 5]

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setCameraLocation', {'x': x, 'y': y, 'z': z})
        return self

    def add_mesh_model(self):
        mesh_model = MeshModel3D(self)
        self.series_list.append(mesh_model)
        return mesh_model

    def set_cursor_mode(self, mode: str):
        """Set chart Cursor behavior.

        Args:
            mode (str): "disabled" | "show-all" | "show-all-interpolated" | "show-nearest" |
                "show-nearest-interpolated" | "show-pointed" | "show-pointed-interpolated"

        Returns:
            The instance of the class for fluent interface.
        """
        cursor_modes = (
            'disabled',
            'show-all',
            'show-all-interpolated',
            'show-nearest',
            'show-nearest-interpolated',
            'show-pointed',
            'show-pointed-interpolated',
        )
        if mode not in cursor_modes:
            raise ValueError(f"Expected mode to be one of {cursor_modes}, but got '{mode}'.")

        self.instance.send(self.id, 'setCursorMode', {'mode': mode})
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
            chart.set_user_interactions(None)

            ## Restore default interactions:
            chart.set_user_interactions()
            chart.set_user_interactions({})

            ## Disable zooming:
            chart.set_user_interactions(
                {
                    'zoom': {
                        'wheel': {
                            'camera': False,
                        },
                    },
                }
            )
        """
        return super().set_user_interactions(interactions)


class Chart3DDashboard(Chart3D):
    """Class for Chart3D contained in Dashboard."""

    def __init__(
        self,
        instance: Instance,
        dashboard_id: str,
        column: int,
        row: int,
        colspan: int,
        rowspan: int,
        title: str = None,
    ):
        ChartWithSeries.__init__(self, instance)
        self.instance.send(
            self.id,
            'createChart3D',
            {
                'db': dashboard_id,
                'column': column,
                'row': row,
                'colspan': colspan,
                'rowspan': rowspan,
            },
        )
        if title:
            self.instance.send(self.id, 'setTitle', {'title': title})
        ChartWithXYZAxis.__init__(self)
