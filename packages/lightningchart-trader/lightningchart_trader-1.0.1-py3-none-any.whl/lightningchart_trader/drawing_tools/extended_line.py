from lightningchart_trader.drawing_tools import DrawingToolBase


class ExtendedLine(DrawingToolBase):
    def __init__(self, trader, startX, startY, endX=None, endY=None):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addExtendedLine',
            {
                'traderID': trader.id,
                'startX': startX,
                'startY': startY,
                'endX': endX,
                'endY': endY,
            },
        )

    def set_extend_lines(self, extendLeft: bool, extendRight: bool):
        """Sets whether the top and bottom lines should be extended to the left and right edges of the chart.

        Args:
            extendLeft (bool): Set true to extend the lines to the left edge.
            extendRight (bool): Set true to extend the lines to the right edge.
        """
        self.instance.send(
            self.id,
            'setExtendLinesLeftRight',
            {'extendLeft': extendLeft, 'extendRight': extendRight},
        )
        return self

    def set_line_color(self, color: str):
        """Sets the color of the Trend Line.

        Args:
            color (str): New line color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setLineColor', {'color': color})
        return self

    def set_line_width(self, width: int | float):
        """Sets the width of the Trend Line.

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
        endX: int | float,
        endY: int | float,
    ):
        """Updates the drawing tool based on the control points' locations.

        Args:
            startX (int | float): Starting point X location.
            startY (int | float): Starting point Y location.
            endX (int | float): End point X location.
            endY (int | float): End point Y location.
        """
        self.instance.send(
            self.id,
            'updateExtendedLinePosition',
            {'startX': startX, 'startY': startY, 'endX': endX, 'endY': endY},
        )
        return self
