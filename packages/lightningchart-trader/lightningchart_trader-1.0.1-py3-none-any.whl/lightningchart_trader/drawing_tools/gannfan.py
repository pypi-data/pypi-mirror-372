from lightningchart_trader.drawing_tools import DrawingToolBase


class GannFan(DrawingToolBase):
    def __init__(
        self,
        trader,
        startX: int | float,
        startY: int | float,
        endX: int | float,
        endY: int | float,
        lineColor: str,
        lineWidth: int | float,
    ):
        """Initializes a Gann Fun drawing tool.

        Args:
            trader: The trading chart instance.
            startX (int | float): X-coordinate of the starting point.
            startY (int | float): Y-coordinate of the starting point.
            endX (int | float): X-coordinate of the ending point.
            endY (int | float): Y-coordinate of the ending point.
            lineColor (str): Line color in HEX format, e.g., #FFFFFF.
            lineWidth (int | float): Line width.
            areaColor (str): Area fill color in HEX format, e.g., #FFFFFF.
        """
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addGannFan',
            {
                'traderID': trader.id,
                'startX': startX,
                'startY': startY,
                'endX': endX,
                'endY': endY,
                'lineColor': lineColor,
                'lineWidth': lineWidth,
            },
        )

    def set_line_color(self, color: str):
        """Sets the line color of the Gann Box.

        Args:
            color (str): New line color as string, should be in HEX format e.g., #FFFFFF.
        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the line width of the Gann Box.

        Args:
            width (int | float): New line width.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_magnetic(self, is_magnetic: bool):
        """Sets whether the Gann Box should snap to OHLC data points.

        Args:
            is_magnetic (bool): Set true to enable snapping to data points.
        """
        self.instance.send(self.id, 'setMagnetic', {'isMagnetic': is_magnetic})
        return self

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
            'updateGannFunPosition',
            {'startX': startX, 'startY': startY, 'endX': endX, 'endY': endY},
        )
        return self

    def dispose(self):
        """Disposes the Gann Box tool."""
        self.instance.send(self.id, 'dispose')
        return self

    def set_fill_enabled(self, fillEnabled: bool):
        """Sets whether the area between the cycle lines is filled.

        Args:
            fillEnabled (bool): Set true to enable fill.
        """
        self.instance.send(self.id, 'setFillEnabled', {'fillEnabled': fillEnabled})
        return self
