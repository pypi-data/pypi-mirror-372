import uuid


class Heatmap:
    def __init__(self, trader, start_x, start_y, end_x, end_y, data_values):
        self.id = str(uuid.uuid4()).split('-')[0]
        self.instance = trader.instance

        self.instance.send(
            self.id,
            'addHeatmap',
            {
                'traderID': trader.id,
                'startX': start_x,
                'startY': start_y,
                'endX': end_x,
                'endY': end_y,
                'dataValues': data_values,
            },
        )

    def dispose(self):
        """Disposes the heatmap."""
        self.instance.send(self.id, 'dispose', {})
        return self

    def get_name(self):
        """Gets the name of the heatmap. Returns None if no name is set."""
        return self.name if self.name else None

    def set_data(self, data):
        """Sets new data values to the heatmap.

        Args:
            data (list of lists of numbers): A 2D array of new data values to update the heatmap.
        """
        self.instance.send(self.id, 'setData', {'data': data})
        return self

    def set_palette(self, palette_steps):
        """Assigns a new set of steps for the palette used by the heatmap.

        Args:
            palette_steps (list of dicts): A list of steps where each step has a 'value' and a 'color'.
            Example: [{'value': 0, 'color': '#0032FF1E'}, {'value': 50, 'color': '#00FF321E'}, {'value': 100, 'color': '#FFFF321E'}]
        """
        self.instance.send(self.id, 'setPalette', {'paletteSteps': palette_steps})
        return self

    def set_name(self, name: str):
        """Sets the name of the heatmap.

        Args:
            ame (str): The name to assign to the heatmap.
        """
        self.name = name
        self.instance.send(self.id, 'setName', {'name': name})
        return self

    def set_size(
        self,
        start_x: int | float,
        start_y: int | float,
        end_x: int | float,
        end_y: int | float,
    ):
        """Sets the size of the heatmap using axis values.

        Args:
            start_x (int | float): The starting X-coordinate.
            start_y (int | float): The starting Y-coordinate.
            end_x (int | float): The ending X-coordinate.
            end_y (int | float): The ending Y-coordinate.
        """
        self.instance.send(
            self.id,
            'setSize',
            {'startX': start_x, 'startY': start_y, 'endX': end_x, 'endY': end_y},
        )
        return self

    def show_in_result_table(self, show_in_table: bool):
        """Controls whether the heatmap is visible in the result table.

        Args:
            show_in_table (bool): Set to True to show the heatmap in the result table, False otherwise.
        """
        self.instance.send(self.id, 'showInResultTable', {'showInTable': show_in_table})
        return self

    def set_interpolate(self, setInterpolate: bool):
        """Enables or disables the interpolation of the heatmap.

        Args:
            set_interpolate (bool): Set to True to enable interpolation, False to disable it.
        """
        self.instance.send(self.id, 'setInterpolate', {'setInterpolate': setInterpolate})
        return self
