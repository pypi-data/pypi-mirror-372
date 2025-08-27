from lightningchart_trader.drawing_tools import DrawingToolBase


class DateRange(DrawingToolBase):
    def __init__(self, trader, startX, startY, endX=None, endY=None):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addDateRange',
            {
                'traderID': trader.id,
                'startX': startX,
                'startY': startY,
                'endX': endX,
                'endY': endY,
            },
        )

    def set_area_color(self, color: str):
        """Sets the area color of the Date Range.

        Args:
            color (str): New area color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setAreaColor', {'color': color})
        return self

    def set_fill_enabled(self, fill_enabled: bool):
        """Sets whether the measurement area is colored or not.

        Args:
            fill_enabled (bool): Set true to enable colored fill.
        """
        self.instance.send(self.id, 'setFillEnabled', {'fillEnabled': fill_enabled})
        return self

    def set_line_color(self, color: str):
        """Sets the line color.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the lines.

        Args:
            width (int | float): New line width.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def update_position(
        self,
        point1X: int | float,
        point1Y: int | float,
        point2X: int | float,
        point2Y: int | float,
    ):
        """Updates the drawing tool based on the control points' locations.

        Args:
            point1X (int | float): First point X-location.
            point1Y (int | float): First point Y-location.
            point2X (int | float): Second point X-location.
            point2Y (int | float): Second point Y-location.
        """
        self.instance.send(
            self.id,
            'updateDateRangePosition',
            {
                'point1X': point1X,
                'point1Y': point1Y,
                'point2X': point2X,
                'point2Y': point2Y,
            },
        )
        return self
