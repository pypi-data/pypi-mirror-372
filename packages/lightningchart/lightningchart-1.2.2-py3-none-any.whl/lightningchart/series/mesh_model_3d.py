from lightningchart.charts import Chart
from lightningchart.series import ComponentWithPaletteColoring, SeriesWith3DShading
from lightningchart.utils import convert_to_list


class MeshModel3D(ComponentWithPaletteColoring, SeriesWith3DShading):
    def __init__(self, chart: Chart):
        super().__init__(chart)
        self.instance.send(self.id, 'addMeshModel', {'chart': chart.id})

    def set_model_geometry(self, vertices: list[float], indices: list[int], normals: list[float] = None):
        """Method for loading triangulated 3D model geometry data. Please note that
        LightningChart Python does not include any routines for parsing 3D model files.
        To display your 3D models with LightningChart, you have to export it to a
        triangulated file format (such as .OBJ), parse the data and supply list of vertices,
        indices and optionally normals to LightningChart Python.

        Args:
            vertices: 3D model vertices
            indices: 3D model indices
            normals: 3D model normals

        Returns:
            The instance of the class for fluent interface.
        """
        vertices = convert_to_list(vertices)
        indices = convert_to_list(indices)
        normals = convert_to_list(normals)

        self.instance.send(
            self.id,
            'setModelGeometry',
            {'vertices': vertices, 'indices': indices, 'normals': normals},
        )
        return self

    def set_scale(self, scale: float | dict):
        """Set scale of the model.

        Args:
            scale: Number for symmetric scale multiplier or dict with separate scale multipliers for x, y, z.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setScale', {'scale': scale})
        return self

    def set_model_location(self, x: int | float, y: int | float, z: int | float):
        """Set location of the model.

        Args:
            x: x-axis location.
            y: y-axis location.
            z: z-axis location.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setModelLocation', {'x': x, 'y': y, 'z': z})
        return self

    def set_model_rotation(self, x: int | float, y: int | float, z: int | float):
        """Set rotation of the model.

        Args:
            x: x-axis rotation.
            y: y-axis rotation.
            z: z-axis rotation.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setModelRotation', {'x': x, 'y': y, 'z': z})
        return self

    def set_vertex_values(self, callback):
        """Assign number values to each vertex of the model.

        Args:
            callback: Callback function that supplies the user with array of vertex locations
                in World coordinate system and expects a number array with same length to be returned.

        Returns:
            The instance of the class for fluent interface.
        """
        vertex_values = callback()
        self.instance.send(self.id, 'setVertexValues', {'values': vertex_values})
        return self

    def set_model_alignment(self, x: int | float, y: int | float, z: int | float):
        """Set alignment of the model. Describes which "corner" of the model is positioned at model location.

        Args:
            x: x-axis alignment.
            y: y-axis alignment.
            z: z-axis alignment.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setModelAlignment', {'x': x, 'y': y, 'z': z})
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

    def set_effect(self, enabled: bool):
        """Set theme effect enabled on component or disabled.

        Args:
            enabled: Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setEffect', {'enabled': enabled})
        return self

    def set_animation_highlight(self, enabled: bool):
        """Set state of component highlighting.

        Args:
            enabled: Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAnimationHighlight', {'enabled': enabled})
        return self
