from lightningchart_trader.drawing_tools import DrawingToolBase


class CrossLine(DrawingToolBase):
    def __init__(self, trader, x_position, y_position):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addCrossLine',
            {
                'traderID': trader.id,
                'xPosition': x_position,
                'yPosition': y_position,
            },
        )

    def set_line_color(self, color: str):
        """Sets the color of the Cross Line.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the Cross Line.

        Args:
            width (int | float): New line width.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_magnetic(self, is_magnetic: bool):
        """Sets whether the drawing tool should automatically snap to OLHC-data points.

        Args:
            is_magnetic (bool): Set true to enable snapping to data points.
        """
        self.instance.send(self.id, 'setMagnetic', {'isMagnetic': is_magnetic})
        return self

    def update_position(self, x_value: int | float, y_value: int | float):
        """Updates the drawing tool location.

        Args:
            x_value (int | float): X-value for the cross point.
            y_value (int | float): Y-value (price) for the cross point.
        """
        self.instance.send(
            self.id,
            'updateCrossLinePosition',
            {'xPosition': x_value, 'yPosition': y_value},
        )
        return self
