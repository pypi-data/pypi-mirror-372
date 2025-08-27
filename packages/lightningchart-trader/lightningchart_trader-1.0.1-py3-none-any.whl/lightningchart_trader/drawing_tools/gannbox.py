from lightningchart_trader.drawing_tools import DrawingToolBase


class GannBox(DrawingToolBase):
    def __init__(
        self,
        trader,
        startX: int | float,
        startY: int | float,
        endX: int | float,
        endY: int | float,
        lineColor: str,
        lineWidth: int | float,
        areaColor: str,
    ):
        """Initializes a Gann Box drawing tool.

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
            'addGannBox',
            {
                'traderID': trader.id,
                'startX': startX,
                'startY': startY,
                'endX': endX,
                'endY': endY,
                'lineColor': lineColor,
                'lineWidth': lineWidth,
                'areaColor': areaColor,
            },
        )

    def set_area_color(self, color: str):
        """Sets the area color of the Date Range.

        Args:
            color (str): New area color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setAreaColor', {'color': color})
        return self

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

    def show_angles(self, show_angles: bool):
        """Sets whether diagonal angle lines are shown inside the Gann Box.

        Args:
            show_angles (bool): Set true to show diagonal lines.
        """
        self.instance.send(self.id, 'showAngles', {'showAngles': show_angles})
        return self

    def update_position(
        self,
        topLeftX: int | float,
        topLeftY: int | float,
        topRightX: int | float,
        topRightY: int | float,
        bottomLeftX: int | float,
        bottomLeftY: int | float,
        bottomRightX: int | float,
        bottomRightY: int | float,
    ):
        """Updates the Gann Box based on control points' locations.

        Args:
            topLeftX (int | float): Top left X-location.
            topLeftY (int | float): Top left Y-location.
            topRightX (int | float): Top right X-location.
            topRightY (int | float): Top right Y-location.
            bottomLeftX (int | float): Bottom left X-location.
            bottomLeftY (int | float): Bottom left Y-location.
            bottomRightX (int | float): Bottom right X-location.
            bottomRightY (int | float): Bottom right Y-location.
        """
        self.instance.send(
            self.id,
            'updateGannBoxPosition',
            {
                'topLeftX': topLeftX,
                'topLeftY': topLeftY,
                'topRightX': topRightX,
                'topRightY': topRightY,
                'bottomLeftX': bottomLeftX,
                'bottomLeftY': bottomLeftY,
                'bottomRightX': bottomRightX,
                'bottomRightY': bottomRightY,
            },
        )
        return self

    def dispose(self):
        """Disposes the Gann Box tool."""
        self.instance.send(self.id, 'dispose')
        return self
