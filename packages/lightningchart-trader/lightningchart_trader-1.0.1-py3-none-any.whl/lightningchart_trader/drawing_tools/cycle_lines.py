from lightningchart_trader.drawing_tools import DrawingToolBase


class CycleLines(DrawingToolBase):
    def __init__(self, trader, startX, startY, endX=None, endY=None):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addCycleLines',
            {
                'traderID': trader.id,
                'startX': startX,
                'startY': startY,
                'endX': endX,
                'endY': endY,
            },
        )

    def set_time_zone_count(self, timeZoneCount: int):
        """Sets the number of time zones.

        Args:
            timeZoneCount (int): New time zone count.
        """
        self.instance.send(self.id, 'setTimeZoneCount', {'timeZoneCount': timeZoneCount})
        return self

    def set_line_color(self, color: str):
        """Sets the color of the Cycle Lines.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the Cycle Lines.

        Args:
            width (int | float): New line width.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_fill_enabled(self, fillEnabled: bool):
        """Sets whether the area between the cycle lines is filled.

        Args:
            fillEnabled (bool): Set true to enable fill.
        """
        self.instance.send(self.id, 'setFillEnabled', {'fillEnabled': fillEnabled})
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
            'updatePositionCycleLines',
            {'startX': startX, 'startY': startY, 'endX': endX, 'endY': endY},
        )
        return self
