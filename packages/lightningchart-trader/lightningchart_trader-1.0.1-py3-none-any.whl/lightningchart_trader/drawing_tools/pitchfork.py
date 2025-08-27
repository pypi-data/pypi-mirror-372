from lightningchart_trader.drawing_tools import DrawingToolBase


class Pitchfork(DrawingToolBase):
    def __init__(
        self,
        trader,
        startX,
        startY,
        endX1=None,
        endY1=None,
        endX2=None,
        endY2=None,
        lineColor='#000000',
        lineWidth=1,
        areaColor='#FFFFFF',
    ):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addPitchfork',
            {
                'traderID': trader.id,
                'startX': startX,
                'startY': startY,
                'endX1': endX1,
                'endY1': endY1,
                'endX2': endX2,
                'endY2': endY2,
                'lineColor': lineColor,
                'lineWidth': lineWidth,
                'areaColor': areaColor,
            },
        )

    def set_area_color(self, color: str):
        """Sets the area color of the Pitchfork.

        Args:
            color (str): New area color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setAreaColor', {'color': color})
        return self

    def set_line_color(self, color: str):
        """Sets the line color of the Pitchfork lines.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the Pitchfork lines.

        Args:
            width (int | float): New line width.
        """
        self.instance.send(self.id, 'setLineWidth', {'width': width})
        return self

    def set_magnetic(self, is_magnetic: bool):
        """Sets whether the drawing tool should automatically snap to OHLC data points.

        Args:
            is_magnetic (bool): Set true to enable snapping to data points.
        """
        self.instance.send(self.id, 'setMagnetic', {'isMagnetic': is_magnetic})
        return self

    def update_position(
        self,
        startX: int | float,
        startY: int | float,
        endX1: int | float,
        endY1: int | float,
        endX2: int | float,
        endY2: int | float,
    ):
        """Updates the drawing tool based on the control points' locations.

        Args:
            startX (int | float): Starting point X-location.
            startY (int | float): Starting point Y-location.
            endX1 (int | float): First end point X-location.
            endY1 (int | float): First end point Y-location.
            endX2 (int | float): Second end point X-location.
            endY2 (int | float): Second end point Y-location.
        """
        self.instance.send(
            self.id,
            'updatePitchforkPosition',
            {
                'startX': startX,
                'startY': startY,
                'endX1': endX1,
                'endY1': endY1,
                'endX2': endX2,
                'endY2': endY2,
            },
        )
        return self
