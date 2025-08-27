from lightningchart_trader.drawing_tools import DrawingToolBase


class SineWave(DrawingToolBase):
    def __init__(self, trader, startX, startY, endX=None, endY=None):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addSineWave',
            {
                'traderID': trader.id,
                'startX': startX,
                'startY': startY,
                'endX': endX,
                'endY': endY,
            },
        )

    def update_position(
        self,
        startX: int | float,
        startY: int | float,
        endX: int | float,
        endY: int | float,
    ):
        """Updates the drawing tool based on the control points' locations.

        Args:
            startX (int | float): Start point X-location.
            startY (int | float): Start point Y-location.
            endX (int | float): End point X-location.
            endY (int | float): End point Y-location.
        """
        self.instance.send(
            self.id,
            'updatePositionSineWave',
            {'startX': startX, 'startY': startY, 'endX': endX, 'endY': endY},
        )
        return self

    def set_magnetic(self, is_magnetic: bool):
        """Sets whether the drawing tool should automatically snap to OHLC data points.

        Args:
            is_magnetic (bool): Set true to enable snapping to data points.
        """
        self.instance.send(self.id, 'setMagnetic', {'isMagnetic': is_magnetic})
        return self

    def set_smoothness(self, smoothness: int | float):
        """Sets the smoothness of the Sine Wave.

        Args:
            smoothness (int | float): The smoothness value for the wave.
        """
        self.instance.send(self.id, 'setSmoothness', {'smoothness': smoothness})
        return self

    def set_line_color(self, color: str):
        """Sets the color of the Sine Wave.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the Sine Wave.

        Args:
            width (int | float): New line width.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self
