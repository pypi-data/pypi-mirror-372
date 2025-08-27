from lightningchart_trader.drawing_tools import DrawingToolBase


class PriceRange(DrawingToolBase):
    def __init__(
        self,
        trader,
        startX,
        startY,
        endX=None,
        endY=None,
        lineColor='#000000',
        lineWidth=1,
        areaColor='#FFFFFF',
    ):
        super().__init__(trader)
        self.instance.send(
            self.id,
            'addPriceRange',
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
        """Sets the area color of the Price Range.

        Args:
            color (str): New area color as string, should be in HEX format e.g. #FFFFFF.
        """
        self.instance.send(self.id, 'setAreaColor', {'color': color})
        return self

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

    def set_fill_enabled(self, fillEnabled: bool):
        """Sets whether the measurement area is colored or not.

        Args:
            fillEnabled (bool): Set true to enable colored fill.
        """
        self.instance.send(self.id, 'setFillEnabled', {'fillEnabled': fillEnabled})
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

    def set_magnetic(self, is_magnetic: bool):
        """Sets whether the drawing tool should automatically snap to OHLC data points.

        Args:
            is_magnetic (bool): Set true to enable snapping to data points.
        """
        self.instance.send(self.id, 'setMagnetic', {'isMagnetic': is_magnetic})
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
            'updatePriceRangePosition',
            {
                'point1X': point1X,
                'point1Y': point1Y,
                'point2X': point2X,
                'point2Y': point2Y,
            },
        )
        return self
